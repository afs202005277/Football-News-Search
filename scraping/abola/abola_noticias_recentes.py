import sqlite3

import requests
from bs4 import BeautifulSoup
import multiprocessing
from scraping.db.db import DB
from scraping.utils import convert_to_uniform_date


def scrape_link(link):
    link = link['linkToNoFrame']
    content = requests.get(link)
    soup = BeautifulSoup(content.content, features="html.parser")

    try:
        # 2008 & 2009 - no need to do it (already done by Andre)
        if "replay/2008" in link or "replay/2009" in link:
            return {}
    except:
        pass

    if content.status_code in [400, 404] or (soup.find('title') is not None and 'Página não encontrada' in soup.find('title').get_text(strip=True)) or soup.find('body') is None or ".woff" in link or (soup.find('h2') is not None and 'Página indisponível' in soup.find('h2').text) or (soup.find('div', attrs={'class', 'msg-erro'}) is not None and 'Ocorreu um erro. Por favor tente novamente.' in soup.find('div', attrs={'class', 'msg-erro'}).get_text(strip=True)):
        return {}

    try:
        title = soup.find('div', attrs={'id': 'a5g2'}).text
        text = soup.find('div', attrs={'id': 'a5g4'}).text
        date = soup.find('div', attrs={'id': 'a5x'}).text.split()[-1]
        return {'title': title, 'content': text, 'date': date}
    except:
        pass

    try:
        #2017-...
        new = soup.find('section', attrs={'id': 'Noticia'})
        if soup.find('h5') is not None and 'Não existem notícias com o conteúdo requisitado.' in soup.find('h5').get_text(strip=True):
            return {}
        title = new.find('h1', attrs={'class': 'titulo'}).text
        text_container = new.find('div', attrs={'class': 'corpo-noticia'})
        text = "\n".join([p.text for p in text_container.findAll('p')])
        date = new.find('span', attrs={'class', 'data-hora'}).find('span').text.split()[0]
        return {'title': title, 'content': text, 'date': date}
    except:
        pass

    print('Not extractable: ', link)
    return {}

def save_to_db(db, data):
    for document in data:
        try:
            if document != {}:
                db.insert_new((document['title'], document['content'], document['date'], 'abola'))
        except sqlite3.IntegrityError as e:
            continue

if __name__ == "__main__":


    from_date = 19960101000000
    to_date = from_date + 100000000 if int((from_date + 100000000) / 100000000) - int((from_date + 100000000) / 10000000000)*100 < 13 else from_date + 8900000000

    headers = {'Accept': 'application/json'}

    real_offset = 0

    while to_date < 20231006000000:

        offset = 0
        r = requests.get('https://arquivo.pt/textsearch?q=nnh&siteSearch=abola.pt&maxItems=2000&offset=' + str(offset) + '&fields=linkToNoFrame&from=' + str(from_date) + '&to=' + str(to_date), headers=headers)
        response_items = r.json()["response_items"]

        while len(response_items) != 0:
            pool_obj = multiprocessing.Pool()
            ans = pool_obj.map(scrape_link, response_items)
            pool_obj.close()

            save_to_db(DB(), ans)

            offset += len(response_items)
            real_offset += len(response_items)
            r = requests.get('https://arquivo.pt/textsearch?q=nnh&siteSearch=abola.pt&maxItems=2000&offset=' + str(offset) + '&fields=linkToNoFrame&from=' + str(from_date) + '&to=' + str(to_date), headers=headers)
            response_items = r.json()["response_items"]
            print("Done ", real_offset, "links")

        from_date = to_date
        to_date = from_date + 100000000 if int((from_date + 100000000) / 100000000) - int((from_date + 100000000) / 10000000000)*100 < 13 else from_date + 8900000000