def generate_report(pytest_results: dict, function_name: str) -> list:
    tests = pytest_results.get("tests", [])
    passed = [t for t in tests if t["outcome"] == "passed"]
    failed = [t for t in tests if t["outcome"] == "failed"]

    print("\n" + "="*60)
    print(f"  QA DEFECT REPORT — {function_name}")
    print("="*60)
    print(f"  Total Tests : {len(tests)}")
    print(f"  Passed      : {len(passed)}")
    print(f"  Failed      : {len(failed)}")
    print("="*60)

    if failed:
        print("\nFAILED TESTS:")
        for t in failed:
            print(f"  - {t['nodeid']}")
            if "call" in t and "longrepr" in t["call"]:
                print(f"    Reason: {t['call']['longrepr'][:200]}")
    else:
        print("\nAll tests passed. No defects found.")

    print("\n" + "="*60 + "\n")
    return [t["nodeid"].split("::")[1] for t in failed]
