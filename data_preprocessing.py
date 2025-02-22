import os
import pandas as pd
import json
import logging
import sys
from collections import defaultdict

# Set up logging
logging.basicConfig(
    filename="preprocessing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def clean_and_filter_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the dataset by removing irrelevant columns, handling missing values,
    and keeping only important features for ML processing.
    """
    
    # Drop irrelevant sources
    irrelevant_sources = {"commits.csv", "pull_requests.csv", "repo_details.csv", "contributors.csv", "branches.csv"}
    df = df[~df["source_csv"].isin(irrelevant_sources)]
    
    # Handle missing values
    df["value"].fillna("unknown", inplace=True)
    
    # Standardize text fields
    df["value"] = df["value"].astype(str).str.strip().str.lower()
    
    return df

def extract_features(df: pd.DataFrame) -> dict:
    """
    Extracts relevant repository features dynamically and structures them in an optimized JSON format.
    """
    repo_entry = {
        "codebase": {"files": set(), "dependencies": [], "frameworks": set()},
        "deployment": {"ci_cd": {"workflows": set(), "detected_services": set()}, "cloud_providers": defaultdict(int)}
    }
    
    for source, subset in df.groupby("source_csv"):
        for column, values in subset.groupby("column_name"):
            value_list = values["value"].dropna().tolist()
            
            # Handle codebase
            if source == "repository_contents.csv":
                repo_entry["codebase"]["files"].update(value_list)
            elif source == "dependencies.csv":
                for value in value_list:
                    try:
                        dep_dict = json.loads(value)
                        repo_entry["codebase"]["dependencies"].extend(
                            [{"name": k, "version": v} for k, v in dep_dict.items()]
                        )
                    except json.JSONDecodeError:
                        # Handle the case where the value is not a valid JSON
                        dep_info = value.split(":")
                        if len(dep_info) == 2:
                            repo_entry["codebase"]["dependencies"].append({"name": dep_info[0].strip(), "version": dep_info[1].strip()})
                        else:
                            repo_entry["codebase"]["dependencies"].append({"name": value, "version": "unknown"})
            elif source == "frameworks.csv":
                repo_entry["codebase"]["frameworks"].update(value_list)
            
            # Handle deployment
            elif source == "cicd_workflows.csv":
                repo_entry["deployment"]["ci_cd"]["workflows"].update(value_list)
            elif source == "cicd_services.csv":
                for value in value_list:
                    if value.endswith(".yml"):
                        repo_entry["deployment"]["ci_cd"]["workflows"].add(value)
                    else:
                        repo_entry["deployment"]["ci_cd"]["detected_services"].add(value)
            elif source == "user_ci_cd_services_summary.csv":
                for val in value_list:
                    if val.isdigit():
                        repo_entry["deployment"]["cloud_providers"][column] = int(val)
                    else:
                        repo_entry["deployment"]["cloud_providers"][val] += 1
    
    # Convert sets back to lists for JSON serialization
    repo_entry["codebase"]["files"] = sorted(repo_entry["codebase"]["files"])
    repo_entry["codebase"]["frameworks"] = sorted(repo_entry["codebase"]["frameworks"])
    repo_entry["deployment"]["ci_cd"]["workflows"] = sorted(repo_entry["deployment"]["ci_cd"]["workflows"])
    repo_entry["deployment"]["ci_cd"]["detected_services"] = sorted(repo_entry["deployment"]["ci_cd"]["detected_services"])
    
    # Fix cloud provider counts
    repo_entry["deployment"]["cloud_providers"] = dict(repo_entry["deployment"]["cloud_providers"])
    
    return repo_entry

def feature_engineering(data: dict) -> dict:
    """
    Performs feature engineering on the extracted data to identify specific requirements and characteristics.
    """
    features = {
        "needs_database": False,
        "needs_cache": False,
        "uses_docker": False,
        "uses_nodejs": False,
        "uses_python": False,
        "uses_redis": False,
        "uses_ci_cd": False,
        "cloud_providers": []
    }
    
    # Analyze files
    files = data["codebase"]["files"]
    for file in files:
        if file.endswith(".sql"):
            features["needs_database"] = True
        if file.endswith(".cache"):
            features["needs_cache"] = True
        if file.lower() == "dockerfile":
            features["uses_docker"] = True
        if file.lower() == "package.json":
            features["uses_nodejs"] = True
        if file.lower() == "requirements.txt" or file.lower() == "pipfile":
            features["uses_python"] = True
    
    # Analyze dependencies
    dependencies = data["codebase"]["dependencies"]
    for dep in dependencies:
        if dep["name"] == "redis":
            features["uses_redis"] = True
    
    # Analyze CI/CD workflows
    if data["deployment"]["ci_cd"]["workflows"]:
        features["uses_ci_cd"] = True
    
    # Analyze cloud providers
    features["cloud_providers"] = list(data["deployment"]["cloud_providers"].keys())
    
    return features

def save_csv(data: dict, output_path: str):
    """
    Saves extracted repository data to a CSV file.
    """
    flattened_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                flattened_data[f"{key}_{sub_key}"] = json.dumps(sub_value)
        else:
            flattened_data[key] = json.dumps(value)
    
    df = pd.DataFrame([flattened_data])
    df.to_csv(output_path, index=False, encoding="utf-8")

def main():
    input_csv = "../Data-retrieval/all_data_combined.csv"
    output_csv = "processed_data.csv"
    
    try:
        df = pd.read_csv(input_csv)
        logging.info(f"Successfully loaded data from {input_csv}")
    except FileNotFoundError:
        logging.error(f"Error: File '{input_csv}' not found.")
        sys.exit(1)
    
    cleaned_df = clean_and_filter_data(df)
    extracted_data = extract_features(cleaned_df)
    engineered_features = feature_engineering(extracted_data)
    
    # Combine extracted data and engineered features
    combined_data = {**extracted_data, **engineered_features}
    
    save_csv(combined_data, output_csv)
    
    logging.info(f"Processed data saved to {output_csv}")
    print(f"Processing complete. Data saved to {output_csv}")

if __name__ == "__main__":
    main()
