# ImportFromClickUpToYouTrack

# Overview

The **ImportFromClickUpToYouTrack** project is a Python-based integration tool designed to streamline issue tracking workflows between GitHub and YouTrack.  

This project solves a real-world need for development teams that manage issues across multiple platforms by automating the process of transferring and synchronizing issues. It reduces manual work, improves consistency, and keeps teams aligned.  

Key capabilities include:
- **Automated Issue Import** — Quickly bring GitHub issues into YouTrack without manual duplication.
- **Two-way Synchronization** — Keep both systems up-to-date with the latest issue data.
- **Custom Field Mapping** — Automatically map GitHub issue fields (title, description, state, assignee, labels) to YouTrack custom fields.
- **Duplicate Detection** — Prevent creating duplicate issues in YouTrack by checking existing issues before import.
- **Extensible Design** — Uses the Strategy Pattern for field mapping, enabling easy extension for new fields or services.
- **Configurable Sync Modes** — One-time imports or continuous synchronization with adjustable intervals.
- **Dry-run Mode** — Test imports without making any changes, useful for validating configuration.
- **Detailed Logging** — Comprehensive logs for debugging, tracking progress, and auditing.

This tool is ideal for:
- Development teams migrating issue history from GitHub to YouTrack.
- Teams who want to keep GitHub and YouTrack issue boards in sync.
- Organizations aiming to standardize issue workflows across platforms.
- Developers who need a robust and extensible solution for issue integration.

---

# Features

- **Full Issue Import:** Import issues from GitHub to YouTrack, including description, state, assignee, and labels.
- **Smart Synchronization:** Check for existing issues before creating to avoid duplicates.
- **Custom Field Strategy:** Flexible field mapping using the Strategy Pattern.
- **Logging & Error Handling:** Comprehensive logs and exception handling for production reliability.
- **Configurable:** Adjust sync intervals, issue limits, and run in dry-run mode for safe testing.

---

# Requirements

- Python 3.9+
- GitHub Personal Access Token
- YouTrack API Token
- Required Python packages (see `requirements.txt`)

---


---
## Installation

1. Clone the repository:

```bash
git clone https://github.com/devlastu/ImportFromClickUpToYouTrack.git
cd ImportFromClickUpToYouTrack
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```
---

## Key Components

### 🔌 API Clients (`src/clients/`)
- **github_client.py**: Handles GitHub API interactions
- **youtrack_client.py**: Manages YouTrack API communications

### 🗺️ Mappers (`src/mappers/`)
- **issue_mapper.py**: Core mapping logic between GitHub and YouTrack issues
- **field_strategies/**: Individual field transformation strategies

### 🛠️ Services (`src/services/`)
- **issue_service.py**: CRUD operations for issues
- **project_service.py**: Project management in YouTrack
- **user_service.py**: User validation and assignment logic
- **service_orchestrator.py**: Coordinates all services

### 🔄 Synchronizers (`src/synchronizers/`)
- **issue_synchronizer.py**: Main sync engine between platforms

### ⚙️ Configuration
- **config.py**: Environment variables and settings
- **logging_config.py**: Logging setup and configuration

### 🖥️ Entry Point
- **cli.py**: Command-line interface for tool execution

---

# Configuration

-Edit src/config.py with your own credentials:

### config.py
GITHUB_TOKEN = "your_github_token_here"
YOUTRACK_TOKEN = "your_youtrack_token_here"
YOUTRACK_URL = "https://your-instance.youtrack.cloud"
YOUTRACK_PROJECT = "GS"
YOUTRACK_PROJECT_ID = "0-1"

-You can use environment variables too

---
# Usage

## Run script
You can run cli.py directly as it has a default structure for execution. 
This allows you to experiment interactively in the console without extra setup.

## Run the CLI tool:

```bash
python src/cli.py --repo owner/repo --project GS --sync --interval 60
```

## Cli arguments:
- --repo: GitHub repository in the format owner/repo

- --project: YouTrack project ID or short name

- --state: Filter issues (open, closed, all)

- --dry-run: Run without creating/updating issues

- --limit: Limit number of issues processed

- --sync: Run in continuous sync mode

- --interval: Interval in seconds for continuous sync

---
# How it works

The tool is designed to automate the synchronization of GitHub issues into YouTrack while preserving important metadata and supporting continuous synchronization.
The process is built in several key steps:


### 1. Fetch Issues

The tool connects to the GitHub API using a personal access token and retrieves issues for the specified repository.
It supports filtering issues by state:

- open: Fetch only open issues

- closed: Fetch only closed issues

- all: Fetch all issues

It also supports limiting the number of issues processed with the --limit argument.

This is handled in the IssueSynchronizer class, which calls the GitHub client (GitHubClient) to fetch issue data in JSON format.

### 2. Map Issues

GitHub and YouTrack have different data structures.
The tool uses the IssueMapper system to transform GitHub issue data into YouTrack issue format.

Mapping is done via strategies:

- SummaryStrategy → Maps issue title to YouTrack summary

- DescriptionStrategy → Converts GitHub issue body into a YouTrack description, adding metadata such as GitHub URL, issue number, and creation date

- StateStrategy → Maps GitHub issue states (open, closed) into YouTrack states (To Do, In Progress, etc.)

- AssigneeStrategy → Maps GitHub assignee to YouTrack assignee, handling differences in user representation and ensuring the user exists in the YouTrack project

This modular design allows easy extension for additional field mapping in the future.

### 3. Check Existing Issues
Before creating a new issue in YouTrack, the tool checks whether an issue with the same summary already exists in the target project.

This avoids creating duplicates.
The check is done by calling YouTrack API through the IssueService and querying issues in the project with matching summaries.


### 4. Create or Update Issues

Depending on the result of the check:

If issue doesn’t exist
A new issue is created in YouTrack with mapped fields such as summary, description, state, assignee, and custom fields (e.g., priority, due date).

If issue exists
The tool compares GitHub and YouTrack versions using the mapping strategies.
If changes are detected, it updates the existing YouTrack issue with the new information.
This ensures that issues stay in sync over time.

Changes and updates are handled in a way that minimizes unnecessary API calls, improving efficiency.


### 5. Manage Project Team and Assignees

The tool automatically ensures that the assignee exists in the target YouTrack project team.

It uses UserService to check if the user exists in YouTrack.

If the assignee is not in the project team, it adds them using ProjectService.

User data is managed to handle differences between GitHub and YouTrack representations.

This guarantees that all assigned issues in GitHub are correctly linked to users in YouTrack.


### 6. Logging

Every step is logged with detailed information for debugging and auditing:

Fetch results

Mapping changes

Issue creation and updates

Errors and exceptions

Project and user operations

Logging helps diagnose synchronization issues and track system activity.


### 7. Continuous Sync

If the --sync flag is enabled, the tool runs in a loop:

It fetches GitHub issues at defined intervals (--interval argument)

Checks for changes and updates YouTrack accordingly

Sleeps for the interval period before repeating

This makes it a robust tool for keeping GitHub and YouTrack issues in sync automatically, without manual intervention.


### 8. Error Handling

The tool is designed with resilience in mind:

Errors in fetching issues, mapping, or API calls are caught and logged without stopping the whole process.

Failures in one issue do not block others.

The system reports failures with clear logs for debugging.


#### 💡 In short: This system is a full-featured GitHub → YouTrack issue synchronizer that handles fetching, mapping, deduplication, creation, updating, user management, and continuous synchronization — all while providing detailed logging for transparency and debugging.

