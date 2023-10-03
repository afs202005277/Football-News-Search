##########################################
# PARSER FOR YEARS 2019-2022
##########################################

from record_parser import Parser

from bs4 import BeautifulSoup

class RecordParser1922(Parser):
    def __init__(self, timestamp, html, db, log, debug):
        self.blacklist = ['Record Premium', 'Resultados e classificações', 'Internacional']
        super().__init__(timestamp, html, db, log, debug)

    def __news_selector__(self, soup):
        return soup.select('div.noticia_box h1 a')

    def __new_content_selector__(self, soup):
        # For some reason, some news have duplicated div.text_container
        # Fetch the inner most, last in the result
        t = soup.select('div#texto_styck div.text_container')[-1]
        return ''.join(t.find_all(string=True, recursive=False)).rstrip().lstrip().replace('\n', '')
    
    def __sections_selector__(self):
        sections = BeautifulSoup(self.html, features='lxml').select('.icons_menu.futebol ul li > a')
        return list(filter(lambda x : x.text not in self.blacklist, sections))
