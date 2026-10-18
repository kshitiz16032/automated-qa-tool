import json
import os
import re

def _extract_json_array(raw: str) -> list:
    """Robustly extract a JSON array from Gemini's response, even if wrapped in markdown or prose."""
    # Strip markdown code fences if present
    clean = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
    # Try direct parse first
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass
    # Fall back: extract from first '[' to last ']' (greedy, handles nested objects)
    start = clean.find("[")
    end = clean.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(clean[start:end + 1])
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Could not extract a valid JSON array from Gemini response:\n{raw[:500]}")

def generate_pytest_file(test_cases_json: str, function_name: str, file_path: str) -> str:
    try:
        test_cases = _extract_json_array(test_cases_json)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to parse Gemini response as JSON: {e}")
        raise

    os.makedirs("generated_tests", exist_ok=True)
    output_path = f"generated_tests/test_{function_name}.py"
    module_path = os.path.abspath(file_path).replace("\\", "/")

    lines = []
    lines.append("import sys")
    lines.append(f"sys.path.insert(0, '{os.path.dirname(module_path)}')")
    lines.append(f"from {os.path.splitext(os.path.basename(file_path))[0]} import {function_name}")
    lines.append("import pytest")
    lines.append("")

    for tc in test_cases:
        test_name = tc.get("test_name", "test_case")
        inputs = tc.get("input", [])
        expected = tc.get("expected_output")
        lines.append(f"def {test_name}():")
        if expected is None:
            lines.append(f"    try:")
            lines.append(f"        {function_name}(*{inputs})")
            lines.append(f"    except Exception:")
            lines.append(f"        pass")
        else:
            lines.append(f"    assert {function_name}(*{inputs}) == {repr(expected)}")
        lines.append("")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Generated {len(test_cases)} test cases at {output_path}")
    return output_path
