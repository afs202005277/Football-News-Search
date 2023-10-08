##########################################
# PARSER FOR YEARS 2008-2010
##########################################

from record_parser import Parser

from bs4 import BeautifulSoup

class RecordParser0810(Parser):
    def __init__(self, timestamp, html, db, log, debug):
        super().__init__(timestamp, html, db, log, debug)

    def __news_selector__(self, soup):
        return list(filter(lambda x : 'noticia' in x['href'], soup.select('a.bcinzento')))

    def __new_content_selector__(self, soup):
        return ''.join(soup.select('.apreto12n')[0].find_all(string=True, recursive=True)).rstrip().lstrip().replace('\n', '')
    
    def __sections_selector__(self):
        links = BeautifulSoup(self.html, features='lxml').select('#menu-05 ul.rMenu-ver a')
        if self.timestamp[:4] == '2009':
            for link in links:
                link['href'] = f'/noFrame/replay/{self.timestamp}/http://www.record.pt/{link["href"]}'
        return links
