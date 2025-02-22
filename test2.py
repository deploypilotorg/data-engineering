import os
import sys
import re
import base64
import csv
import requests
from typing import List, Dict


# 1) Parsing and GitHub helper functions
##

def parse_repo_url(repo_url: str):
    """
    Attempts to parse either a full GitHub URL or 'owner/repo' format,
    returning (owner, repo).
    """
    pattern = r"(?:github\.com[/:])([^/]+)/([^/.]+)"
    match = re.search(pattern, repo_url)
    if match:
        owner = match.group(1)
        repo = match.group(2)
        return owner, repo

    # If "owner/repo" was passed directly
    if "/" in repo_url:
        owner, repo = repo_url.split("/")
        return owner, repo
    
    # If space separated
    if " " in repo_url:
        parts = repo_url.split()
        if len(parts) == 2:
            return parts[0], parts[1]

    raise ValueError("Cannot parse repository URL/identifier.")

def get_github_api(url, token=None, params=None):
    """
    For GitHub API endpoints that return JSON.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    response = requests.get(url, headers=headers, params=params or {})
    response.raise_for_status()
    return response.json()

def get_raw_file_content(download_url, token=None) -> str:
    """
    For direct 'download_url' links that serve raw file data (not JSON).
    Returns the file content as UTF-8 text.
    """
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    resp = requests.get(download_url, headers=headers)
    resp.raise_for_status()
    return resp.text

def save_to_csv(filename, fieldnames, rows):
    """
    Utility function to save rows (list of dicts) into a CSV with the given fieldnames.
    """
    # Ensure directory for the CSV exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def fetch_contents_recursively(owner: str, repo: str, path: str, token=None, all_contents=None):
    """
    Recursively fetches contents of a GitHub repo (folders/files).
    Returns a list of dict items with 'name', 'path', 'type' (file/dir), 'download_url'.
    """
    if all_contents is None:
        all_contents = []

    base_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    if path:
        url = f"{base_url}/{path}"
    else:
        url = base_url  # top-level

    try:
        contents_data = get_github_api(url, token=token)
    except requests.exceptions.HTTPError as e:
        print(f"Error accessing {url}: {e}")
        return all_contents

    if isinstance(contents_data, dict) and contents_data.get("type") == "file":
        # Single file
        all_contents.append({
            "name": contents_data.get("name"),
            "path": contents_data.get("path"),
            "type": "file",
            "download_url": contents_data.get("download_url")
        })
        return all_contents
    elif not isinstance(contents_data, list):
        # If it's not a list, might be an error or special case
        return all_contents

    # It's presumably a directory listing
    for item in contents_data:
        item_type = item.get("type")
        item_name = item.get("name")
        item_path = item.get("path")
        download_url = item.get("download_url")
        all_contents.append({
            "name": item_name,
            "path": item_path,
            "type": item_type,
            "download_url": download_url
        })
        # If directory, recurse
        if item_type == "dir":
            fetch_contents_recursively(owner, repo, item_path, token, all_contents)

    return all_contents

##
# 2) Main script logic
##

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <github_repo_url_or_owner_repo>")
        sys.exit(1)

    repo_input = sys.argv[1]
    try:
        owner, repo = parse_repo_url(repo_input)
    except ValueError as e:
        print(e)
        sys.exit(1)

    # We assume "owner" is the GitHub username from which we'll also fetch public repos
    github_token = "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"
    print(f"Owner (User): {owner}, Target Repo: {repo}")

    # We'll store all CSV files inside "mini-csvs"
    mini_csvs_folder = "mini-csvs"

    ##
    # 2A) Analyze the single target repo
    ##
    # We'll produce the same mini CSVs as before, but now in "mini-csvs"

    # -- Repo Details
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    repo_data = get_github_api(repo_url, token=github_token)
    repository_name = repo_data.get("name")
    repository_owner = repo_data.get("owner", {}).get("login")
    languages_url = repo_data.get("languages_url")
    languages_used = get_github_api(languages_url, token=github_token) if languages_url else {}

    repo_info_rows = [{
        "repository_name": repository_name,
        "repository_owner": repository_owner,
        "languages_used": ", ".join(languages_used.keys()) if languages_used else ""
    }]
    save_to_csv(
        os.path.join(mini_csvs_folder, "repo_details.csv"),
        fieldnames=["repository_name", "repository_owner", "languages_used"],
        rows=repo_info_rows
    )

    """# -- Commits
    commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    commits_data = get_github_api(commits_url, token=github_token)
    commit_rows = []
    for c in commits_data:
        commit_info = c.get("commit", {})
        author_info = commit_info.get("author", {})
        commit_rows.append({
            "sha": c.get("sha"),
            "author_name": author_info.get("name"),
            "author_email": author_info.get("email"),
            "date": author_info.get("date"),
            "message": commit_info.get("message")
        })

    save_to_csv(
        os.path.join(mini_csvs_folder, "commits.csv"),
        fieldnames=["sha", "author_name", "author_email", "date", "message"],
        rows=commit_rows
    )"""

    # -- Branches
    branches_url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    branches_data = get_github_api(branches_url, token=github_token)
    branch_rows = []
    for b in branches_data:
        branch_rows.append({
            "branch_name": b.get("name"),
            "commit_sha": b.get("commit", {}).get("sha")
        })
    save_to_csv(
        os.path.join(mini_csvs_folder, "branches.csv"),
        fieldnames=["branch_name", "commit_sha"],
        rows=branch_rows
    )

    """# -- Tags
    tags_url = f"https://api.github.com/repos/{owner}/{repo}/tags"
    tags_data = get_github_api(tags_url, token=github_token)
    tag_rows = []
    for t in tags_data:
        tag_rows.append({
            "tag_name": t.get("name"),
            "commit_sha": t.get("commit", {}).get("sha")
        })
    save_to_csv(
        os.path.join(mini_csvs_folder, "tags.csv"),
        fieldnames=["tag_name", "commit_sha"],
        rows=tag_rows
    )
"""
    """# -- Pull Requests (open and closed)
    pulls_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    pulls_data = get_github_api(pulls_url, token=github_token, params={"state": "all"})
    pull_rows = []
    for pr in pulls_data:
        pull_rows.append({
            "pr_number": pr.get("number"),
            "title": pr.get("title"),
            "state": pr.get("state"),
            "created_at": pr.get("created_at"),
            "merged_at": pr.get("merged_at"),
            "user_login": pr.get("user", {}).get("login"),
            "body": pr.get("body")
        })
    save_to_csv(
        os.path.join(mini_csvs_folder, "pull_requests.csv"),
        fieldnames=["pr_number", "title", "state", "created_at", "merged_at", "user_login", "body"],
        rows=pull_rows
    )"""

    # -- Collaborators
    collaborators_url = f"https://api.github.com/repos/{owner}/{repo}/collaborators"
    try:
        collaborators_data = get_github_api(collaborators_url, token=github_token)
        collaborator_rows = []
        for col in collaborators_data:
            collaborator_rows.append({
                "login": col.get("login"),
                "id": col.get("id"),
                "permissions": col.get("permissions")
            })
        save_to_csv(
            os.path.join(mini_csvs_folder, "collaborators.csv"),
            fieldnames=["login", "id", "permissions"],
            rows=collaborator_rows
        )
    except requests.exceptions.HTTPError as e:
        print(f"Error retrieving collaborators: {e}")

    # -- Contributors
    contributors_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    try:
        contributors_data = get_github_api(contributors_url, token=github_token)
        contributor_rows = []
        for contrib in contributors_data:
            contributor_rows.append({
                "login": contrib.get("login"),
                "contributions": contrib.get("contributions")
            })
        save_to_csv(
            os.path.join(mini_csvs_folder, "contributors.csv"),
            fieldnames=["login", "contributions"],
            rows=contributor_rows
        )
    except requests.exceptions.HTTPError as e:
        print(f"Error retrieving contributors: {e}")

    # -- Recursively Retrieve All Repository Contents
    all_contents = fetch_contents_recursively(owner, repo, "", github_token)
    content_rows = []
    for item in all_contents:
        content_rows.append({
            "name": item["name"],
            "path": item["path"],
            "type": item["type"],
        })
    save_to_csv(
        os.path.join(mini_csvs_folder, "repository_contents.csv"),
        fieldnames=["name", "path", "type"],
        rows=content_rows
    )

    # -- Identify known dependency or framework files
    known_framework_files = [
        "package.json", "requirements.txt", "Gemfile", "Pipfile",
        "pyproject.toml", "composer.json", "build.gradle",
        "pom.xml", "Cargo.toml"
    ]
    frameworks_found = []
    dependencies_found = []

    # -- Identify CI/CD file extensions
    cicd_extensions = [".yml", ".yaml", ".bicep"]
    cloud_services = ["azure", "aws", "gcp"]  # naive substring approach
    cicd_rows = []
    found_services_rows = []

    for item in all_contents:
        if item["type"] == "file":
            filename = item["name"]
            download_url = item.get("download_url", "")
            extension = os.path.splitext(filename)[1].lower()

            # Check for framework/dependency file
            if filename in known_framework_files:
                frameworks_found.append(filename)
                try:
                    file_text = get_raw_file_content(download_url, github_token)
                    dependencies_found.append(
                        f"In {filename}: {file_text[:100]}..."
                    )
                except Exception as ex:
                    print(f"Could not read {filename}: {ex}")

            # Check for CI/CD file
            if extension in cicd_extensions:
                cicd_rows.append({
                    "workflow_file": filename,
                    "path": item["path"]
                })
                try:
                    file_text = get_raw_file_content(download_url, github_token).lower()
                    found_services = []
                    for srv in cloud_services:
                        if srv in file_text:
                            found_services.append(srv.capitalize())
                    if found_services:
                        found_services_rows.append({
                            "file": item["path"],
                            "services_detected": ", ".join(found_services)
                        })
                except Exception as ex:
                    print(f"Error reading CI/CD file {filename}: {ex}")

    # Save frameworks & dependencies
    fw_rows = [{"framework_file": fw} for fw in frameworks_found]
    save_to_csv(
        os.path.join(mini_csvs_folder, "frameworks.csv"),
        fieldnames=["framework_file"],
        rows=fw_rows
    )

    deps_rows = [{"dependencies_info": dep} for dep in dependencies_found]
    save_to_csv(
        os.path.join(mini_csvs_folder, "dependencies.csv"),
        fieldnames=["dependencies_info"],
        rows=deps_rows
    )

    # Save the discovered CI/CD files
    if cicd_rows:
        save_to_csv(
            os.path.join(mini_csvs_folder, "cicd_workflows.csv"),
            fieldnames=["workflow_file", "path"],
            rows=cicd_rows
        )
    else:
        print("No CI/CD workflow files found in the target repository.")

    if found_services_rows:
        save_to_csv(
            os.path.join(mini_csvs_folder, "cicd_services.csv"),
            fieldnames=["file", "services_detected"],
            rows=found_services_rows
        )

    # -- README.md
    readme_url = f"https://api.github.com/repos/{owner}/{repo}/contents/README.md"
    try:
        readme_data = get_github_api(readme_url, token=github_token)
        readme_content_encoded = readme_data.get("content")
        readme_content = base64.b64decode(readme_content_encoded).decode("utf-8") if readme_content_encoded else ""
        readme_rows = [{"readme": readme_content}]
        save_to_csv(
            os.path.join(mini_csvs_folder, "readme.csv"),
            fieldnames=["readme"],
            rows=readme_rows
        )
    except requests.exceptions.HTTPError as e:
        print(f"No README.md found or not accessible: {e}")

    print("Single-repo analysis completed. Mini CSV files are in 'mini-csvs'.")

    ##
    # 2B) Fetch all public repos of the user and see what CI/CD services they use
    ##
    # We'll do a simpler approach: for each repo, we search for CI/CD references (Azure, AWS, GCP)
    # Then we keep a global counter across all public repos.
    service_counts = {
        "Azure": 0,
        "AWS": 0,
        "GCP": 0
    }

    # GitHub endpoint for user’s public repos:
    # GET /users/{username}/repos
    # We might need pagination if there are >100 repos, but let's do a naive approach
    user_repos_url = f"https://api.github.com/users/{owner}/repos"
    try:
        user_repos_data = get_github_api(user_repos_url, token=github_token, params={"per_page": 100})
        # If the user has more than 100 repos, consider adding pagination
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching user repos for '{owner}': {e}")
        user_repos_data = []

    # For each repo, recursively scan for files with .yml, .yaml, .bicep, then increment counters
    for user_repo in user_repos_data:
        if user_repo.get("private") == True:
            # skip private repos
            continue
        rname = user_repo["name"]
        rowner = user_repo["owner"]["login"]
        # fetch contents recursively
        contents = fetch_contents_recursively(rowner, rname, "", github_token)
        for item in contents:
            if item["type"] == "file":
                fname = item["name"].lower()
                extension = os.path.splitext(fname)[1]
                if extension in [".yml", ".yaml", ".bicep"]:
                    # naive substring approach
                    try:
                        file_txt = get_raw_file_content(item["download_url"], github_token).lower()
                        if "azure" in file_txt:
                            service_counts["Azure"] += 1
                        if "aws" in file_txt:
                            service_counts["AWS"] += 1
                        if "gcp" in file_txt:
                            service_counts["GCP"] += 1
                    except Exception as ex:
                        print(f"Error reading file in {rowner}/{rname}: {ex}")

    # Now write service_counts to a single CSV
    sc_rows = []
    for service, count in service_counts.items():
        sc_rows.append({"service": service, "count": count})

    user_services_csv = os.path.join(mini_csvs_folder, "user_ci_cd_services_summary.csv")
    save_to_csv(
        user_services_csv,
        fieldnames=["service", "count"],
        rows=sc_rows
    )
    print(f"User's public repo CI/CD services summarized in '{user_services_csv}'.")

    ##
    # 2C) Combine all mini CSVs into one CSV
    ##
    combined_csv = "all_data_combined.csv"
    combine_csvs_into_one(mini_csvs_folder, combined_csv)
    print(f"All mini CSV data combined into '{combined_csv}'.")

##
# 3) Combine all CSV files into one
##

def combine_csvs_into_one(folder_path: str, output_csv: str):
    """
    Gathers all CSV files within the given folder and merges them
    into a single CSV with columns:
      - source_csv
      - row_index
      - column_name
      - value
    This ensures we capture all data from all CSV files in a simple, consistent format.
    """
    os.makedirs(os.path.dirname(output_csv) or ".", exist_ok=True)
    fieldnames = ["source_csv", "row_index", "column_name", "value"]

    with open(output_csv, mode="w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=fieldnames)
        writer.writeheader()

        # List all files in folder
        for fname in os.listdir(folder_path):
            if not fname.lower().endswith(".csv"):
                continue
            csv_path = os.path.join(folder_path, fname)
            with open(csv_path, mode="r", encoding="utf-8") as in_f:
                reader = csv.DictReader(in_f)
                row_index = 0
                for row in reader:
                    for col in reader.fieldnames:
                        writer.writerow({
                            "source_csv": fname,
                            "row_index": row_index,
                            "column_name": col,
                            "value": row[col]
                        })
                    row_index += 1

if __name__ == "__main__":
    main()
