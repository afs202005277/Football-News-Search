import sqlite3
from datetime import timedelta
from bs4 import BeautifulSoup
from scraping.utils import *
from scraping.RateLimitedRequest import RateLimitedRequest
from scraping.db.db import DB


def has_no_seta_id(tag):
    return tag.has_attr('class') and 'linkNoticias' in tag['class'] and 'seta' not in tag.get('id', '')


class ABolaScrapper:

    def __init__(self, params, limited_requester, black_list):
        self.params = params
        self.target_text = ""
        self.all_data = []
        self.requester = limited_requester
        self.black_list = black_list

    def contains_text(self, element):
        return self.target_text in element.get_text()

    def parser1(self, links, url):
        final = []
        for link in links:
            href = link.get('href')
            self.target_text = link.get_text()
            if "ver" in href and "icia" in href:
                href = '?op=ver&noticia=' + href[href.find('icia=') + len('icia='):]
            new_url = url[:url.rfind('?')] + href
            if any(substring in new_url for substring in self.black_list):
                continue
            full_page = self.requester.get(new_url)
            full_page_soup = BeautifulSoup(full_page.text, 'html.parser')
            tables = full_page_soup.select('tr > td.dg')
            title_element = list(filter(self.contains_text, tables))[0]
            full_text = title_element.parent.parent.get_text(strip=True, separator='\n')
            full_text = full_text[full_text.find(self.target_text) + len(self.target_text):]
            publish_date = full_text.split("\n")[-1]
            full_text = full_text[:full_text.find(publish_date)]
            final.append({'title': title_element.text, 'body': full_text, 'date': publish_date})
        return final

    def parser2(self, soup, url, find_more):
        final = []
        text_fields = soup.select('table[id*="Noticia"] p')
        title = text_fields[0].text
        body = "\n".join(map(lambda x: x.text, text_fields[1:]))
        date = soup.find(class_='dataTitNotPrincipal').text
        final.append({'title': title, 'body': body, 'date': date})
        if find_more:
            links = soup.find_all(has_no_seta_id)
            for link in links:
                new_link = url[:url.rfind('/') + 1] + link.get('href')
                if any(substring in new_link for substring in self.black_list):
                    continue
                response = self.requester.get(new_link)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                final += self.parser2(soup, new_link, False)
        return final

    def parse_text(self, url):
        final = []
        try:
            # Send a GET request to the URL
            if any(substring in url for substring in self.black_list):
                return final
            response = self.requester.get(url)
            response.raise_for_status()  # Raise an exception if the request was not successful

            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', {'class': 'dg'}, recursive=True)
            if len(links) != 0:
                final += self.parser1(links, url)
            elif soup.select('table[id*="Noticia"]'):
                final += self.parser2(soup, url, True)
            elif 'print.asp' in url:
                title = soup.find('td', {'class': 'dg'}).text
                body = []
                for body_element in soup.find_all('td', class_=['de', 'df']):
                    body.append(body_element.get_text(strip=True))
                body = "\n".join(body)
                date = soup.find('td', {'class': 'dk'}).text
                final += {'title': title, 'body': body, 'date': date}
            elif len(list(soup.find('body').children)) == 1 and list(soup.find('body').children)[0].name == 'img':
                print('Found single image. Ignoring...')
            else:
                print("Unknown HTML: " + url)
        except Exception as e:
            print(f"An error occurred: {e}")
        return final

    def fetch_all(self):
        start_date = datetime.strptime(self.params['from'], "%Y%m%d%H%M%S")
        current_time = datetime.now()
        one_month = timedelta(days=30.44)

        while start_date < current_time:
            while True:
                link = build_api_request(self.params)
                print("Major request: " + link)
                all_urls = self.requester.get(link)
                if all_urls.headers.get("content-type") == "application/json":
                    json_data = all_urls.json()
                    for idx, json_object in enumerate(json_data['response_items']):
                        self.all_data += self.parse_text(json_object['linkToNoFrame'])
                        print(len(self.all_data))
                    if len(json_data['response_items']) == 0:
                        break
                    self.params['offset'] = str(
                        int(self.params['offset']) + len(json_data['response_items']))

            start_date += one_month
            self.params['from'] = start_date.strftime("%Y%m%d%H%M%S")
            self.params['to'] = (start_date + one_month).strftime("%Y%m%d%H%M%S")
            self.params['offset'] = "0"

        return self.all_data

    def save_to_db(self, db):
        for document in self.all_data:
            try:
                db.insert_new((document['title'], document['body'], convert_to_uniform_date(document['date']), 'abola'))
            except sqlite3.IntegrityError as e:
                continue
        print("Finished saving. Current size of table: " + str(db.count_rows()))


def main(url=None):
    request_parameters = {
        'q': '',
        'from': '20070609140106',
        'to': '20070709140106',
        'siteSearch': 'abola.pt',
        'maxItems': '2000',
        'prettyPrint': 'false',
        'dedupValue': '2000',
        'dedupField': 'site',
        'fields': 'linkToNoFrame',
        'offset': '0'
    }
    black_list = ['votar.aspx', '/videos/', 'registo.aspx', '.css', '.jpg', 'gif', '.png', '.swf']
    limited_requester = RateLimitedRequest(250)
    scrapper = ABolaScrapper(request_parameters, limited_requester, black_list)
    if url:
        all_data = scrapper.parse_text(url)
    else:
        all_data = scrapper.fetch_all()
    print("Retrieved " + str(len(all_data)) + " data items!")
    scrapper.save_to_db(DB())


if __name__ == "__main__":
    main()
# url = 'https://arquivo.pt/noFrame/replay/20081021111623/http://abola.pt/nnh/ver.aspx?id=150881'
# print(parse_text(url))
# 2194
