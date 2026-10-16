import csv
import re
import requests
from bs4 import BeautifulSoup

INPUT_FILE = "requiredsoftwares.csv"
OUTPUT_FILE = "latest_versions.csv"

session = requests.Session()
session.headers.update({
    "User-Agent": "SoftwareVersionAgent/1.0",
    "Accept": "application/vnd.github+json"
})

def get_json(url):
    response = session.get(url, timeout=20)
    response.raise_for_status()
    return response.json()

def get_html(url):
    response = session.get(url, timeout=20)
    response.raise_for_status()
    return response.text

def check_version(name):
    key = name.strip().lower()

    try:
        if key == "python":
            html = get_html("https://www.python.org/downloads/")
            soup = BeautifulSoup(html, "html.parser")
            candidates = []

            for link in soup.select("a[href]"):
                text = link.get_text(" ", strip=True)
                match = re.search(r"Python\s+(3\.\d+\.\d+)", text)
                if match:
                    candidates.append(match.group(1))

            if candidates:
                version = candidates[0]
                return version, "https://www.python.org/downloads/", "verified"

        elif key == "node.js":
            data = get_json("https://nodejs.org/dist/index.json")
            stable = [
                item for item in data
                if not item.get("version", "").startswith("v")
                or "-" not in item.get("version", "")
            ]
            stable = [
                item for item in stable
                if item.get("lts") and item.get("version", "").startswith("v")
            ]
            if stable:
                return stable[0]["version"].lstrip("v"), (
                    "https://nodejs.org/en/download"
                ), "verified"

        elif key == "uv":
            data = get_json("https://api.github.com/repos/astral-sh/uv/releases/latest")
            return data["tag_name"].lstrip("v"), data["html_url"], "verified"

        elif key == "git":
            data = get_json(
                "https://api.github.com/repos/git-for-windows/git/releases/latest"
            )
            return data["tag_name"].lstrip("v"), data["html_url"], "verified"

        elif key == "visual studio code":
            data = get_json(
                "https://api.github.com/repos/microsoft/vscode/releases/latest"
            )
            return data["tag_name"].lstrip("v"), data["html_url"], "verified"

        return "Unknown", "", "unverified"

    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        print(f"Could not verify {name}: {exc}")
        return "Unknown", "", "unverified"

def main():
    with open(INPUT_FILE, newline="", encoding="utf-8-sig") as file:
        items = list(csv.DictReader(file))

    fields = [
        "sno", "name", "current_version", "latest_version",
        "source_url", "status", "notes"
    ]

    results = []

    for item in items:
        name = (item.get("name") or "").strip()
        if not name:
            continue

        print(f"\nChecking {name}...")
        version, source, status = check_version(name)

        results.append({
            "sno": item.get("sno", ""),
            "name": name,
            "current_version": item.get("version", ""),
            "latest_version": version,
            "source_url": source,
            "status": status,
            "notes": (
                "Retrieved from a release source."
                if status == "verified"
                else "Could not verify; check the official source."
            )
        })

        print(f"Latest: {version} | Status: {status}")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nReport saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
