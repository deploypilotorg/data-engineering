import os
import pandas as pd
import json
import logging
import sys

# Set up logging
logging.basicConfig(filename="preprocessing.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_features(df: pd.DataFrame) -> dict:
    """
    Extracts all relevant repository features dynamically and structures them in JSON format.
    """
    repositories = {}
    
    grouped = df.groupby("row_index")
    for repo_id, group in grouped:
        repo_entry = {}
        
        for source in group["source_csv"].unique():
            subset = group[group["source_csv"] == source]
            source_data = {}
            
            for column in subset["column_name"].unique():
                values = subset[subset["column_name"] == column]["value"].dropna().tolist()
                
                # Store lists for categorical fields, counts for numerical ones
                if len(values) == 1:
                    source_data[column] = values[0]
                else:
                    source_data[column] = values
            
            repo_entry[source.replace(".csv", "")] = source_data
        
        repositories[str(repo_id)] = repo_entry
    
    return repositories

def save_json(data: dict, output_path: str):
    """
    Saves extracted repository data to a JSON file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def main():
    input_csv = "../Data-retrieval/all_data_combined.csv"
    output_json = "processed_data.json"
    
    try:
        df = pd.read_csv(input_csv)
        logging.info(f"Successfully loaded data from {input_csv}")
    except FileNotFoundError:
        logging.error(f"Error: File '{input_csv}' not found.")
        sys.exit(1)
    
    processed_data = extract_features(df)
    save_json(processed_data, output_json)
    
    logging.info(f"Processed data saved to {output_json}")
    print(f"Processing complete. Data saved to {output_json}")

if __name__ == "__main__":
    main()
