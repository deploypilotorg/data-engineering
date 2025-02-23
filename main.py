import requests
from bs4 import BeautifulSoup
import time
import json

class GitIngestScraper:
    def __init__(self):
        self.base_url = "https://gitingest.com/haxybaxy/portfolio"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_page(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def parse_repository_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        directory_structure = soup.find('div', id='directory-structure-container')

        if directory_structure:
            return directory_structure.decode_contents()  # This returns the inner HTML as a string
        else:
            print("Directory structure container not found")
            return None

    def scrape(self):
        html = self.fetch_page(self.base_url)
        if html:
            return self.parse_repository_data(html)
        return None

if __name__ == "__main__":
    scraper = GitIngestScraper()
    results = scraper.scrape()

    # Save results to a JSON file
    with open('gitingest_data.json', 'w') as f:
        json.dump(results, f, indent=4)
