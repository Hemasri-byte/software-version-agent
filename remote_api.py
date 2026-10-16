
import os
import secrets
from datetime import datetime, timezone

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Software Version Agent API")

AGENT_TOKEN = os.getenv("AGENT_TOKEN")


class SoftwareVersion(BaseModel):
    name: str
    installed_version: str
    latest_version: str = ""
    comparison_status: str = ""


class MachineReport(BaseModel):
    machine_name: str = Field(min_length=1, max_length=100)
    software: list[SoftwareVersion]


@app.get("/")
def health():
    return {"status": "online", "service": "Software Version Agent API"}


@app.post("/reports")
def receive_report(
    report: MachineReport,
    x_agent_token: str = Header(default=""),
):
    if not AGENT_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="Server authentication token is not configured",
        )

    if not secrets.compare_digest(x_agent_token, AGENT_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid agent token")

    os.makedirs("reports", exist_ok=True)

    safe_name = "".join(
        char for char in report.machine_name
        if char.isalnum() or char in "-_"
    )[:100] or "remote-machine"

    filename = f"reports/{safe_name}.json"
    data = {
        "machine_name": report.machine_name,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "software": [item.model_dump() for item in report.software],
    }

    import json
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    return {"status": "received", "machine_name": report.machine_name}
