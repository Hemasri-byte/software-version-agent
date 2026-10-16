
import csv
import os
import socket

import requests

API_URL = "http://127.0.0.1:8000/reports"
AGENT_TOKEN = os.getenv("AGENT_TOKEN")

if not AGENT_TOKEN:
    raise SystemExit(
        "AGENT_TOKEN is missing. Set it in this PowerShell window."
    )

software = []

with open("version_comparison.csv", newline="", encoding="utf-8") as file:
    for row in csv.DictReader(file):
        software.append({
            "name": row["name"],
            "installed_version": row["installed_version"],
            "latest_version": row["latest_version"],
            "comparison_status": row["comparison_status"],
        })

payload = {
    "machine_name": socket.gethostname(),
    "software": software,
}

response = requests.post(
    API_URL,
    json=payload,
    headers={"X-Agent-Token": AGENT_TOKEN},
    timeout=15,
)

response.raise_for_status()
print("Report submitted successfully!")
print(response.json())
