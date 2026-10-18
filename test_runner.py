import subprocess
import json
import os

def run_tests(test_file_path: str, regression_only: bool = False, failed_tests: list = None) -> dict:
    report_path = "generated_tests/report.json"
    cmd = ["python", "-m", "pytest", test_file_path,
           "--json-report", f"--json-report-file={report_path}", "-v"]

    if regression_only and failed_tests:
        test_ids = " or ".join(failed_tests)
        cmd += ["-k", test_ids]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

    if os.path.exists(report_path):
        with open(report_path) as f:
            return json.load(f)
    return {}
