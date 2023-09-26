##########################################
# PARSER FOR YEARS 2011-2015
##########################################

from bs4 import BeautifulSoup
import requests

class RecordParser3():
    def __init__(self, timestamp, html, db, log, debug):
        self.debug = debug
        self.timestamp = timestamp
        self.html = html
        self.db = db
        self.log = log
        self.club_sections = []
        self.fetch_club_sections()
        self.fetch_news()

    def fetch_club_sections(self):
        resp = requests.get(f'https://arquivo.pt/noFrame/replay/{self.timestamp}/http://www.record.xl.pt/')
        soup = BeautifulSoup(resp.text, features='lxml')

        for a in soup.select('.listaBrazoes a'):
            self.club_sections.append(a['href'][30:])

    def fetch_section(self, section):
        if self.debug: print(f'\n==> HANDLE SECTION - {section}\n')

        news_counter = 0

        resp = requests.get(f'https://arquivo.pt/noFrame/replay/{self.timestamp}{section}')
        soup = BeautifulSoup(resp.text, features='lxml')
        
        news = soup.select('div.caixaModNot a.linkUnd')
        for new in news:
            if self.debug: print(f'= FOUND NEW - {new.text}')

            try:
                resp = requests.get(f'https://arquivo.pt{new["href"]}')
                soup = BeautifulSoup(resp.text, features='lxml')

                if not resp.ok:
                    if self.debug: print('FOUND EMPTY NEW PAGE')
                    continue

                content = ''.join(soup.select('#newsBody').find_all(string=True, recursive=False)).rstrip().lstrip().replace('\n', '')
                if content == '':
                    self.log.warning(f'Did not found the text of the new - {self.timestamp} - {new.text}')
                    continue    
                
                try:
                    self.db.insert_new((new.text, content))
                except Exception as e:
                    self.log.error(f'Failed to insert into in the database, maybe duplicated - {e}')
                finally:
                    news_counter += 1
            except Exception as e:
                self.log.error(f'Failed to get content on new - {self.timestamp} - {new.text}')
                pass

        return news_counter

    def fetch_news(self):
        news_counter = 0
        for section in self.club_sections + ['/http://www.record.xl.pt/futebol/default.aspx']:
            self.fetch_section(section)
        if news_counter == 0: self.log.error(f'Didn\'t found any new on timestamp {self.timestamp}, analyze this year.')
        print(f'Found {news_counter} news on {self.timestamp}')