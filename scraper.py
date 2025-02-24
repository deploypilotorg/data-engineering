from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import sys
import argparse
import os

class GitIngestScraper:
    def __init__(self, owner_repo):
        self.base_url = f"https://gitingest.com/{owner_repo}"
        self.driver = webdriver.Chrome()
        # Add a list of file extensions to skip
        self.skip_extensions = ['.css', '.map', '.svg', '.ico', '.gltf']

    def fetch_page(self, url):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "directory-structure-container"))
            )
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
            return self.driver.page_source
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None

    def parse_repository_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # Get directory structure
        directory_structure = soup.find('input', {'id': 'directory-structure-content'})
        # Get the second textarea content
        textarea_content = soup.find_all('textarea')[1]  # Using index 1 to get the second textarea

        result = {
            'directory_structure': directory_structure.get('value') if directory_structure else None,
            'textarea_content': textarea_content.text if textarea_content else None
        }

        if not directory_structure or not textarea_content:
            print("Some content was not found")

        return result

    def scrape(self):
        html = self.fetch_page(self.base_url)
        if html:
            return self.parse_repository_data(html)
        return None

    def __del__(self):
        # Clean up the browser when done
        if hasattr(self, 'driver'):
            self.driver.quit()

    def filter_css_content(self, content):
        lines = content.split('\n')
        filtered_lines = []
        skip_mode = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check for header
            if line.startswith('=' * 48):
                if i + 1 < len(lines):  # Check if next line exists
                    file_line = lines[i + 1]
                    if file_line.startswith('File:'):
                        # Check if file ends with any of the skip extensions
                        should_skip = any(file_line.endswith(ext) for ext in self.skip_extensions)
                        skip_mode = should_skip
                        # Add the header lines
                        filtered_lines.append(line)
                        filtered_lines.append(file_line)
                        filtered_lines.append(lines[i + 2])  # Add the closing '=' line
                        i += 2  # Skip the next two lines as we've handled them
            elif not skip_mode:
                filtered_lines.append(line)
            i += 1

        return '\n'.join(filtered_lines)

if __name__ == "__main__":
    # Create temp directory if it doesn't exist
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)

    parser = argparse.ArgumentParser(description='Scrape repository data from GitIngest')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('repo', nargs='?', help='Single repository in format owner/repo')
    group.add_argument('-f', '--file', help='File containing owner/repo entries, one per line')

    args = parser.parse_args()

    if args.file:
        # Read repositories from file
        try:
            with open(args.file, 'r') as f:
                repos = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            sys.exit(1)
    else:
        repos = [args.repo]

    for repo in repos:
        print(f"Processing repository: {repo}")
        scraper = GitIngestScraper(repo)
        results = scraper.scrape()

        if not results:
            print(f"Failed to fetch repository data for {repo}")
            continue

        # Create repo-specific filenames with temp directory
        base_filename = os.path.join(output_dir, repo.replace('/', '_'))

        # Save directory structure
        with open(f'{base_filename}_directory_structure.txt', 'w', encoding='utf-8') as f:
            f.write(results['directory_structure'])

        # Save filtered code content
        with open(f'{base_filename}_code_content.txt', 'w', encoding='utf-8') as f:
            filtered_content = scraper.filter_css_content(results['textarea_content'])
            f.write(filtered_content)

        print(f"Completed processing {repo}")
