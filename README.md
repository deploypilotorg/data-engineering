GitHub Repo & User CI/CD Analyzer
This script performs a comprehensive analysis of:

A single target GitHub repository (pulling data like commits, branches, tags, CI/CD files, frameworks, etc.).
All public repositories belonging to the same user to detect and aggregate which CI/CD services (Azure, AWS, GCP) have been used across their repos.
Features
Repository Analysis

Retrieves:
Basic repository details (owner, name, languages)
Commits (SHA, author info, date, message)
Branches (name, latest commit)
Tags (name, commit)
Pull Requests (open & closed)
Collaborators & Contributors
Framework / Dependency files (e.g., package.json, requirements.txt, etc.)
CI/CD configurations (.yml, .yaml, .bicep)
README.md content
Stores each category in its own CSV file within a mini-csvs/ folder.
User Public Repo CI/CD Summaries

Looks up all public repos for the user (the same user/owner of the target repo).
Recursively scans each repo for CI/CD files (.yml, .yaml, .bicep).
Naively checks if the file references azure, aws, or gcp.
Aggregates a total count of how many times each cloud service is referenced.
Stores this summary in mini-csvs/user_ci_cd_services_summary.csv.
Unified CSV

Finally merges all the CSV files in the mini-csvs/ folder into a single CSV file called all_data_combined.csv, which organizes the data in a standardized row structure:
source_csv - which mini CSV file the row came from
row_index - row number in the original file
column_name - field name in the original CSV
value - cell content
Requirements
Python 3.7+ (or higher)
Requests library (for HTTP calls)
bash
Copy
Edit
pip install requests
(Optional) GitHub Personal Access Token
If you’re analyzing private repos or want to avoid rate limits, export your token:
bash
Copy
Edit
export GITHUB_TOKEN="ghp_XXXXXXXXXXXXXXXXXXXXXXXX"
How to Use
Clone or Download this repository/script.
Install Dependencies (e.g., requests).
Run the script from your command line, passing in the target repo:
bash
Copy
Edit
python script.py <github_repo_url_or_owner/repo>
Examples:
bash
Copy
Edit
python script.py https://github.com/octocat/Hello-World
python script.py octocat/Hello-World
Explanation of the Script Flow
Initial Input: You provide a single GitHub repo reference (owner/repo or full URL).
Single-Repo Analysis:
The script calls the GitHub API (v3) to gather details about that repo.
Writes CSVs (e.g., commits.csv, branches.csv, tags.csv, etc.) into mini-csvs/.
User Public Repo Analysis:
Identifies the GitHub user (the owner) of the target repo.
Fetches a list of all their public repositories.
For each public repo, recursively scans for files with .yml, .yaml, or .bicep extensions and does a naive substring check for "azure", "aws", "gcp".
Totals up the usage counts for each service across all those repos, storing the results in mini-csvs/user_ci_cd_services_summary.csv.
Data Consolidation:
All CSV files in mini-csvs/ are read and merged into all_data_combined.csv.
This single CSV has four columns:
source_csv (which mini-CSV file the row came from)
row_index (the row number in that CSV)
column_name
value
Output Files
The script automatically creates:

mini-csvs/ folder, containing multiple CSVs:
repo_details.csv, commits.csv, branches.csv, tags.csv, pull_requests.csv, etc.
user_ci_cd_services_summary.csv (counts of Azure, AWS, and GCP across all public repos).
all_data_combined.csv in the script’s directory, combining all those files into a single CSV.
Potential Improvements
Pagination: If a user has more than 100 repos or a repo has >100 commits, you’ll need pagination to retrieve all data.
Structured Parsing: For .yml/.yaml files, a structured parse (e.g. using PyYAML) can reduce false positives.
Terraform / Bicep: Similarly, specialized parsing libraries can detect providers more accurately.
Permissions: Collaborators, private repos, or advanced data requires a valid GitHub Personal Access Token.
