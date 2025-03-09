# papers_fetcher.py
from typing import List, Dict, Optional
import csv
import logging
import os
from datetime import datetime
import requests
from Bio import Entrez  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

Entrez.email = os.getenv("PUBMED_EMAIL", "your.email@example.com")
Entrez.api_key = "c51aa81834d511930dfdde2af96d7b862708"  # Hardcoded API key

class PaperFetcher:
    """Class to fetch and process research papers from PubMed."""
    
    def __init__(self, query: str, debug: bool = False):
        """Initialize with search query and debug flag."""
        self.query = query
        self.debug = debug
        self.setup_logging()

    def setup_logging(self) -> None:
        """Configure logging based on debug flag."""
        level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    def search_papers(self) -> List[str]:
        """Search PubMed and return list of paper IDs."""
        try:
            handle = Entrez.esearch(db="pubmed", term=self.query, retmax=100)
            record = Entrez.read(handle)
            handle.close()
            logging.debug(f"Found {len(record['IdList'])} papers")
            return record['IdList']
        except Exception as e:
            logging.error(f"Search failed: {str(e)}")
            raise

    def fetch_paper_details(self, ids: List[str]) -> List[Dict]:
        """Fetch detailed information for given paper IDs."""
        try:
            handle = Entrez.efetch(db="pubmed", id=ids, retmode="xml")
            papers = Entrez.read(handle)
            handle.close()
            return self.process_papers(papers)
        except Exception as e:
            logging.error(f"Fetch details failed: {str(e)}")
            raise

    def is_company_affiliation(self, affiliation: str) -> bool:
        """Heuristic to identify company affiliations."""
        academic_terms = {'university', 'college', 'institute', 'laboratory', 'school', 'dept', 'department'}
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
                        affiliations.append(author_aff.split(',')[0])
                
                email = ""
                if "ELocationID" in article:
                    for eloc in article["ELocationID"]:
                        if "ValidYN" in eloc.attributes and eloc.attributes["ValidYN"] == "Y":
                            email = str(eloc)
                
                if company_authors:
                    results.append({
                        "PubmedID": pubmed_id,
                        "Title": title,
                        "Publication Date": date_str,
                        "Non-academic Author(s)": "; ".join(company_authors),
                        "Company Affiliation(s)": "; ".join(affiliations),
                        "Corresponding Author Email": email
                    })
                    
            except Exception as e:
                logging.debug(f"Error processing paper {pubmed_id}: {str(e)}")
                continue
                
        return results

    def save_to_csv(self, results: List[Dict], filename: Optional[str] = None) -> None:
        """Save results to CSV file or print to console."""
        if not results:
            logging.info("No results to save")
            return

        headers = ["PubmedID", "Title", "Publication Date", 
                  "Non-academic Author(s)", "Company Affiliation(s)", 
                  "Corresponding Author Email"]
        
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(results)
            logging.info(f"Results saved to {filename}")
        else:
            print(",".join(headers))
            for row in results:
                print(",".join(f'"{row.get(h, "")}"' for h in headers))

def fetch_papers(query: str, debug: bool = False, filename: Optional[str] = None) -> None:
    """Main function to fetch papers and save results."""
    fetcher = PaperFetcher(query, debug)
    ids = fetcher.search_papers()
    results = fetcher.fetch_paper_details(ids)
    fetcher.save_to_csv(results, filename)