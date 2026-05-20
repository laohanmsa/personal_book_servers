
import sys
import os
import re

def collapse_match(match):
    """
    Takes a regex match object (which captured the inner content of a tag/variable),
    and collapses it to a single line with normalized spacing.
    """
    full_match = match.group(0)
    inner_content = match.group(1)

    # If there are no newlines in the full match, return it as is
    if '\n' not in full_match:
        return full_match

    # Replace all whitespace sequences (including newlines) with a single space
    # but first strip leading/trailing whitespace of the inner content
    cleaned_inner = re.sub(r'\s+', ' ', inner_content.strip())

    # Reconstruct the tag/variable with the original delimiters
    if full_match.startswith('{{'):
        return f'{{{{ {cleaned_inner} }}}}'
    elif full_match.startswith('{%'):
        return f'{{% {cleaned_inner} %}}'
    return full_match # Should not happen based on regex

def fix_file(filepath):
    # 2. check if it is html or template file
    if not (filepath.endswith('.html') or filepath.endswith('.txt')): # .txt sometimes used for templates
        print(f"Skipping {filepath}: Not an HTML or template file.")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    original_content = content

    # Regex for {{ ... }} and {% ... %}
    # We use non-greedy matching .*?
    # We allow multiline via DOTALL (passing it as flag to sub won't work easily with lambda,
    # so we compile patterns)

    # Pattern for variables: {{ ... }}
    var_pattern = re.compile(r'({{\s*(.*?)\s*}})', re.DOTALL)
    content = var_pattern.sub(collapse_match, content)

    # Pattern for block tags: {% ... %}
    tag_pattern = re.compile(r'({%\s*(.*?)\s*%})', re.DOTALL)
    content = tag_pattern.sub(collapse_match, content)

    if content != original_content:
        # Calculate fixed lines for reporting
        print(f"Found multiline tags/variables in {filepath}. Fixing...")

        # We can't easily map back to line numbers after substitution without complex logic,
        # but we can try to confirm what changed.
        # For the requirement "report the fixed lines", we will compare diffs or just report success.
        # A simple way is to iterate matches again on original content to report line numbers before fixing.

        # Re-scan original content to report line numbers of issues
        issues = []
        for match in var_pattern.finditer(original_content):
            if '\n' in match.group(0):
                line_no = original_content[:match.start()].count('\n') + 1
                issues.append(f"Line {line_no}: Multiline variable {{ ... }}")

        for match in tag_pattern.finditer(original_content):
            if '\n' in match.group(0):
                line_no = original_content[:match.start()].count('\n') + 1
                issues.append(f"Line {line_no}: Multiline tag {{% ... %}}")

        for issue in issues:
            print(issue)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully updated {filepath}.")
    else:
        print(f"No multiline tags found in {filepath}.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python template_formatter.py <filepath>")
        sys.exit(1)

    target_file = sys.argv[1]
    if os.path.exists(target_file):
        fix_file(target_file)
    else:
        print(f"File not found: {target_file}")
