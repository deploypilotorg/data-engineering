from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json

class GitIngestScraper:
    def __init__(self):
        self.base_url = "https://gitingest.com/haxybaxy/portfolio"
        self.driver = webdriver.Chrome()

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

if __name__ == "__main__":
    scraper = GitIngestScraper()
    results = scraper.scrape()

    # Save directory structure and textarea content to separate text files
    with open('directory_structure.txt', 'w', encoding='utf-8') as f:
        f.write(results['directory_structure'])

    with open('code_content.txt', 'w', encoding='utf-8') as f:
        f.write(results['textarea_content'])
