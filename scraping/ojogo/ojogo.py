import sqlite3
from datetime import timedelta

from scraping.RateLimitedRequest import RateLimitedRequest
from bs4 import BeautifulSoup
import requests
import logging
from scraping.db.db import DB
from scraping.utils import *
import re

logging.basicConfig(filename='ojogo.log', filemode='w', format='%(levelname)s - %(message)s')


def parser1(soup):
    title_element = soup.select_one('header div h1')
    text_list = [title_element.text]
    if title_element.select_one('span.ojpremium'):
        text_list[0] = text_list[0][len("Premium "):]
    for child in soup.find('div', {'class': 't-a-c-wrap js-select-and-share-1'}).find_all(recursive=False):
        if (child.has_attr('role') and child['role'] == 'complementary') or (
                child.has_attr('class') and any('pub-box' in fc for fc in child.get('class'))) or (
                child.has_attr('class') and
                child.name == 'div' and any('footer' in fc for fc in child.get('class'))):
            continue
        text = child.get_text(strip=True)
        text_list.append(text)
    return text_list[0], "" if len(text_list) == 1 else ' '.join(text_list[1:]), soup.select('time')[0].get('datetime')[
                                                                                 :len("0000-00-00")]


def parse_text(limit_request, url):
    res = []
    try:
        original_file_response = limit_request.get(url)
        original_file_response.raise_for_status()

        soup = BeautifulSoup(original_file_response.text, 'html.parser')
        page_title = soup.find('title').text
        if page_title == 'Sapo Infordesporto' or 'Assinaturas' in page_title:
            return res
        target_div = soup.find('div', {'class': 't-a-c-wrap js-select-and-share-1'})
        body_table = soup.select('body > table')
        if target_div:
            res.append(parser1(soup))
        elif len(body_table) == 1:
            main_table = body_table[0]
            title = body_table[0].find('h1').get_text(strip=True)
            body = main_table.find_all('p')[2:]
            body = list("\n".join(map(lambda x: x.get_text(strip=True), body)))
            tmp = list(filter(lambda x: re.match(r'\b\d{2}-\d{2}-\d{4}\b', x.get_text(strip=True)),
                              soup.select('body > table > tr table font')))
            date = tmp[0].get_text(strip=True)
            res.append((title, body, date))
        elif soup.find('div', {'class': 't-g1-list-1'}).find('div').find_all('article'):
            links = list(map(lambda x: x.find('h2').find('a').get('href'),
                             soup.find('div', {'class': 't-g1-list-1'}).find('div').find_all('article')))
            for link in links:
                full_link = "https://arquivo.pt" + link
                response = requests.get(full_link)
                response.raise_for_status()
                res.append(parser1(BeautifulSoup(response.text, 'html.parser')))
        else:
            print("Unknown HTML: " + url)
    except Exception as e:
        print("Error: " + str(e) + "\nurl: " + url + "\n")
    return res


def fetch_all(request_params):
    blacklist = ['.gif', '.jpg', 'estatisticas.asp', 'resultados.asp', '.txt', 'apps-rss', 'termos-uso', '/sugestoes/',
                 'pesquisa.html', 'resultados.html', 'classificacoes.html', 'multimedia/videos', '/subscricoes',
                 '/totojogos', 'requests.aspx', 'content-gating', '.ttf', 'ficha-tecnica']
    used_links = set()
    files = []
    final_url = ""
    limit_request = RateLimitedRequest()
    start_date = datetime.strptime(request_params['from'], "%Y%m%d%H%M%S")
    current_time = datetime.now()
    one_month = timedelta(days=30.44)
    while start_date < current_time:
        print(len(files))
        try:
            final_url = build_api_request(request_params)
            response = limit_request.get(final_url)
            print("Major request: " + final_url)
            if response.headers.get("content-type") == "application/json":
                json_data = response.json()
                for idx, json_object in enumerate(json_data['response_items']):
                    if (len(json_object['title']) < 4 or not (json_object['title'][3] == ' ' and json_object['title'][
                                                                                                 :3].isdigit())) and 'linkToNoFrame' in json_object:
                        original_file_url = json_object['linkToNoFrame']
                        if original_file_url in used_links or any(
                                substring in original_file_url for substring in blacklist):
                            continue
                        else:
                            used_links.add(original_file_url)
                        files += parse_text(limit_request, original_file_url)
                    else:
                        logging.warning(f'Http status code title: ' + str(idx))
                request_params['offset'] = str(int(request_params['offset']) + len(json_data['response_items']))
                start_date += one_month
                request_params['from'] = start_date.strftime("%Y%m%d%H%M%S")
                request_params['to'] = (start_date + one_month).strftime("%Y%m%d%H%M%S")
                request_params['offset'] = "0"
            else:
                print(f"URL '{final_url}' does not return JSON data.")

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching URL '{final_url}': {e}")
    return files


def main(url=None):
    request_parameters = {
        'q': '',
        'from': '20000609140106',
        'to': '20000709140106',
        'siteSearch': 'ojogo.pt',
        'maxItems': '2000',
        'prettyPrint': 'false',
        'fields': 'title,linkToNoFrame',
        'offset': '0'
    }
    if url:
        var = parse_text(RateLimitedRequest(250), url)
        print(var)
        print(len(var))
    else:
        documents = fetch_all(request_parameters)
        db = DB()
        for (title, body, date) in documents:
            try:
                if isinstance(body, list):
                    body = "".join(body)
                db.insert_new((title, body, convert_to_uniform_date(date)))
            except sqlite3.IntegrityError as e:
                continue
        db.close()


main(
    'https://arquivo.pt/noFrame/replay/20190831083848/https://ojogo.pt/futebol/1a-liga/rio-ave/noticias/interior/extremo-do-chelsea-a-caminho-do-rio-ave-avancam-em-italia-11241429.html')
