import time
from datetime import datetime
from time import sleep
from RateLimitedRequest import RateLimitedRequest

from bs4 import BeautifulSoup
import requests
import logging

BASE_URL = 'https://arquivo.pt/textsearch?'
logging.basicConfig(filename='ojogo.log', filemode='w', format='%(levelname)s - %(message)s')


def get_current_timestamp():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def fetch_all(request_params):
    tmp_list = [key + '=' + value + '&' for key, value in request_params.items()]
    final_url = BASE_URL + "".join(tmp_list)[:-1]
    used_links = set()
    limit_request = RateLimitedRequest()
    while True:
        has_items = False
        try:
            response = limit_request.get(final_url)
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
                        div_element = soup.find('div', {'data-ngx-name': 'description',
                                                        'class': 't-a-c-wrap js-select-and-share-1'})
                        if div_element is None:
                            logging.warning(f'Did not found the text of the {str(idx)}- {original_file_url}')
                        else:
                            print("SUCCESS: " + original_file_url)
                            text_list = [soup.select_one('header div h1').text]
                            for child in div_element.find_all(recursive=False):
                                if child.has_attr('role') and child['role'] == 'complementary':
                                    continue
                                text = child.get_text(strip=True)
                                text_list.append(text)
                            combined_text = ' '.join(text_list)
                            print(combined_text)
                            print("\n")
                    else:
                        logging.warning(f'Http status code title: ' + str(idx))
                if not has_items:
                    break
                else:
                    final_url = json_data['next_page']
                return True  # Indicate successful processing
            else:
                print(f"URL '{final_url}' does not return JSON data.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching URL '{final_url}': {e}")
    return False


def main():
    request_parameters = {
        'q': '',
        'to': get_current_timestamp(),
        'siteSearch': 'ojogo.pt',
        'maxItems': '2000',
        'prettyPrint': 'false'
    }
    fetch_all(request_parameters)


main()
