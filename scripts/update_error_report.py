import os
import re

ERROR_LOG = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../error_rolling.log")
)
REPORT_MD = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../CRITICAL_ERRORS_REPORT.md")
)

RECENT_ERRORS_HEADER = "## Recent Errors\n"


def extract_errors_from_log(log_path):
    errors = set()
    if not os.path.exists(log_path):
        return errors
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if "ERROR" in line:
                # Extract the error message after 'ERROR'
                match = re.search(r"ERROR\s+(.*)", line)
                if match:
                    errors.add(match.group(1).strip())
    return errors


def read_existing_recent_errors(md_path):
    if not os.path.exists(md_path):
        return set(), None, None
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    start = content.find(RECENT_ERRORS_HEADER)
    if start == -1:
        return set(), content, None
    end = content.find("---", start)
    if end == -1:
        end = len(content)
    section = content[start + len(RECENT_ERRORS_HEADER) : end].strip()
    existing = set(
        line.strip("- ").strip() for line in section.split("\n") if line.strip()
    )
    return existing, content, (start, end)


def update_report_with_errors(errors, md_path):
    existing, content, section_range = read_existing_recent_errors(md_path)
    new_errors = errors - existing
    if not new_errors:
        print("No new errors to add.")
        return
    new_section = "\n".join(f"- {err}" for err in sorted(existing | new_errors))
    if section_range:
        start, end = section_range
        updated = (
            content[: start + len(RECENT_ERRORS_HEADER)]
            + new_section
            + "\n"
            + content[end:]
        )
    else:
        # Insert after introduction (after first '---')
        intro_end = content.find("---")
        if intro_end == -1:
            intro_end = 0
        updated = (
            content[:intro_end]
            + "---\n\n"
            + RECENT_ERRORS_HEADER
            + new_section
            + "\n\n"
            + content[intro_end:]
        )
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(updated)
    print(f"Added {len(new_errors)} new errors to the report.")


def main():
    errors = extract_errors_from_log(ERROR_LOG)
    update_report_with_errors(errors, REPORT_MD)


if __name__ == "__main__":
    main()
