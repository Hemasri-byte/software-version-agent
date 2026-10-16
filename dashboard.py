import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
LATEST_FILE = BASE_DIR / "latest_versions.csv"
COMPARISON_FILE = BASE_DIR / "version_comparison.csv"
SUMMARY_FILE = BASE_DIR / "version_summary.txt"
AUTHORS_FILE = BASE_DIR / "file_authors.csv"

st.set_page_config(
    page_title="Software Version Agent",
    page_icon="🖥️",
    layout="wide",
)

st.title("🖥️ Software Version Agent")
st.caption(
    "Check software releases, compare versions, and identify source-code authors."
)


def read_csv(path):
    if path.exists():
        try:
            return pd.read_csv(path).fillna("")
        except (OSError, pd.errors.ParserError):
            return pd.DataFrame()
    return pd.DataFrame()


def run_script(script_name, input_text=None):
    script_path = BASE_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR,
        input=input_text,
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
    st.write("Refresh the reports when required.")

    refresh_versions = st.button(
        "🔄 Check versions now", width="stretch"
    )
    refresh_authors = st.button(
        "👤 Scan source-code authors", width="stretch"
    )

    st.divider()
    st.write("**Project outputs**")
    st.write("- latest_versions.csv")
    st.write("- version_comparison.csv")
    st.write("- version_summary.txt")
    st.write("- file_authors.csv")


if refresh_versions:
    try:
        with st.spinner("Checking release sources..."):
            st.session_state["checker_output"] = run_script("main.py")

        with st.spinner("Comparing installed versions..."):
            st.session_state["comparison_output"] = run_script(
                "compare_versions.py"
            )

        st.success("Version check and comparison completed.")
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        st.error(f"Version check failed: {exc}")


if refresh_authors:
    try:
        with st.spinner("Scanning source-code files..."):
            st.session_state["author_output"] = run_script(
                "author_finder.py",
                input_text=str(BASE_DIR) + "\n",
            )
        st.success("Source-code author scan completed.")
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        st.error(f"Author scan failed: {exc}")


comparison = read_csv(COMPARISON_FILE)
latest = read_csv(LATEST_FILE)
authors = read_csv(AUTHORS_FILE)

if not comparison.empty and "comparison_status" in comparison.columns:
    statuses = comparison["comparison_status"].astype(str)
    updates = int((statuses == "Update available").sum())
    current = int((statuses == "Up to date").sum())
    undetected = int(
        statuses.str.contains(
            "Could not detect installed version", regex=False
        ).sum()
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Software checked", len(comparison))
    col2.metric("Updates available", updates)
    col3.metric("Up to date", current)
    col4.metric("Not detected", undetected)

    st.subheader("Version comparison")
    st.dataframe(comparison, width="stretch", hide_index=True)

    st.download_button(
        "⬇️ Download comparison CSV",
        data=comparison.to_csv(index=False).encode("utf-8"),
        file_name="version_comparison.csv",
        mime="text/csv",
    )
else:
    st.info(
        "No comparison report found yet. Click Check versions now in the sidebar."
    )


if not latest.empty:
    st.subheader("Latest versions from release sources")
    st.dataframe(latest, width="stretch", hide_index=True)

    st.download_button(
        "⬇️ Download latest versions CSV",
        data=latest.to_csv(index=False).encode("utf-8"),
        file_name="latest_versions.csv",
        mime="text/csv",
    )


st.subheader("Source Code Authors")
st.caption(
    "Author names are obtained from source-code comments or the latest "
    "Git commit affecting each file. Git commit authors may differ from "
    "the original file authors."
)

if not authors.empty:
    st.dataframe(authors, width="stretch", hide_index=True)

    st.download_button(
        "⬇️ Download author report",
        data=authors.to_csv(index=False).encode("utf-8"),
        file_name="file_authors.csv",
        mime="text/csv",
    )
else:
    st.info(
        "No author report found yet. Click Scan source-code authors in the sidebar."
    )


if SUMMARY_FILE.exists():
    st.subheader("Text summary")
    st.text(SUMMARY_FILE.read_text(encoding="utf-8"))

with st.expander("Last run output"):
    st.text(
        st.session_state.get(
            "checker_output", "Checker has not run in this session."
        )
    )
    st.text(
        st.session_state.get(
            "comparison_output", "Comparison has not run in this session."
        )
    )
    st.text(
        st.session_state.get(
            "author_output", "Author scan has not run in this session."
        )
    )

st.divider()
st.caption(
    "Version results depend on the release sources configured in main.py."
)
