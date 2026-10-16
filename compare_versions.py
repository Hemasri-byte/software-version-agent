import csv
import os
import re
import subprocess
from packaging.version import Version

INPUT_FILE = "latest_versions.csv"
OUTPUT_FILE = "version_comparison.csv"
SUMMARY_FILE = "version_summary.txt"

def run_command(command):
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip() or result.stderr.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return ""

def get_installed_version(name):
    commands = {
        "Python": ["python", "--version"],
        "uv": ["uv", "--version"],
        "Node.js": ["node", "--version"],
        "Git": ["git", "--version"],
    }

    if name == "Visual Studio Code":
        output = run_command(["cmd", "/c", "code --version"])
        if output:
            return output.splitlines()[0].strip()

        paths = [
            os.path.expandvars(
                r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"
            ),
            os.path.expandvars(
                r"%ProgramFiles%\Microsoft VS Code\Code.exe"
            ),
            os.path.expandvars(
                r"%ProgramFiles(x86)%\Microsoft VS Code\Code.exe"
            ),
        ]

        for path in paths:
            if os.path.isfile(path):
                output = run_command([path, "--version"])
                if output:
                    return output.splitlines()[0].strip()

        return "Not detected"

    output = run_command(commands.get(name, []))
    if not output:
        return "Not detected"

    match = re.search(r"(?<!\d)v?(\d+\.\d+\.\d+)", output)
    return match.group(1) if match else "Unknown"

def normalize_version(value):
    match = re.search(r"(\d+\.\d+\.\d+)", value or "")
    return match.group(1) if match else None

def compare(installed, latest):
    if installed in ("Unknown", "Not detected"):
        return "Could not detect installed version"

    installed_normalized = normalize_version(installed)
    latest_normalized = normalize_version(latest)

    if not installed_normalized:
        return "Could not read installed version"
    if not latest_normalized:
        return "Latest version unavailable"

    try:
        current = Version(installed_normalized)
        newest = Version(latest_normalized)

        if current < newest:
            return "Update available"
        if current == newest:
            return "Up to date"
        return "Installed version is newer"
    except Exception:
        return "Could not compare versions"

def main():
    with open(INPUT_FILE, newline="", encoding="utf-8-sig") as file:
        software_list = list(csv.DictReader(file))

    fields = [
        "name", "installed_version", "latest_version",
        "comparison_status", "source_url"
    ]
    results = []

    for item in software_list:
        name = item["name"].strip()
        latest = item["latest_version"].strip()
        installed = get_installed_version(name)
        status = compare(installed, latest)

        results.append({
            "name": name,
            "installed_version": installed,
            "latest_version": latest,
            "comparison_status": status,
            "source_url": item["source_url"],
        })

        print(
            f"{name}: installed={installed}, latest={latest}, "
            f"status={status}"
        )

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    update_count = sum(
        row["comparison_status"] == "Update available" for row in results
    )
    current_count = sum(
        row["comparison_status"] == "Up to date" for row in results
    )
    undetected_count = sum(
        row["comparison_status"] == "Could not detect installed version"
        for row in results
    )
    other_count = len(results) - update_count - current_count - undetected_count

    summary = (
        "SOFTWARE VERSION SUMMARY\n"
        "========================\n"
        f"Total software checked: {len(results)}\n"
        f"Updates available: {update_count}\n"
        f"Up to date: {current_count}\n"
        f"Installed version not detected: {undetected_count}\n"
        f"Other results: {other_count}\n\n"
        "Details:\n"
        + "\n".join(
            f"- {row['name']}: {row['comparison_status']}"
            for row in results
        )
    )

    with open(SUMMARY_FILE, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"\nComparison report saved to {OUTPUT_FILE}")
    print(f"Summary saved to {SUMMARY_FILE}\n")
    print(summary)

if __name__ == "__main__":
    main()
