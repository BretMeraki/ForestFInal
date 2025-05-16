import subprocess
import re

def test_pylint_no_errors():
    """
    Run pylint on the codebase and assert that there are no E-codes (errors).
    This test will fail if any critical errors are present.
    """
    result = subprocess.run(
        [
            "pylint",
            "forest_app",
            "tests",
            "--output-format=text",
        ],
        capture_output=True,
        text=True,
    )
    # Look for lines starting with E (error codes)
    error_lines = [
        line for line in result.stdout.splitlines()
        if re.match(r"^.+: E[0-9]{4}:", line)
    ]
    if error_lines:
        print("\n\nPylint errors found:\n" + "\n".join(error_lines))
    assert not error_lines, "Pylint E-codes (errors) found in codebase!" 