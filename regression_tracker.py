import json
import os
from dotenv import load_dotenv

load_dotenv()

LOCAL_TRACKER_FILE = "generated_tests/regression_tracker.json"
GCS_BLOB_NAME = "regression_tracker.json"

# ---------------------------------------------------------------------------
# GCS helpers — only imported/used if GCS is configured
# ---------------------------------------------------------------------------

def _get_gcs_bucket():
    """
    Returns a GCS Bucket object if both GCS_BUCKET_NAME and
    GOOGLE_APPLICATION_CREDENTIALS are set in the environment.
    Returns None if GCS is not configured or the import fails.
    """
    bucket_name = os.getenv("GCS_BUCKET_NAME", "").strip()
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()

    # Treat placeholder values as unconfigured
    if (not bucket_name
            or bucket_name == "your-bucket-name"
            or not creds_path
            or creds_path == "path/to/your-service-account-key.json"):
        return None

    try:
        from google.cloud import storage
        client = storage.Client()
        return client.bucket(bucket_name)
    except Exception as e:
        print(f"[GCS] Could not connect to Google Cloud Storage: {e}")
        print("[GCS] Falling back to local file storage.")
        return None


def _load_from_gcs(bucket) -> dict:
    """Download and parse the tracker JSON from GCS. Returns {} on any error."""
    try:
        blob = bucket.blob(GCS_BLOB_NAME)
        if not blob.exists():
            return {}
        content = blob.download_as_text()
        return json.loads(content)
    except Exception as e:
        print(f"[GCS] Failed to read from bucket: {e}")
        print("[GCS] Falling back to local file storage.")
        return None          # None signals caller to use local fallback


def _save_to_gcs(bucket, data: dict) -> bool:
    """Upload the tracker JSON to GCS. Returns True on success, False on error."""
    try:
        blob = bucket.blob(GCS_BLOB_NAME)
        blob.upload_from_string(
            json.dumps(data, indent=2),
            content_type="application/json"
        )
        print(f"[GCS] Regression tracker saved to gs://{bucket.name}/{GCS_BLOB_NAME}")
        return True
    except Exception as e:
        print(f"[GCS] Failed to write to bucket: {e}")
        print("[GCS] Falling back to local file storage.")
        return False


# ---------------------------------------------------------------------------
# Local file helpers
# ---------------------------------------------------------------------------

def _load_from_local() -> dict:
    """Read tracker JSON from the local file. Returns {} if file doesn't exist."""
    if not os.path.exists(LOCAL_TRACKER_FILE):
        return {}
    with open(LOCAL_TRACKER_FILE) as f:
        return json.load(f)


def _save_to_local(data: dict) -> None:
    """Write tracker JSON to the local file."""
    os.makedirs(os.path.dirname(LOCAL_TRACKER_FILE), exist_ok=True)
    with open(LOCAL_TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Public API — same signatures as before
# ---------------------------------------------------------------------------

def load_failed_tests(function_name: str) -> list:
    """
    Load the list of previously failed test names for a given function.
    Tries GCS first; falls back to local file if GCS is not configured or fails.
    """
    bucket = _get_gcs_bucket()

    if bucket is not None:
        data = _load_from_gcs(bucket)
        if data is not None:                     # None means GCS read failed
            return data.get(function_name, [])
        # GCS read failed — fall through to local

    return _load_from_local().get(function_name, [])


def save_failed_tests(function_name: str, failed: list) -> None:
    """
    Save the list of failed test names for a given function.
    Tries GCS first; falls back to local file if GCS is not configured or fails.
    """
    bucket = _get_gcs_bucket()

    if bucket is not None:
        # Load existing data from GCS (or start fresh), update, and re-upload
        data = _load_from_gcs(bucket)
        if data is None:
            data = _load_from_local()            # GCS read failed — use local data
        data[function_name] = failed
        if _save_to_gcs(bucket, data):
            return                               # GCS write succeeded — done
        # GCS write failed — fall through to local

    # Local fallback
    data = _load_from_local()
    data[function_name] = failed
    _save_to_local(data)
