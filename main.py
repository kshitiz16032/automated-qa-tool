import argparse
from code_reader import read_function_source
from prompt_builder import build_prompt
from llm_client import get_gemini_response
from test_generator import generate_pytest_file
from test_runner import run_tests
from report_generator import generate_report
from regression_tracker import load_failed_tests, save_failed_tests

def main():
    parser = argparse.ArgumentParser(description="Automated QA Intelligence Tool")
    parser.add_argument("file", help="Path to the Python file containing the function")
    parser.add_argument("function", help="Name of the function to test")
    parser.add_argument("--regression", action="store_true",
                        help="Run only previously failed tests")
    args = parser.parse_args()

    print(f"\nReading function: {args.function} from {args.file}")
    source = read_function_source(args.file, args.function)

    print("Sending to Gemini AI for test case generation...")
    prompt = build_prompt(source, args.function)
    raw_response = get_gemini_response(prompt)

    print("Generating PyTest file...")
    test_file = generate_pytest_file(raw_response, args.function, args.file)

    failed_tests = load_failed_tests(args.function) if args.regression else None
    results = run_tests(test_file, regression_only=args.regression, failed_tests=failed_tests)

    failed = generate_report(results, args.function)
    save_failed_tests(args.function, failed)

if __name__ == "__main__":
    main()
