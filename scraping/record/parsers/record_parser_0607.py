##########################################
# PARSER FOR YEARS 2006-2007
##########################################

from record_parser import Parser

from bs4 import BeautifulSoup

class RecordParser0607(Parser):
    def __init__(self, timestamp, html, db, log, debug):
        super().__init__(timestamp, html, db, log, debug)

    def __news_selector__(self, soup):
        return soup.select('a.v9_black')

    def __new_content_selector__(self, soup):
        return ''.join(soup.select('aux').find_all(string=True, recursive=False)).rstrip().lstrip().replace('\n', '')
    
    def __sections_selector__(self):
        soup = BeautifulSoup(self.html, features='lxml')
        links = soup.select('a.v10_menu')
        filtered = list(filter(lambda x : 'idselect' in x['href'], links))
        for f in filtered:
            f['href'] = f'/noFrame/replay/{self.timestamp}/http://www.record.pt/{f["href"]}'
        return filtered