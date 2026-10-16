import csv
import re
import subprocess
from pathlib import Path

SOURCE_EXTENSIONS = {".py", ".js", ".java"}
OUTPUT_FILE = "file_authors.csv"

AUTHOR_PATTERNS = [
    re.compile(r"^\s*#\s*Author\s*:\s*(.+)$", re.IGNORECASE),
    re.compile(r"^\s*//\s*Author\s*:\s*(.+)$", re.IGNORECASE),
    re.compile(r"^\s*\*\s*@author\s+(.+)$", re.IGNORECASE),
    re.compile(r"^\s*\*\s*Author\s*:\s*(.+)$", re.IGNORECASE),
    re.compile(r"^\s*/\*\s*Author\s*:\s*(.+?)\s*\*/", re.IGNORECASE),
]


def find_comment_author(file_path):
    try:
        with file_path.open("r", encoding="utf-8", errors="replace") as file:
            for line_number, line in enumerate(file, start=1):
                if line_number > 80:
                    break

                for pattern in AUTHOR_PATTERNS:
                    match = pattern.search(line)
                    if match:
                        return match.group(1).strip()

    except OSError:
        pass

    return ""


def find_git_author(file_path, root):
    try:
        relative_path = file_path.resolve().relative_to(root.resolve())

        result = subprocess.run(
            [
                "git", "log", "-1", "--format=%an",
                "--", relative_path.as_posix()
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return result.stdout.strip()

    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass

    return ""


def main():
    folder = input(
        "Enter source-code folder path (Enter for current folder): "
    ).strip()

    root = Path(folder).expanduser().resolve() if folder else Path.cwd()

    if not root.is_dir():
        print(f"Folder does not exist: {root}")
        return

    results = []

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue

        if any(
            part.lower() in {".venv", ".git", "__pycache__", "node_modules"}
            for part in path.parts
        ):
            continue

        author = find_comment_author(path)

        if author:
            method = "Source-code comment"
        else:
            author = find_git_author(path, root)
            if author:
                method = "Latest Git commit author"
            else:
                author = "Not found"
                method = "No comment or Git history author found"

        results.append({
            "file_path": str(path.resolve()),
            "language": path.suffix.lower().lstrip("."),
            "author": author,
            "method": method,
        })

        print(f"{path.name}: {author} ({method})")

    fields = ["file_path", "language", "author", "method"]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nFiles scanned: {len(results)}")
    print(f"Report saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
