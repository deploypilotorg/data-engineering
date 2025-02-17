def detect_frameworks(deps_text):
    """
    Detect frameworks from dependencies text.
    """
    frameworks = []
    lower_deps = deps_text.lower()
    
    # Framework detection
    if 'flask' in lower_deps:
        frameworks.append('Flask')
    if 'sqlalchemy' in lower_deps:
        frameworks.append('SQLAlchemy')
    if 'django' in lower_deps:
        frameworks.append('Django')
    if 'fastapi' in lower_deps:
        frameworks.append('FastAPI')
    if 'pytest' in lower_deps:
        frameworks.append('Pytest')
        
    return frameworks

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and engineer features from the combined CSV data.
    """
    repo_features = {}
    
    # 1. Basic Repo Info
    repo_details = df[df["source_csv"] == "repo_details.csv"]
    repo_features["repository_name"] = repo_details[repo_details["column_name"] == "repository_name"]["value"].iloc[0]
    repo_features["repository_owner"] = repo_details[repo_details["column_name"] == "repository_owner"]["value"].iloc[0]
    repo_features["languages_used"] = repo_details[repo_details["column_name"] == "languages_used"]["value"].iloc[0]

    # 2. Count Features
    repo_features["num_branches"] = df[df["source_csv"] == "branches.csv"]["row_index"].nunique()
    repo_features["num_contributors"] = df[df["source_csv"] == "contributors.csv"]["row_index"].nunique()
    repo_features["num_collaborators"] = df[df["source_csv"] == "collaborators.csv"]["row_index"].nunique()

    # 3. CI/CD Features
    cicd_services = df[df["source_csv"] == "cicd_services.csv"]
    if "services_detected" in cicd_services.columns:
        cicd_services = cicd_services["services_detected"].tolist()
        repo_features["has_ci_cd"] = 1 if cicd_services else 0
        repo_features["detected_services"] = ", ".join(cicd_services) if cicd_services else "None"
    else:
        repo_features["has_ci_cd"] = 0
        repo_features["detected_services"] = "None"

    # 4. Dependency Features
    dependencies = df[df["source_csv"] == "dependencies.csv"]["value"].tolist()
    repo_features["dependencies"] = ", ".join(dependencies) if dependencies else "None"

    # Enhanced framework detection
    frameworks = detect_frameworks(repo_features["dependencies"])
    repo_features["detected_frameworks"] = ", ".join(frameworks) if frameworks else "None"
    repo_features["has_web_framework"] = any(f in ['Flask', 'Django', 'FastAPI'] for f in frameworks)

    # Analyze dependencies more deeply
    repo_features["has_database"] = any(d for d in dependencies if "sql" in d.lower() or "mongo" in d.lower() or "postgresql" in d.lower())

    # Repository complexity indicators
    repo_contents = df[df["source_csv"] == "repository_contents.csv"]
    repo_features["has_docker"] = any("Dockerfile" in str(value) for value in repo_contents["value"])
    repo_features["has_tests"] = any("test" in str(value).lower() for value in repo_contents["value"])

    # 5. README Features
    readme_text = df[df["source_csv"] == "readme.csv"]["value"].iloc[0] if "readme.csv" in df["source_csv"].unique() else ""
    repo_features["readme_length"] = len(readme_text)
    repo_features["readme_keywords"] = " ".join(re.findall(r"\b\w{4,}\b", readme_text.lower()))  # Extract keywords

    # Add repository size/activity metrics
    repo_features["num_commits"] = df[df["source_csv"] == "commits.csv"]["row_index"].nunique()
    repo_features["num_pull_requests"] = df[df["source_csv"] == "pull_requests.csv"]["row_index"].nunique()

    return pd.DataFrame([repo_features])