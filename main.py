import os
# import pandas as pd
import requests
# from bs4 import BeautifulSoup


url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=cancer&retmode=json"


headers = {"api-key": "ff4a79c70e50f45d406700691f1eb0439407"}
response = requests.get(url)
print(response.status_code)
print(response.text)