# Papers Fetcher

A Python tool to fetch research papers from PubMed with at least one author affiliated with a pharmaceutical or biotech company.

## Code Organization

- papers_fetcher.py: Core module containing the paper fetching logic
- cli.py: Command-line interface
- pyproject.toml: Poetry configuration file

## Installation

1. Install Poetry: pip install poetry
2. Clone the repository: git clone https://github.com/Prathyukatta/papers-fetcher.git
3. Navigate to the project directory
4. Install dependencies: poetry install

## Configuration

Edit papers_fetcher.py to set your email:
```python
Entrez.email = "your.email@example.com"

poetry run get-papers-list "your pubmed query" [-d] [-f output.csv]
poetry run get-papers-list "cancer treatment" -d -f results.csv
