import requests
from bs4 import BeautifulSoup
from timestamps import fetch_record_timestamps
import logging

DEBUG = False

SECTIONS_BLACKLIST = ['Record Premium', 'Resultados e classificações']

logging.basicConfig(filename='record.log', filemode='w', format='%(levelname)s - %(message)s')

def fetch_section(section):
    if DEBUG: print(f'==> HANDLE SECTION - {section.text}\n')

    resp = requests.get(f'https://arquivo.pt{section["href"]}')
    soup = BeautifulSoup(resp.text, features='lxml')
    
    news = soup.select('div.noticia_box h1 a')
    for new in news:
        # Special type of news we are not interested
        if 'live' in new['href']: continue

        if DEBUG: print(f'= FOUND NEW - {new.text}\n')

        try:
            resp = requests.get(f'https://arquivo.pt{new["href"]}')
            soup = BeautifulSoup(resp.text, features='lxml')

            if not resp.ok:
                if DEBUG: print('FOUND EMPTY NEW PAGE')
                continue

            # For some reason, some news have duplicated div.text_container
            # Fetch the inner most, last in the result
            t = soup.select('div#texto_styck div.text_container')[-1]
            content = ''.join(t.find_all(string=True, recursive=False)).rstrip().lstrip().replace('\n', '')
            if content == '':
                logging.warning(f'Did not found the text of the new - {timestamp} - {new.text}')
                continue    
            
            #print(f'{new.text}\n{content}\n\n')
        except Exception as e:
            logging.error(f'Failed to get content on new - {timestamp} - {new.text}')
            pass

        if DEBUG: input()

def fetch_main_page(timestamp):
    resp = requests.get(f'https://arquivo.pt/noFrame/replay/{timestamp}/https://www.record.pt/')
    ok = False
    if not resp.ok:
        logging.error(f'Failed to fetch url - {timestamp}')
    elif resp.text == '':
        logging.warning(f'Timestamp returned empty page - {timestamp}')
    else:
        ok = True
    return resp, ok

def fetch_timestamp(timestamp):
    # For now, only 2019 for testing
    if timestamp[:4] != '2019':
        return
    
    if DEBUG: print(f'====================== {timestamp} ======================\n')

    resp, ok = fetch_main_page(timestamp)
    if not ok: return

    soup = BeautifulSoup(resp.text, features='lxml')
    sections = soup.select('header nav a')

    if DEBUG: print(f'SECTIONS FOUND: {",".join(map(lambda s : s.text, sections))}\n')

    for section in sections:
        if section.text not in SECTIONS_BLACKLIST:
            fetch_section(section)

for timestamp in fetch_record_timestamps():
    fetch_timestamp(timestamp)