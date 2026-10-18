# Automated QA Intelligence Tool

An AI-powered test automation tool that automatically generates, executes,
and reports test cases for Python functions using Gemini AI and PyTest.

## Features
- Automatic test case generation using Gemini AI (LLM)
- Covers normal, edge case, negative, and boundary test scenarios
- Automated test execution using PyTest
- Structured defect report with pass/fail results
- Regression testing mode to re-run only previously failed tests
- Regression state stored in **Google Cloud Storage** (with automatic local-file fallback)
- Modular architecture with clean separation of concerns

## Tech Stack
Python, Gemini AI (gemini-3.8-flash), PyTest, google-genai, google-cloud-storage, python-dotenv

## Setup
1. Clone the repo
2. Create virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install: `pip install -r requirements.txt`
4. Create `.env` and add: `GEMINI_API_KEY=your_key_here`
5. Get your free Gemini API key from https://aistudio.google.com/app/apikey

## Google Cloud Storage Setup (Optional)

By default the regression tracker saves failed test names to a local JSON file.
To store them in GCS instead, follow these steps:

### 1. Create a GCS Bucket
- Go to https://console.cloud.google.com/storage
- Click **Create Bucket**, give it a unique name (e.g. `my-qa-tool-tracker`)
- Choose a region and leave all other settings as default

### 2. Create a Service Account
- Go to https://console.cloud.google.com/iam-admin/serviceaccounts
- Click **Create Service Account**, give it a name (e.g. `qa-tool-sa`)
- Grant it the role: **Storage Object Admin**
- Click **Done**, then open the service account → **Keys** tab → **Add Key** → **JSON**
- Download the JSON key file and save it somewhere safe (e.g. `C:/keys/gcs-key.json`)

### 3. Update `.env`
```
GCS_BUCKET_NAME=my-qa-tool-tracker
GOOGLE_APPLICATION_CREDENTIALS=C:/keys/gcs-key.json
```

### How the Fallback Works
- If `GCS_BUCKET_NAME` is blank or still the placeholder value → uses local file
- If GCS credentials are invalid or the bucket is unreachable → automatically falls back to local file and prints a warning
- The local fallback file is `generated_tests/regression_tracker.json`

## Usage

```bash
# Generate and run all tests for the add function
python main.py sample_functions/calculator.py add

# Run only previously failed tests (regression mode)
python main.py sample_functions/calculator.py divide --regression
```

## How It Works
1. Reads the target function's source code
2. Sends it to Gemini AI with a structured prompt
3. Gemini returns test cases in JSON format
4. Tool generates a valid PyTest file from the JSON
5. PyTest executes all tests and captures results
6. A structured defect report is printed (pass/fail counts + failure reasons)
7. Failed test names are saved for regression re-runs

## Project Structure
```
automated-qa-tool/
├── main.py                  # Entry point — CLI runner
├── code_reader.py           # Reads function source code from file
├── prompt_builder.py        # Builds structured prompt for Gemini
├── llm_client.py            # Sends prompt to Gemini API
├── test_generator.py        # Converts JSON test cases into PyTest code
├── test_runner.py           # Executes PyTest and captures results
├── report_generator.py      # Generates structured defect report
├── regression_tracker.py    # Tracks previously failed tests (GCS or local)
├── requirements.txt         # All dependencies
└── sample_functions/
    └── calculator.py        # Sample functions to test the tool on
```

## Author
Kshitiz Aggarwal — github.com/kshitiz16032
