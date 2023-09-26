import requests
import re
from bs4 import BeautifulSoup

def fetch_timestamps(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, features='lxml')
    return [re.findall(r'\d+', link['href'])[0] for link in soup.select('a') if '/wayback/' in link['href']]
