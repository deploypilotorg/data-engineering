# GitHub Repository & CI/CD Analysis Tool

## 🚀 Overview

Welcome to our GitHub Repository & CI/CD Analysis Tool! This powerful Python-based solution helps you analyze GitHub repositories and their CI/CD configurations with ease. Whether you're a developer, DevOps engineer, or tech lead, this tool provides valuable insights into repository structures, deployment patterns, and infrastructure setups.

## ✨ Key Features

### 🔍 Intelligent Repository Analysis
- **Comprehensive Data Collection**: Scrapes and analyzes repository data including:
  - Complete directory structures
  - Code content and patterns
  - CI/CD configuration files
  - Infrastructure as Code (IaC) files
  - Package and dependency management files

### 🛠️ Advanced Feature Detection
- **Deployment Platform Identification**:
  - AWS (CloudFormation, SAM, CDK)
  - Vercel
  - Firebase
  - Heroku
  - And more...

- **Infrastructure Analysis**:
  - CI/CD pipeline configurations
  - Containerization (Docker, Kubernetes)
  - Serverless architectures
  - Database implementations
  - Authentication systems

### 📊 Detailed Reporting
- Generates comprehensive reports in multiple formats:
  - CSV files for easy data analysis
  - JSON files for detailed technical insights
  - Console output for quick overviews

## 🛠️ Technical Requirements

### System Requirements
- Python 3.7 or higher
- Modern web browser (for Selenium)
- Stable internet connection

### Dependencies
The project uses several powerful Python packages:
- **Selenium**: For web scraping and automation
- **BeautifulSoup4**: For HTML parsing
- **OpenAI API**: For advanced code analysis
- **Requests**: For HTTP operations
- **tqdm**: For progress tracking

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## 🚀 Getting Started

### 1. Installation
```bash
# Clone the repository
git clone [your-repo-url]

# Navigate to the project directory
cd data-engineering-2

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the project root with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

### 3. Usage
Run the script with a file containing repository names and their deployment platforms:

```bash
python src/main.py repos.txt
```

### Input File Format (`repos.txt`)
```
username/repository | Platform
username/repository | Platform
```

Example:
```
haxybaxy/portfolio | Vercel
IsraelChidera/focus-app | Firebase
jitsi/jitsi-meet | Vercel
```

## 🔄 How It Works

### 1. Data Collection Phase
- Reads repository information from the input file
- Uses `GitIngestScraper` to collect repository data
- Downloads and processes repository contents

### 2. Analysis Phase
- `FeatureAnalyzer` class processes the collected data
- Identifies deployment platforms and infrastructure
- Analyzes code patterns and features
- Generates detailed insights

### 3. Output Generation
- Creates CSV files in the `temp` directory
- Generates JSON files with detailed analysis
- Provides console output for quick insights

## 📁 Project Structure

```
data-engineering-2/
├── src/
│   ├── main.py           # Main script entry point
│   ├── scraper.py        # Repository scraping logic
│   └── feature_analyzer.py # Analysis implementation
├── datasets/             # Sample datasets
├── requirements.txt      # Project dependencies
└── README.md            # This documentation
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please ensure your code follows our style guidelines and includes appropriate tests.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for their powerful API
- The open-source community for their invaluable tools
- All contributors who have helped improve this project





