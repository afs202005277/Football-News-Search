import pandas as pd

from query_analysis import QUERIES, BASE_URL, convert_parameters_to_url
import requests


def get_best_boosts(file_path):
    df = pd.read_csv(file_path, sep=";")
    df = df.sort_values(by='Average Precision', ascending=False)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', None)
    print(df[['Metrics Tested']].iloc[0])


def get_excel_values(query):
    try:
        query_url = convert_parameters_to_url(BASE_URL, query['query'])

        print(query_url)

        response = requests.get(query_url)
        response.raise_for_status()
        results = response.json()['response']['docs']
        qrels = []


        with open(query['qrels_file'], 'r') as file:
            for line in file:
                qrels.append(int(line.strip()))

        sol = []
        for i in range(min(len(results), 30)):
            idx = int(results[i]['id'])
            if idx in qrels:
                sol.append(1)
            else:
                sol.append(0)

        print(sol)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching results for query '{query['name']}': {e}")
        return

#get_best_boosts('metrics/thorough_analysis1699992951.csv')
get_excel_values(QUERIES[3])