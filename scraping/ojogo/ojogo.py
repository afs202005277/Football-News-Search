import sqlite3
import time
from datetime import datetime
from time import sleep
from RateLimitedRequest import RateLimitedRequest
import sys
from bs4 import BeautifulSoup
import requests
import logging
sys.path.append('../db/')
sys.path.append('../')
from db import DB
from utils import *

logging.basicConfig(filename='ojogo.log', filemode='w', format='%(levelname)s - %(message)s')




def fetch_all(request_params):
    counter = 0
    offset = 0
    database = DB()
    final_url = build_api_request(request_params)
    used_links = set()
    limit_request = RateLimitedRequest()
    while True:
        has_items = False
        try:
            response = limit_request.get(final_url)
            print(final_url)
            if response.headers.get("content-type") == "application/json":
                json_data = response.json()
                for idx, json_object in enumerate(json_data['response_items']):
                    has_items = True
                    if (len(json_object['title']) < 4 or not (json_object['title'][3] == ' ' and json_object['title'][
                                                                                                 :3].isdigit())) and 'linkToNoFrame' in json_object:
                        original_file_url = json_object['linkToNoFrame']
                        if original_file_url in used_links:
                            continue
                        else:
                            used_links.add(original_file_url)
                        original_file_response = limit_request.get(original_file_url)
                        original_file_response.raise_for_status()

                        soup = BeautifulSoup(original_file_response.text, 'html.parser')
                        div_element = soup.find('div', {'class': 't-a-c-wrap js-select-and-share-1'})
                        if div_element is None:
                            logging.warning(f'Did not found the text of the {str(idx)}- {original_file_url}')
                        else:
                            # print(json_object['tstamp'])
                            print("SUCCESS: " + original_file_url)
                            text_list = [soup.select_one('header div h1').text]
                            for child in div_element.find_all(recursive=False):
                                if child.has_attr('role') and child['role'] == 'complementary':
                                    continue
                                text = child.get_text(strip=True)
                                text_list.append(text)
                            combined_text = ' '.join(text_list)
                            #print(combined_text)
                            #print("\n")
                            counter += 1
                            try:
                                database.insert_new(
                                    (text_list[0], "" if len(text_list) == 1 else ' '.join(text_list[1:])))
                            except sqlite3.IntegrityError as e:
                                logging.warning(f'File already existed in database: ' + str(idx))
                    else:
                        logging.warning(f'Http status code title: ' + str(idx))
                if not has_items:
                    break
                else:
                    if 'offset' in final_url:
                        print('-------------')
                        print('CHANGING PAGE')
                        print('Prev: ' + final_url)
                        prev_offset = int(final_url[final_url.rfind('=') + 1:])
                        final_url = final_url[:final_url.rfind('=') + 1] + str(
                            len(json_data['response_items']) + prev_offset)
                        print('After: ' + final_url)
                        print('-------------')
                    else:
                        print('-------------')
                        print('CHANGING PAGE')
                        print('Prev: ' + final_url)
                        final_url += '&offset=' + str(len(json_data['response_items']))
                        print('After: ' + final_url)
                        print('-------------')
            else:
                print(f"URL '{final_url}' does not return JSON data.")

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching URL '{final_url}': {e}")
    print(counter)
    database.close()


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
    fetch_all(request_parameters)


main()
