import requests
import sys
import re

# Places where we import files
sys.path.append('../db/')
sys.path.append('../')
sys.path.append('./parsers/')

from db import DB
from log import Log
from bs4 import BeautifulSoup

from record_parser_1115 import RecordParser1115
from record_parser_1618 import RecordParser1618
from record_parser_1922 import RecordParser1922

DEBUG = True
TIMESTAMPS_URL = 'https://arquivo.pt/partials/url-search-results?q=record.pt&l=pt&from=19910806&to=20230922&trackingId=0aff2dce6cf6860f8751_7c22d40ff6809992edcb&adv_and=record.pt'

db = DB()
log = Log('record')

def fetch_timestamps(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, features='lxml')
    return [re.findall(r'\d+', link['href'])[0] for link in soup.select('a') if '/wayback/' in link['href']]

def fetch_html(timestamp):
    resp = requests.get(f'https://arquivo.pt/noFrame/replay/{timestamp}/https://www.record.pt/')
    ok = False
    if not resp.ok:
        log.error(f'Failed to fetch url - {timestamp}')
    elif resp.text == '':
        log.warning(f'Timestamp returned empty page - {timestamp}')
    else:
        ok = True
    return resp, ok

def fetch_timestamp(timestamp):
    print(f'====================== {timestamp} ======================\n')
    resp, ok = fetch_html(timestamp)
    if not ok: return

    year = int(timestamp[:4])
    if year >= 2019: 
        RecordParser1922(timestamp, resp.text, db, log, DEBUG)
    elif year >= 2016:
        RecordParser1618(timestamp, resp.text, db, log, DEBUG)
    elif year >= 2011:
        RecordParser1115(timestamp, resp.text, db, log, DEBUG)

print('Scrapping [RECORD.PT] started.')

for timestamp in fetch_timestamps(TIMESTAMPS_URL):
    # Temporary code to test different scrappers
    test_scrappers = 0

    if (test_scrappers == 0 and timestamp[:4] >= '2019') or \
       (test_scrappers == 1 and timestamp[:4] >= '2016' and timestamp[:4] < '2019') or \
       (test_scrappers == 1 and timestamp[:4] >= '2011' and timestamp[:4] < '2016'):
        fetch_timestamp(timestamp)

print('Scrapping [RECORD.PT] ended.')
db.close()