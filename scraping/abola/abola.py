from datetime import datetime

import requests
from bs4 import BeautifulSoup
from utils import *

target_text = ""


def contains_text(element):
    return target_text in element.get_text()


def get_current_timestamp():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def parse_text(url):
    global target_text
    final = []
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was not successful

        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all the anchor (a) tags in the HTML
        links = soup.find_all('a', {'class': 'dg'}, recursive=True)

        # Extract and print the href attribute of each anchor tag
        for link in links:
            href = link.get('href')
            target_text = link.get_text()
            if "ver" in href and "icia" in href:
                href = '?op=ver&noticia=' + href[href.find('icia=') + len('icia='):]
            new_url = url[:url.rfind('?')] + href
            full_page = requests.get(new_url)
            full_page_soup = BeautifulSoup(full_page.text, 'html.parser')
            tables = full_page_soup.select('tr > td.dg')
            title_element = list(filter(contains_text, tables))[0]
            full_text = title_element.parent.parent.get_text(strip=True, separator='\n')
            full_text = full_text[full_text.find(target_text) + len(target_text):]
            publish_date = full_text.split("\n")[-1]
            full_text = full_text[:full_text.find(publish_date)]
            final.append({'title': title_element.text, 'body': full_text, 'date': publish_date})
    except Exception as e:
        print(f"An error occurred: {e}")
    return set(final)


def main():
    request_parameters = {
        'q': '',
        'to': get_current_timestamp(),
        'siteSearch': 'ojogo.pt',
        'maxItems': '2000',
        'prettyPrint': 'false',
        'dedupValue': '2000',
        'dedupField': 'site',
        'offset': '0'
    }

    parse_text(url)


main()
url = 'https://arquivo.pt/noFrame/replay/20080311162500/http://abola.pt/nnh/?op=lista%5Ftema&id=1&pag=0'  # Replace with the URL of the HTML page you want to scrape
