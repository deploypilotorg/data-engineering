# GitHub Repo & User CI/CD Analyzer

## Overview
This repository contains a Python script that analyzes GitHub repositories and their CI/CD configurations. It scrapes data from specified repositories and generates detailed analysis reports.

## Features

### Repository Scraping
- Scrapes repository data from GitIngest, including:
  - Directory structure
  - Code content
- Supports scraping multiple repositories from a file or a single repository.

### Analysis
- Analyzes the scraped data to determine:
  - Deployment platforms (e.g., AWS, Vercel, Firebase)
  - Infrastructure features (e.g., CI/CD, containerization)
  - Code features (e.g., authentication, database usage)

### Output
- Generates CSV files containing:
  - Analysis results for each repository.
  - Detailed infrastructure and code analysis.

## Requirements
- **Python 3.7+**
- **Selenium** for web scraping.
- **BeautifulSoup** for HTML parsing.
- **OpenAI API** for advanced code analysis.

Install dependencies with:
```bash
pip install -r requirements.txt
```

### (Optional) OpenAI API Key
To enable advanced code analysis, set up an OpenAI API key:


## Usage

1. **Clone or download** this repository.
2. **Install dependencies**.
3. **Run the script**, specifying the input file containing repository names:

```bash
python main.py repos.txt
```

### Example Input File (`repos.txt`):

haxybaxy/portfolio | Vercel
IsraelChidera/focus-app | Firebase
jitsi/jitsi-meet | Vercelhaxybaxy/portfolio | Vercel
IsraelChidera/focus-app | Firebase
jitsi/jitsi-meet | Vercel

## Script Workflow

1. **Scraping Phase**:
   - The script reads repository names from the input file.
   - It scrapes data for each repository using the `GitIngestScraper` class.

2. **Analysis Phase**:
   - The script analyzes the scraped data using the `FeatureAnalyzer` class.
   - It determines the deployment platform and identifies key features.

3. **Output Generation**:
   - The results are saved in a temporary directory as CSV files.
   - A summary of the analysis is printed to the console.

## Output Files
The script generates:
- **CSV files** in the `temp` directory containing:
  - `analysis_results.csv`: Analysis results for each repository.
- **JSON files** with detailed analysis results for each repository.

## Contributing
Feel free to submit issues or pull requests to improve the functionality of this analyzer.





