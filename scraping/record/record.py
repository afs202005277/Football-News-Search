import requests
import sys

# Places where we import files
sys.path.append('../db/')
sys.path.append('../')
sys.path.append('./parsers/')

from db import DB
from log import Log
from timestamps import fetch_timestamps
from record_parser1 import RecordParser1
from record_parser2 import RecordParser2
from record_parser3 import RecordParser3

DEBUG = True
TIMESTAMPS_URL = 'https://arquivo.pt/partials/url-search-results?q=record.pt&l=pt&from=19910806&to=20230922&trackingId=0aff2dce6cf6860f8751_7c22d40ff6809992edcb&adv_and=record.pt'

db = DB()
log = Log('record')

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
        RecordParser1(timestamp, resp.text, db, log, DEBUG)
    elif year >= 2016:
        RecordParser2(timestamp, resp.text, db, log, DEBUG)
    elif year >= 2011:
        RecordParser3(timestamp, resp.text, db, log, DEBUG)
    """
    elif year >= x:
        RecordParser2(...)
    ...
    """

print('Scrapping [RECORD.PT] started.')

for timestamp in fetch_timestamps(TIMESTAMPS_URL):
    # For now, only these works >= 2019
    if timestamp[:4] >= '2019':
        fetch_timestamp(timestamp)
    """
    if timestamp[:4] >= '2016' and timestamp[:4] < '2019':
        fetch_timestamp(timestamp)
    """

print('Scrapping [RECORD.PT] ended.')
db.close()