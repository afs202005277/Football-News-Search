import requests
import re
from bs4 import BeautifulSoup

URL = 'https://arquivo.pt/partials/url-search-results?q=record.pt&l=pt&from=19910806&to=20230922&trackingId=0aff2dce6cf6860f8751_7c22d40ff6809992edcb&adv_and=record.pt'

def fetch_record_timestamps():
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, features='lxml')
    return [re.findall(r'\d+', link['href'])[0] for link in soup.select('a') if '/wayback/' in link['href']]

if __name__ == '__main__':
    print(fetch_record_timestamps())