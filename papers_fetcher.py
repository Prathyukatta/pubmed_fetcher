from typing import List, Dict, Optional
import csv
import logging
import os
import time
import requests
import pandas as pd
from datetime import datetime
from Bio import Entrez  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

# Set Entrez API details
Entrez.email = os.getenv("PUBMED_EMAIL", "your.email@example.com")
Entrez.api_key = "c51aa81834d511930dfdde2af96d7b862708"  # Hardcoded API key

class PaperFetcher:
    """Class to fetch and process research papers from PubMed."""

    def __init__(self, query: str = "Machine Learning", debug: bool = False):
        """Initialize with search query and debug flag."""
        self.query = query
        self.debug = debug
        self.setup_logging()

    def setup_logging(self) -> None:
        """Configure logging based on debug flag."""
        level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    def search_papers(self) -> List[str]:
        """Search PubMed and return list of paper IDs."""
        try:
            handle = Entrez.esearch(db="pubmed", term=self.query, retmax=100)
            record = Entrez.read(handle)
            handle.close()
            logging.debug(f"Found {len(record['IdList'])} papers")
            return record["IdList"]
        except Exception as e:
            logging.error(f"Search failed: {str(e)}")
            return []

    def fetch_paper_details(self, ids: List[str]) -> List[Dict]:
        """Fetch detailed information for given paper IDs."""
        results = []
        try:
            handle = Entrez.efetch(db="pubmed", id=ids, retmode="xml")
            papers = Entrez.read(handle)
            handle.close()
            return self.process_papers(papers)
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error: {str(e)}")
        except Exception as e:
            logging.error(f"Fetch details failed: {str(e)}")
        return results

    def is_company_affiliation(self, affiliation: str) -> bool:
        """Heuristic to identify company affiliations."""
        academic_terms = {"university", "college", "institute", "laboratory", "school", "dept", "department"}
        affiliation_lower = affiliation.lower()
        return not any(term in affiliation_lower for term in academic_terms)

    def process_papers(self, papers: Dict) -> List[Dict]:
        """Process raw paper data into structured format."""
        results = []
        for paper in papers["PubmedArticle"]:
            try:
                medline = paper["MedlineCitation"]
                article = medline["Article"]

                pubmed_id = str(medline["PMID"])
                title = article["ArticleTitle"]
                pub_date = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
                date_str = f"{pub_date.get('Year', '')}-{pub_date.get('Month', '01')}-{pub_date.get('Day', '01')}"

                authors = article.get("AuthorList", [])
                company_authors = []
                affiliations = []

                for author in authors:
                    aff_list = author.get("AffiliationInfo", [])
                    if not aff_list:
                        continue

                    author_aff = aff_list[0].get("Affiliation", "")
                    if self.is_company_affiliation(author_aff):
                        name = f"{author.get('ForeName', '')} {author.get('LastName', '')}".strip()
                        company_authors.append(name)
                        affiliations.append(author_aff.split(",")[0])

                email = ""
                if "ELocationID" in article:
                    for eloc in article["ELocationID"]:
                        if "ValidYN" in eloc.attributes and eloc.attributes["ValidYN"] == "Y":
                            email = str(eloc)

                if company_authors:
                    results.append(
                        {
                            "PubmedID": pubmed_id,
                            "Title": title,
                            "Publication Date": date_str,
                            "Non-academic Author(s)": "; ".join(company_authors),
                            "Company Affiliation(s)": "; ".join(affiliations),
                            "Corresponding Author Email": email,
                        }
                    )

            except Exception as e:
                logging.debug(f"Error processing paper {pubmed_id}: {str(e)}")
                continue

        return results

    def save_to_excel(self, results: List[Dict], filename: str = "results.xlsx") -> None:
        """Save results to an Excel file and open it."""
        if not results:
            logging.info("No results to save")
            return

        df = pd.DataFrame(results)
        df.to_excel(filename, index=False, engine="openpyxl")
        logging.info(f"Results saved to {filename}")

        # Open the Excel file automatically (Windows only)
        os.startfile(filename)

def fetch_papers(debug: bool = False) -> None:
    """Main function to fetch papers and save results to an Excel file."""
    fetcher = PaperFetcher(debug=debug)
    ids = fetcher.search_papers()
    
    # Retry mechanism for incomplete HTTP read
    for _ in range(3):
        try:
            results = fetcher.fetch_paper_details(ids)
            break
        except Exception as e:
            logging.warning(f"Retrying due to error: {str(e)}")
            time.sleep(5)
    else:
        logging.error("Failed to fetch paper details after multiple attempts.")
        return

    fetcher.save_to_excel(results)

if __name__ == "__main__":
    fetch_papers(debug=True)
