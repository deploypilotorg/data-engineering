# GitHub Repo & User CI/CD Analyzer

## Overview
This script performs a comprehensive analysis of:

1. A single target GitHub repository, extracting data such as commits, branches, tags, CI/CD configurations, frameworks, and more.
2. All public repositories belonging to the same user, aggregating CI/CD services (Azure, AWS, GCP) used across their repositories.

## Features

### Repository Analysis
Retrieves and stores:
- **Basic Repository Details**: Owner, name, primary languages.
- **Commits**: SHA, author info, date, commit message.
- **Branches**: Name, latest commit.
- **Tags**: Name, commit reference.
- **Pull Requests**: Open and closed PRs.
- **Collaborators & Contributors**.
- **Framework / Dependency Files**: Extracts files like `package.json`, `requirements.txt`, etc.
- **CI/CD Configurations**: Detects `.yml`, `.yaml`, and `.bicep` files.
- **README.md Content**.

Each category is stored in its own CSV file inside the `mini-csvs/` folder.

### User Public Repo CI/CD Summaries
- Retrieves all public repositories for the owner of the target repository.
- Scans each repository for CI/CD files (`.yml`, `.yaml`, `.bicep`).
- Detects mentions of **Azure**, **AWS**, or **GCP** in those files.
- Aggregates a count of how often each cloud provider is referenced.
- Stores the summary in `mini-csvs/user_ci_cd_services_summary.csv`.

### Unified CSV Output
- Merges all CSV files from `mini-csvs/` into a single consolidated file: `all_data_combined.csv`.
- Standardized row structure:
  - `source_csv`: Originating CSV file.
  - `row_index`: Row number in the original file.
  - `column_name`: Field name in the original CSV.
  - `value`: Cell content.

## Requirements
- **Python 3.7+**
- **Requests library** (for GitHub API calls)
- **Bash** (for running commands)

Install dependencies with:
```bash
pip install requests
```

### (Optional) GitHub Personal Access Token
To analyze private repositories or bypass API rate limits, set up a personal access token:
```bash
export GITHUB_TOKEN="ghp_XXXXXXXXXXXXXXXXXXXXXXXX"
```

## Usage

1. **Clone or download** this repository.
2. **Install dependencies** (`requests`).
3. **Run the script**, specifying the target repository:

```bash
python script.py <github_repo_url_or_owner/repo>
```

### Examples:
```bash
python script.py https://github.com/octocat/Hello-World
python script.py octocat/Hello-World
```

## Script Workflow

1. **Initial Input:** You provide a GitHub repository reference (owner/repo or full URL).
2. **Single-Repo Analysis:**
   - Fetches repository details via the GitHub API (v3).
   - Saves extracted data as CSV files (`commits.csv`, `branches.csv`, `tags.csv`, etc.) inside `mini-csvs/`.
3. **User Public Repo Analysis:**
   - Identifies the GitHub user who owns the target repository.
   - Retrieves all their public repositories.
   - Scans each repo for `.yml`, `.yaml`, and `.bicep` files.
   - Checks for mentions of "azure", "aws", or "gcp".
   - Stores aggregated CI/CD usage in `mini-csvs/user_ci_cd_services_summary.csv`.
4. **Data Consolidation:**
   - Merges all `mini-csvs/` CSV files into `all_data_combined.csv`.
   - Standardized format for easier analysis.

## Output Files
The script generates:

- **`mini-csvs/` folder** containing:
  - `repo_details.csv`, `commits.csv`, `branches.csv`, `tags.csv`, `pull_requests.csv`, etc.
  - `user_ci_cd_services_summary.csv` (counts of Azure, AWS, and GCP references across public repos).
- **`all_data_combined.csv`**: A merged file consolidating all extracted data.

