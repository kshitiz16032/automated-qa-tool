# PROJECT SUMMARY
## Automated QA Intelligence Tool

---

## 1. What This Project Does (Plain English)

Imagine you write a Python function — let's say a function that adds two numbers. Normally, to make sure it works correctly, you would have to manually write a bunch of test cases yourself: "What if I pass 2 and 3? What if I pass zero? What if I pass a word instead of a number?" This is called **QA (Quality Assurance) testing**, and it takes a lot of time.

This tool **automates that entire process**.

You simply run one command, tell the tool which function you want to test, and it does everything automatically:

1. It reads your function's source code
2. It sends the code to **Gemini AI** (Google's large language model) and asks it to generate test cases
3. Gemini sends back a list of test cases (normal inputs, edge cases, tricky inputs, boundary values)
4. The tool converts those test cases into an actual test file
5. It runs those tests automatically using **PyTest**
6. It prints a clear report telling you which tests passed and which failed

There is also a **regression mode**: if some tests failed previously, you can re-run only those specific tests after you fix the bug — to confirm the fix worked.

---

## 2. Every File — What It Does and Why It Exists

```
automated-qa-tool/
├── main.py
├── code_reader.py
├── prompt_builder.py
├── llm_client.py
├── test_generator.py
├── test_runner.py
├── report_generator.py
├── regression_tracker.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── PROJECT_SUMMARY.md          <- This file
└── sample_functions/
    └── calculator.py
```

---

### `main.py` — The Entry Point (The Boss)

This is the file you actually run from the command line. Think of it as the **conductor of an orchestra** — it doesn't do any work itself, but it calls all the other modules in the right order and passes data between them.

**What it does:**
- Reads the command-line arguments (which file? which function? regression mode?)
- Calls `code_reader` → `prompt_builder` → `llm_client` → `test_generator` → `test_runner` → `report_generator` → `regression_tracker` in sequence
- Ties the entire pipeline together

---

### `code_reader.py` — The Source Code Reader

Before you can generate test cases, the AI needs to actually *see* the function's source code. This file handles that job.

**What it does:**
- Takes a file path (e.g. `sample_functions/calculator.py`) and a function name (e.g. `add`)
- Uses Python's built-in `importlib` to load the file as a Python module
- Uses Python's built-in `inspect` to extract the exact source code of that function
- Returns the source code as a plain string

**Why it's needed:** Gemini AI cannot see your files directly. We have to read the function ourselves and pass the text to the AI.

---

### `prompt_builder.py` — The AI Instruction Writer

This file constructs the exact message (called a "prompt") that gets sent to Gemini AI.

**What it does:**
- Takes the function source code and function name as input
- Builds a detailed, structured text prompt that tells Gemini exactly what to do:
  - What kind of test cases to generate (normal, edge, negative, boundary)
  - That it must return **only** a raw JSON array — no extra text, no markdown
  - Exactly what format the JSON should follow

**Why it's needed:** AI models need very precise, clear instructions. A vague prompt gives vague results. This file ensures Gemini always returns clean, parseable JSON.

---

### `llm_client.py` — The Gemini AI Connector

This file handles all communication with the Gemini AI API.

**What it does:**
- Loads the API key securely from the `.env` file
- Creates a Gemini AI client using the `google-genai` SDK
- Sends the prompt to the `gemini-3.8-flash` model
- Returns the raw text response from Gemini
- Handles errors gracefully (prints a clear message if the API call fails)

**Why it's needed:** This is the bridge between your local machine and Google's AI servers. Without this, the tool has no intelligence — it wouldn't know what test cases to generate.

---

### `test_generator.py` — The PyTest File Writer

Gemini returns test cases as JSON text. That's not something PyTest can run directly. This file converts the JSON into actual executable Python test code.

**What it does:**
- Parses the raw JSON response from Gemini (robustly — even if Gemini wraps it in markdown or extra text)
- Creates a `generated_tests/` folder if it doesn't exist
- Writes a valid `.py` test file with one `def test_...():` function per test case
- For test cases with a known expected output: writes an `assert` statement
- For test cases with no expected output (e.g. testing that an exception is raised): writes a `try/except` block

**Why it's needed:** PyTest needs a specific file format to run tests. This file acts as the translator from "AI output" to "runnable test code".

---

### `test_runner.py` — The PyTest Executor

This file actually *runs* the generated tests.

**What it does:**
- Calls PyTest as a subprocess (i.e. it runs `python -m pytest ...` as a command)
- Passes special flags to save results as a JSON report file
- In **regression mode**, filters to run only specific previously-failed tests (using PyTest's `-k` flag)
- Reads the JSON report and returns it as a Python dictionary

**Why it's needed:** Running PyTest via subprocess lets us capture its full output and results programmatically, so we can then generate a custom report from it.

---

### `report_generator.py` — The Defect Reporter

After tests run, this file formats and prints the final human-readable report.

**What it does:**
- Reads the PyTest results dictionary
- Counts how many tests passed and how many failed
- Prints a clean, formatted report showing:
  - Total test count
  - Passed count
  - Failed count
  - For each failed test: its name and the reason it failed
- Returns a list of the names of all failed tests (used by the regression tracker)

**Why it's needed:** Raw PyTest output is detailed but technical. This module presents results in a simple, easy-to-read summary format.

---

### `regression_tracker.py` — The Memory Module

This file gives the tool its memory across multiple runs.

**What it does:**
- **Saves** the names of any tests that failed after each run (stored in `generated_tests/regression_tracker.json`)
- **Loads** those saved failed test names when regression mode is activated
- Organises failures by function name, so tracking `add` and `divide` independently

**Why it's needed:** If you fix a bug and want to verify just the broken tests now pass — without re-running everything — this module enables that with the `--regression` flag.

---

### `requirements.txt` — The Dependency List

A plain text file listing all third-party libraries the project needs.

**Why it's needed:** Anyone cloning this project can run `pip install -r requirements.txt` to install everything at once.

---

### `.env` — The Secret Configuration File

Stores your Gemini API key. This file is **never shared or committed to GitHub**.

**Why it's needed:** Hardcoding API keys directly in source code is a major security risk. Storing them in `.env` keeps them out of version control.

---

### `.gitignore` — The "Don't Upload This" File

Tells Git which files to ignore when committing code.

**What it excludes:**
- `.env` (your secret API key)
- `__pycache__/` and `*.pyc` (compiled Python bytecode)
- `generated_tests/` (auto-generated test files — not source code)
- `.pytest_cache/` (PyTest internal cache)

---

### `sample_functions/calculator.py` — The Demo Functions

Three sample Python functions used to demonstrate and test the tool.

**Functions included:**
- `add(a, b)` — returns the sum of two values
- `divide(a, b)` — divides a by b, raises `ValueError` if b is zero
- `is_palindrome(s)` — checks if a string reads the same forwards and backwards

---

## 3. How the Tool Works — Step by Step

Here is the complete journey from when you press Enter to when you see the report:

```
User runs: python main.py sample_functions/calculator.py add
```

**Step 1 — Read the Function Source**
`main.py` calls `code_reader.py`, which loads `calculator.py` as a Python module and uses `inspect.getsource()` to extract the exact text of the `add` function.

**Step 2 — Build the AI Prompt**
`prompt_builder.py` wraps that source code in a carefully worded instruction for Gemini AI, specifying exactly what kind of test cases are needed and that the response must be pure JSON with no extra text.

**Step 3 — Call Gemini AI**
`llm_client.py` loads the API key from `.env`, creates a Gemini client, and sends the prompt to the `gemini-3.8-flash` model. Gemini responds with a JSON array like:

```json
[
  {"test_name": "test_normal_integers", "input": [2, 3], "expected_output": 5, "test_type": "normal"},
  {"test_name": "test_edge_zeros", "input": [0, 0], "expected_output": 0, "test_type": "edge"},
  {"test_name": "test_negative_invalid_type", "input": ["a", 1], "expected_output": null, "test_type": "negative"}
]
```

**Step 4 — Generate the PyTest File**
`test_generator.py` parses the JSON and writes `generated_tests/test_add.py`, containing one test function per test case.

**Step 5 — Run the Tests**
`test_runner.py` runs PyTest via subprocess and saves results to `generated_tests/report.json`.

**Step 6 — Generate the Report**
`report_generator.py` reads the JSON report and prints a clean summary:

```
============================================================
  QA DEFECT REPORT - add
============================================================
  Total Tests : 7
  Passed      : 7
  Failed      : 0
============================================================
All tests passed. No defects found.
```

**Step 7 — Save Failure State**
`regression_tracker.py` saves the names of any failed tests to `generated_tests/regression_tracker.json` for use in future regression runs.

---

## 4. Technologies and Libraries Used

| Technology | What It Is | Why We Used It |
|---|---|---|
| **Python 3.10+** | The programming language the entire tool is written in | Widely used, easy to read, excellent library support for AI and testing |
| **Gemini AI (gemini-3.8-flash)** | Google's large language model | The intelligence behind test case generation |
| **google-genai** | Official Python SDK for the new Gemini API | Provides a clean Python interface to call Gemini |
| **PyTest** | Python's most popular testing framework | Industry standard for running Python tests |
| **pytest-json-report** | A PyTest plugin | Saves test results as structured JSON so our tool can process them |
| **python-dotenv** | A small library for loading `.env` files | Keeps API keys out of source code |
| **inspect** (built-in) | Python's code introspection module | Extracts the exact source code of any function at runtime |
| **importlib** (built-in) | Python's module loader | Dynamically loads any `.py` file as a module |
| **argparse** (built-in) | Python's CLI argument parser | Gives the tool a proper command-line interface |
| **json** (built-in) | Python's JSON parser | Parses Gemini's response and the regression tracker file |
| **subprocess** (built-in) | Python's process runner | Runs PyTest as a separate process from within Python |
| **re** (built-in) | Python's regular expressions module | Used to robustly extract JSON from Gemini's response |

---

## 5. How to Run the Project

### Prerequisites
- Python 3.10 or newer installed
- A Gemini API key (free from https://aistudio.google.com/app/apikey)

### Setup (one time only)

```bash
# Install all dependencies
pip install -r requirements.txt

# Add your API key to the .env file
# Open .env and set:
GEMINI_API_KEY=your_actual_key_here
```

### Running the Tool

```bash
# Test the 'add' function
python main.py sample_functions/calculator.py add

# Test the 'divide' function
python main.py sample_functions/calculator.py divide

# Test the 'is_palindrome' function
python main.py sample_functions/calculator.py is_palindrome

# Test any function from your own files
python main.py path/to/your_file.py your_function_name
```

### Regression Mode

```bash
# Re-run only the tests that failed in the previous run
python main.py sample_functions/calculator.py add --regression
```

---

## 6. Issues Encountered While Building and How They Were Fixed

### Issue 1 — `google.generativeai` SDK Is Deprecated

**What happened:** Python printed a `FutureWarning` saying the `google.generativeai` package is no longer supported.

**Why it happened:** Google replaced it with a newer package called `google-genai`.

**How we fixed it:**
- Installed the new package: `pip install google-genai`
- Updated `llm_client.py` to use `from google import genai`
- Updated the API call to use `genai.Client(api_key=...)` and `client.models.generate_content(...)`

---

### Issue 2 — Model `gemini-2.0-flash` Was Retired

**What happened:** The API returned a `404 Not Found` error saying `gemini-2.0-flash` is no longer available.

**Why it happened:** Google regularly retires older model versions.

**How we fixed it:** Updated the model name in `llm_client.py` to `gemini-3.8-flash`.

---

### Issue 3 — Gemini Response Was Being Truncated Mid-JSON

**What happened:** Gemini returned a JSON array cut off in the middle, causing a `JSONDecodeError`.

**Why it happened:** The default token limit for the API response was too low.

**How we fixed it:**
- Added `max_output_tokens=8192` in the `GenerateContentConfig`
- Set `temperature=0.2` for more predictable output

---

### Issue 4 — JSON Extraction Regex Was Too Short-Sighted

**What happened:** The regular expression `\[.*?\]` stopped at the first `]` it found — which was inside a nested input array, not the end of the full JSON response.

**Why it happened:** The `.*?` pattern is "non-greedy" — it finds the shortest possible match.

**How we fixed it:** Replaced the regex with a simple bracket search:
- Find the first `[` in the response
- Find the last `]` in the response
- Extract everything between them

This correctly captures the entire outer array regardless of nesting.

---

### Issue 5 — Gemini Sometimes Wraps JSON in Markdown

**What happened:** Despite being told to return only JSON, Gemini would sometimes add markdown code fences or a sentence before the array.

**Why it happened:** Language models are trained on text that often includes such formatting.

**How we fixed it:** Added a robust `_extract_json_array()` function in `test_generator.py` that:
1. Strips any markdown fences with `re.sub()`
2. Tries to parse the cleaned text directly as JSON
3. Falls back to bracket extraction if direct parsing fails

---

*End of Project Summary*

---

**Author:** Kshitiz Aggarwal
**GitHub:** github.com/kshitiz16032
**Built with:** Python · Gemini AI · PyTest
