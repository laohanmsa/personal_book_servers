---
description: Clean up the git repository by identifying, ignoring, and untracking unwanted files.
category: git
status: active
safety: writes-local
---

> [!WARNING]
> This workflow changes git tracking state (`.gitignore`, `git rm --cached`). Review the target files carefully and ask before any history-rewrite action.

1. **Analyze Git Status**
   Check the current status to identify untracked files and files that are tracked but shouldn't be.
   ```bash
   git status
   git ls-files --others --exclude-standard
   ```

2. **Identify Patterns to Ignore**
   Review the list of untracked files. Look for:
   - Data files (`.csv`, `.json`, `.sqlite`)
   - Logs (`.log`, debug txt files)
   - Virtual environments (`venv`, `.env`)
   - IDE settings (`.vscode`, `.idea`)
   - Build artifacts

3. **Update .gitignore**
   Add the identified patterns to `.gitignore`.
   // turbo
   ```bash
   # Example: echo "pattern" >> .gitignore
   ```
   *Action*: Edit `.gitignore` directly (e.g. `apply_patch`) or append with shell commands.

4. **Untrack Previously Tracked Files**
   If any files were already tracked but now need to be ignored, remove them from the index without deleting them from the filesystem.
   ```bash
   git rm --cached <path_to_file_or_dir>
   ```

5. **Verify Clean Removal**
   Check if the files are correctly staged for deletion and ignored.
   ```bash
   git status
   ```

6. **Check History for Leaked Files**
   Verify if the now-ignored files exist in previous commits (to detect sensitive data or large files in history). If found, report it and ask before any history rewrite or cleanup action.
   ```bash
   git log --all --name-only --pretty=format:"" | sort -u | grep "<pattern>"
   ```

7. **Commit Changes**
   Commit the `.gitignore` update and the file removals.
   ```bash
   git add .gitignore
   git commit -m "chore: update gitignore and untrack data/log files"
   ```
