from datetime import datetime

BASE_URL = 'https://arquivo.pt/textsearch?'


def get_current_timestamp():
    return datetime.now().strftime('%Y%m%d%H%M%S')


def build_api_request(params):
    tmp_list = [key + '=' + value + '&' for key, value in params.items()]
    final_url = BASE_URL + "".join(tmp_list)[:-1]
    return final_url


def convert_to_uniform_date(date):
    date = date[:len("0000-00-00")]
    res = date
    if date[2] != '-':  # YYYY-MM-DD format
        year, month, day = date.split('-')
        res = f"{day}-{month}-{year}"
    return res
