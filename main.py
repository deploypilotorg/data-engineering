import csv
import os
import sys
import argparse
from scraper import GitIngestScraper
from feature_analyzer import FeatureAnalyzer

def process_repositories(input_file):
    # Create temp directory if it doesn't exist
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)

    # Read repositories from file
    with open(input_file, 'r') as f:
        repos = [line.strip() for line in f if line.strip()]

    # Initialize CSV headers
    infrastructure_features = [
        "already_deployed", "has_frontend", "has_cicd",
        "multiple_environments", "uses_containerization",
        "uses_iac", "high_availability"
    ]

    code_features = [
        "authentication", "realtime_events", "storage",
        "caching", "ai_implementation", "database",
        "microservices", "monolith", "api_exposed",
        "message_queues", "background_jobs",
        "sensitive_data", "external_apis"
    ]

    csv_headers = ["repository"] + infrastructure_features + code_features

    # Create CSV file
    csv_path = os.path.join(output_dir, "analysis_results.csv")
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()

        # Process each repository
        for repo in repos:
            print(f"\n=== Processing {repo} ===")
            row_data = {"repository": repo}

            try:
                # Step 1: Scrape repository
                print(f"Scraping repository...")
                scraper = GitIngestScraper(repo)
                results = scraper.scrape()

                if not results:
                    print(f"Failed to fetch data for {repo}")
                    continue

                # Save scraped data
                base_filename = os.path.join(output_dir, repo.replace('/', '_'))
                with open(f'{base_filename}_directory_structure.txt', 'w', encoding='utf-8') as f:
                    f.write(results['directory_structure'])
                with open(f'{base_filename}_code_content.txt', 'w', encoding='utf-8') as f:
                    filtered_content = scraper.filter_css_content(results['textarea_content'])
                    f.write(filtered_content)

                # Step 2: Analyze repository
                print(f"Analyzing repository...")
                analyzer = FeatureAnalyzer()
                dir_results = analyzer.analyze_directory_structure(results['directory_structure'])
                code_results = analyzer.analyze_with_llm(filtered_content)

                # Add infrastructure features to row
                for feature in infrastructure_features:
                    row_data[feature] = "Yes" if dir_results.get(feature, False) else "No"

                # Add code features to row
                for feature in code_features:
                    row_data[feature] = "Yes" if code_results.get(feature, {}).get("present", False) else "No"

                # Write row to CSV
                writer.writerow(row_data)
                print(f"Added results for {repo} to CSV")

            except Exception as e:
                print(f"Error processing {repo}: {str(e)}")
                continue

            finally:
                if 'scraper' in locals():
                    del scraper  # Ensure browser is closed

    print(f"\nAnalysis complete! Results saved to {csv_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze multiple repositories and generate CSV report')
    parser.add_argument('input_file', help='Text file containing owner/repo entries, one per line')
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        sys.exit(1)

    process_repositories(args.input_file)
