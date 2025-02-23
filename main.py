from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json

class GitIngestScraper:
    def __init__(self):
        self.base_url = "https://gitingest.com/haxybaxy/portfolio"
        # Initialize Chrome driver (you'll need to have chromedriver installed)
        self.driver = webdriver.Chrome()

    def fetch_page(self, url):
        try:
            self.driver.get(url)
            # Wait up to 10 seconds for the element to be present
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "directory-structure-container"))
            )
            return self.driver.page_source
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None

    def parse_repository_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # Find the hidden input that contains the raw directory structure
        directory_structure = soup.find('input', {'id': 'directory-structure-content'})

        if directory_structure:
            # Get the value attribute which contains the properly formatted tree
            return directory_structure.get('value')
        else:
            print("Directory structure content not found")
            return None

    def scrape(self):
        html = self.fetch_page(self.base_url)
        if html:
            return self.parse_repository_data(html)
        return None

    def __del__(self):
        # Clean up the browser when done
        if hasattr(self, 'driver'):
            self.driver.quit()

if __name__ == "__main__":
    scraper = GitIngestScraper()
    results = scraper.scrape()

    # Save results to a JSON file, ensuring proper encoding
    with open('gitingest_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
