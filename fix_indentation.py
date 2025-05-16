#!/usr/bin/env python3
"""
Script to fix indentation issues in enhanced_hta_service.py by identifying code that's outside of any method
"""

import re
import sys

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def fix_indentation_issues():
    """
    Find code with indentation that's not inside a method
    and remove it or put it inside the appropriate method
    """
    file_path = "forest_app/core/services/enhanced_hta_service.py"
<<<<<<< HEAD
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
=======

    with open(file_path, "r") as f:
        lines = f.readlines()

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    fixed_lines = []
    in_class = False
    method_indent_level = 0
    skip_lines = False
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    for i, line in enumerate(lines):
        # Detect class definition
        if line.strip().startswith("class EnhancedHTAService"):
            in_class = True
            fixed_lines.append(line)
            continue
<<<<<<< HEAD
        
        # Skip any floating indented code blocks
        if in_class and line.strip() and line.startswith("    ") and not skip_lines:
            # Check if it's a method definition
            if re.match(r'\s+def\s+\w+\(', line):
=======

        # Skip any floating indented code blocks
        if in_class and line.strip() and line.startswith("    ") and not skip_lines:
            # Check if it's a method definition
            if re.match(r"\s+def\s+\w+\(", line):
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                # It's a method definition, keep it
                method_indent_level = len(line) - len(line.lstrip())
                fixed_lines.append(line)
            # Check if it's inside a method (more indented than method)
            elif len(line) - len(line.lstrip()) > method_indent_level:
                fixed_lines.append(line)
            # Check if it's a class-level field
<<<<<<< HEAD
            elif not line.strip().startswith(("#", "\"\"\"", "@")):
                # It's not a comment, docstring, or decorator - potential issue
                print(f"Found potentially problematic line {i+1}: {line.strip()}")
=======
            elif not line.strip().startswith(("#", '"""', "@")):
                # It's not a comment, docstring, or decorator - potential issue
                print(f"Found potentially problematic line {i + 1}: {line.strip()}")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                # Skip this line
                continue
            else:
                fixed_lines.append(line)
        else:
            # Not indented or outside of class, keep it
            fixed_lines.append(line)
<<<<<<< HEAD
    
    # Write the fixed content back to the file
    with open(file_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed indentation issues in {file_path}")
    return True

=======

    # Write the fixed content back to the file
    with open(file_path, "w") as f:
        f.writelines(fixed_lines)

    print(f"Fixed indentation issues in {file_path}")
    return True


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
if __name__ == "__main__":
    if fix_indentation_issues():
        sys.exit(0)
    else:
        sys.exit(1)
