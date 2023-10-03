from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
import sys

sys.path.append("../")
from utils import *

target_text = ""


def has_no_seta_id(tag):
    return tag.has_attr('class') and 'linkNoticias' in tag['class'] and 'seta' not in tag.get('id', '')


def contains_text(element):
    return target_text in element.get_text()


def get_current_timestamp():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def parser1(links, url):
    final = []
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
    return final


def parser2(soup, url, find_more):
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
            response = requests.get(new_link)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            final += parser2(soup, new_link, False)

    return final


def parse_text(url):
    global target_text
    final = []
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request was not successful

        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', {'class': 'dg'}, recursive=True)
        if len(links) != 0:
            final += parser1(links, url)
        elif soup.select('table[id*="Noticia"]'):
            final += parser2(soup, url, True)
        else:
            print("Unknown HTML: " + url)
    except Exception as e:
        print(f"An error occurred: {e}")
    return final


def main():
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
    all_data = []
    start_date = datetime.strptime(request_parameters['from'], "%Y%m%d%H%M%S")
    current_time = datetime.now()

    # Define a timedelta representing one month (approx. 30.44 days)
    one_month = timedelta(days=30.44)

    # Loop until the start_date is less than the current_time
    while start_date < current_time:
        while True:
            link = build_api_request(request_parameters)
            print("Major request: " + link)
            all_urls = requests.get(link)
            if all_urls.headers.get("content-type") == "application/json":
                json_data = all_urls.json()
                for idx, json_object in enumerate(json_data['response_items']):
                    all_data += parse_text(json_object['linkToNoFrame'])
                    print(len(all_data))
                if len(json_data['response_items']) == 0:
                    break
                request_parameters['offset'] = str(int(request_parameters['offset']) + len(json_data['response_items']))

        # Add one month to the start_date
        start_date += one_month
        request_parameters['from'] = start_date.strftime("%Y%m%d%H%M%S")
        request_parameters['to'] = (start_date + one_month).strftime("%Y%m%d%H%M%S")

    return all_data


data = main()
print()
# url = 'https://arquivo.pt/noFrame/replay/20081021111623/http://abola.pt/nnh/ver.aspx?id=150881'  # Replace with the URL of the HTML page you want to scrape
# print(parse_text(url))
# 2194
