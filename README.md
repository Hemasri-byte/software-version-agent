# Software Version Agent

A Python-based software version monitoring tool that retrieves release information, detects locally installed versions, compares versions, and displays results in a Streamlit dashboard.

## Features

- Retrieves version information from configured release sources.
- Detects installed versions of Python, uv, Node.js, Git, and Visual Studio Code.
- Compares installed versions with retrieved versions.
- Generates CSV comparison reports and a text summary.
- Displays software status in an interactive Streamlit dashboard.
- Supports downloading reports as CSV files.

## Technology Stack

- Python
- Requests
- Beautiful Soup
- pandas
- packaging
- Streamlit
- CSV and REST APIs

## Project Structure

```text
software-version-agent/
├── main.py
├── compare_versions.py
├── dashboard.py
├── requiredsoftwares.csv
├── latest_versions.csv
├── version_comparison.csv
├── version_summary.txt
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.13
- uv
- Internet connection for retrieving release information

## Setup

Clone or download the repository, then open PowerShell in the project directory.

Install the project dependencies:

```powershell
uv sync
```

## Run the Version Checker

```powershell
uv run python main.py
```

This generates `latest_versions.csv`.

## Compare Installed Versions

```powershell
uv run python compare_versions.py
```

This generates `version_comparison.csv` and `version_summary.txt`.

## Launch the Dashboard

```powershell
uv run streamlit run dashboard.py
```

Open http://localhost:8501 in your browser.

Click **Check versions now** to refresh the reports and dashboard.

## Reports

- `latest_versions.csv`: versions retrieved from configured sources.
- `version_comparison.csv`: installed versions and comparison statuses.
- `version_summary.txt`: summary of the comparison results.

## Limitations

- Version results depend on the configured release sources.
- A version comparison does not guarantee that an upgrade is appropriate for every system.
- Some applications may not be detected if their commands or installation paths are unavailable.
- The tool reports update availability but does not automatically install software.

## Future Enhancements

- Improve Visual Studio Code installation detection.
- Add automated tests and error handling.
- Track version history over time.
- Add configurable software lists.
- Add optional notifications for available updates.

## License

Choose a license before distributing this project publicly.
