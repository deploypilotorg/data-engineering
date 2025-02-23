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
        directory_structure = soup.find('div', id='directory-structure-container')

        if directory_structure:
            return directory_structure.decode_contents()
        else:
            print("Directory structure container not found")
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

    # Save results to a JSON file
    with open('gitingest_data.json', 'w') as f:
        json.dump(results, f, indent=4)
