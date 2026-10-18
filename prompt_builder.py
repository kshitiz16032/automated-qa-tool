def build_prompt(function_source: str, function_name: str) -> str:
    return f"""You are a software testing expert. Analyze the following Python function and generate test cases.

Function:
{function_source}

Generate exactly 6 to 8 test cases covering:
1. Normal inputs (typical expected use)
2. Edge cases (empty, zero, single item)
3. Negative inputs (wrong types, invalid values — set expected_output to null for these)
4. Boundary values (min, max, just above/below limits)

CRITICAL: Return ONLY a raw JSON array. Absolutely no markdown, no code fences, no explanation text before or after. Start your response with [ and end with ].

Format example:
[
  {{"test_name": "test_normal_addition", "input": [2, 3], "expected_output": 5, "test_type": "normal"}},
  {{"test_name": "test_edge_zero", "input": [0, 0], "expected_output": 0, "test_type": "edge"}}
]

Function name to test: {function_name}
"""
