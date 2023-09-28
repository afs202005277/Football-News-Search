##########################################
# PARSER FOR YEARS 2019-2022
##########################################

from bs4 import BeautifulSoup
import requests

class Parser():
    def __init__(self, timestamp, html, db, log, debug):
        self.debug = debug
        self.timestamp = timestamp
        self.html = html
        self.db = db
        self.log = log
        self.fetch_news()

    def __news_selector__(self, soup):
        raise NotImplementedError('Abstract Method - Implementation Missing')

    def __new_content_selector__(self, soup):
        raise NotImplementedError('Abstract Method - Implementation Missing')
    
    def __sections_selector__(self):
        raise NotImplementedError('Abstract Method - Implementation Missing')

    def fetch_section(self, section):
        if self.debug: print(f'\n==> HANDLE SECTION - {section.text}\n')

        news_counter = 0
        resp = requests.get(f'https://arquivo.pt{section["href"]}')
        soup = BeautifulSoup(resp.text, features='lxml')
        
        news = self.__news_selector__(soup)
        for new in news:
            if self.debug: print(f'= FOUND NEW - {new.text}')

            try:
                resp = requests.get(f'https://arquivo.pt{new["href"]}')
                soup = BeautifulSoup(resp.text, features='lxml')

                if not resp.ok:
                    self.log.warning(f'Failed to fecth new page - {self.timestamp} - {new.text}')
                    continue

                content = self.__new_content_selector__(soup)                
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
        return news_counter

    def fetch_news(self):
        news_counter = 0
        for section in self.__sections_selector__():
            news_counter += self.fetch_section(section)

        if news_counter == 0: 
            self.log.error(f'Didn\'t found any new on timestamp {self.timestamp}, analyze this year.')
        print(f'Found {news_counter} news on {self.timestamp}')