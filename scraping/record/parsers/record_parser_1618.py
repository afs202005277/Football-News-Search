##########################################
# PARSER FOR YEARS 2016-2018
##########################################

from record_parser import Parser

from bs4 import BeautifulSoup

class RecordParser1618(Parser):
    def __init__(self, timestamp, html, db, log, debug):
        super().__init__(timestamp, html, db, log, debug)

    def __news_selector__(self, soup):
        return soup.select('div.record-thumb .thumb-info a')

    def __new_content_selector__(self, soup):
        return ''.join(soup.select('#readerBody').find_all(string=True, recursive=False)).rstrip().lstrip().replace('\n', '')
    
    def __sections_selector__(self):
        return BeautifulSoup(self.html, features='lxml').select('.l1 .futebol a') 
