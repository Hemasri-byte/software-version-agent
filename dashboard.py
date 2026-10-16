import csv
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
LATEST_FILE = BASE_DIR / "latest_versions.csv"
COMPARISON_FILE = BASE_DIR / "version_comparison.csv"
SUMMARY_FILE = BASE_DIR / "version_summary.txt"

st.set_page_config(
    page_title="Software Version Agent",
    page_icon="🖥️",
    layout="wide",
)

st.title("🖥️ Software Version Agent")
st.caption("Check software releases, compare versions, and review update status.")

def read_csv(path):
    if path.exists():
        try:
            return pd.read_csv(path).fillna("")
        except (OSError, pd.errors.ParserError):
            return pd.DataFrame()
    return pd.DataFrame()

def run_script(script_name):
    script_path = BASE_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(message or f"{script_name} failed.")
    return result.stdout.strip()

with st.sidebar:
    st.header("Controls")
    st.write("Run the checker to refresh the reports.")
    refresh = st.button("🔄 Check versions now", use_container_width=True)

    st.divider()
    st.write("**Project outputs**")
    st.write("• latest_versions.csv")
    st.write("• version_comparison.csv")
    st.write("• version_summary.txt")

if refresh:
    try:
        with st.spinner("Checking official release sources..."):
            output = run_script("main.py")
            st.session_state["checker_output"] = output

        with st.spinner("Comparing installed versions..."):
            output = run_script("compare_versions.py")
            st.session_state["comparison_output"] = output

        st.success("Version check and comparison completed.")
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        st.error(f"Could not complete the check: {exc}")

comparison = read_csv(COMPARISON_FILE)
latest = read_csv(LATEST_FILE)

if not comparison.empty and "comparison_status" in comparison.columns:
    statuses = comparison["comparison_status"].astype(str)
    updates = int((statuses == "Update available").sum())
    current = int((statuses == "Up to date").sum())
    undetected = int(
        statuses.str.contains("Could not detect installed version", regex=False).sum()
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Software checked", len(comparison))
    col2.metric("Updates available", updates)
    col3.metric("Up to date", current)
    col4.metric("Not detected", undetected)

    st.subheader("Version comparison")
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download comparison CSV",
        data=comparison.to_csv(index=False).encode("utf-8"),
        file_name="version_comparison.csv",
        mime="text/csv",
    )
else:
    st.info("No comparison report found yet. Click **Check versions now** in the sidebar.")

if not latest.empty:
    st.subheader("Latest versions from release sources")
    st.dataframe(latest, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Download latest versions CSV",
        data=latest.to_csv(index=False).encode("utf-8"),
        file_name="latest_versions.csv",
        mime="text/csv",
    )

if SUMMARY_FILE.exists():
    st.subheader("Text summary")
    st.text(SUMMARY_FILE.read_text(encoding="utf-8"))

with st.expander("Last run output"):
    st.text(st.session_state.get("checker_output", "Checker has not run in this session."))
    st.text(st.session_state.get("comparison_output", "Comparison has not run in this session."))

st.divider()
st.caption("Note: version results depend on the release sources configured in main.py.")
