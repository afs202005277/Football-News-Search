##########################################
# PARSER FOR YEARS 2011-2015
##########################################

from record_parser import Parser

from bs4 import BeautifulSoup

class RecordParser1115(Parser):
    def __init__(self, timestamp, html, db, log, debug):
        super().__init__(timestamp, html, db, log, debug)

    def __news_selector__(self, soup):
        return soup.select('div.caixaModNot a.linkUnd')

    def __new_content_selector__(self, soup):
        if self.timestamp[:4] == '2011':
            return ''.join(soup.select('#NewsContainer .newsBody')[0].find_all(string=True, recursive=True)).rstrip().lstrip().replace('\n', '')
        return ''.join(soup.select('#NewsContainer .texto')[0].find_all(string=True, recursive=True)).rstrip().lstrip().replace('\n', '')
    
    def __sections_selector__(self):
        return BeautifulSoup(self.html, features='lxml').select('.listaBrazoes a')
