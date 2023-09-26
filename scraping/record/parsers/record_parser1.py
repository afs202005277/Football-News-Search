##########################################
# PARSER FOR YEARS 2019-2022
##########################################

from bs4 import BeautifulSoup
import requests

SECTIONS_BLACKLIST = ['Record Premium', 'Resultados e classificações', 'Internacional']

class RecordParser1():
    def __init__(self, timestamp, html, db, log, debug):
        self.debug = debug
        self.timestamp = timestamp
        self.html = html
        self.db = db
        self.log = log
        self.fetch_news()

    def fetch_section(self, section):
        if self.debug: print(f'\n==> HANDLE SECTION - {section.text}\n')

        news_counter = 0

        resp = requests.get(f'https://arquivo.pt{section["href"]}')
        soup = BeautifulSoup(resp.text, features='lxml')
        
        news = soup.select('div.noticia_box h1 a')
        for new in news:
            # Special type of news we are not interested
            if 'live' in new['href']: continue

            if self.debug: print(f'= FOUND NEW - {new.text}')

            try:
                resp = requests.get(f'https://arquivo.pt{new["href"]}')
                soup = BeautifulSoup(resp.text, features='lxml')

                if not resp.ok:
                    if self.debug: print('FOUND EMPTY NEW PAGE')
                    continue

                # For some reason, some news have duplicated div.text_container
                # Fetch the inner most, last in the result
                t = soup.select('div#texto_styck div.text_container')[-1]
                content = ''.join(t.find_all(string=True, recursive=False)).rstrip().lstrip().replace('\n', '')
                if content == '':
                    self.log.warning(f'Did not found the text of the new - {self.timestamp} - {new.text}')
                    continue    
                
                try:
                    self.db.insert_new((new.text, content))
                except Exception as e:
                    self.log.error(f'Failed to insert into in the database, maybe duplicated - {e}')
                finally:
                    news_counter += 1
                #print(f'{new.text}\n{content}\n\n')
            except Exception as e:
                self.log.error(f'Failed to get content on new - {self.timestamp} - {new.text}')
                pass

            #ckif DEBUG: input()
        return news_counter

    def fetch_news(self):
        soup = BeautifulSoup(self.html, features='lxml')
        sections = soup.select('header nav a')

        if self.debug: print(f'SECTIONS FOUND: {",".join(map(lambda s : s.text, sections))}')

        news_counter = 0
        for section in sections:
            if section.text not in SECTIONS_BLACKLIST:
                news_counter += self.fetch_section(section)
        if news_counter == 0: self.log.error(f'Didn\'t found any new on timestamp {self.timestamp}, analyze this year.')
        print(f'Found {news_counter} news on {self.timestamp}')