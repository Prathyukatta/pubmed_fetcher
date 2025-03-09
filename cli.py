# cli.py
import argparse
from typing import Optional
from papers_fetcher import fetch_papers

def main() -> None:
    """Command-line interface for fetching papers."""
    parser = argparse.ArgumentParser(
        description="Fetch research papers from PubMed with company affiliations"
    )
    parser.add_argument("query", help="PubMed search query")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")
    parser.add_argument("-f", "--file", help="Output CSV filename")
    # parser.add_argument("-k", "--api-key", help="PubMed API key (optional)")
    
    args = parser.parse_args()
    
    fetch_papers(args.query, args.debug, args.file )

if __name__ == "__main__":
    main()