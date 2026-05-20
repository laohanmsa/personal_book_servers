---
name: Django Template Formatter
description: Enforce single-line usage for Django template tags and variables.
category: formatting
status: active
safety: writes-local
---

# Django Template Formatter Skill

This skill provides a utility to scan a Django template file and flatten any multiline `{{ variable }}` or `{% tag %}` constructs into a single line, as split lines can cause Django `TemplateSyntaxError`.

## Usage

When you encounter a Django template mismatch or want to ensure code quality, run the provided python script on the target file.

### formatting a single file

```bash
python .agent/skills/django_template_formatter/template_formatter.py /path/to/template.html
```

## Behavior

1.  Checks if the file ends with `.html` or `.txt` (skips otherwise).
2.  Scans for `{{ ... }}` and `{% ... %}` blocks that span multiple lines.
3.  Collapses them into a single line, normalizing internal whitespace to a single space.
4.  Reports the line numbers where fixes were applied.
5.  Overwrites the file with the corrected content.
