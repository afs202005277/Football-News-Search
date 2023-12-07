import json

import pandas as pd
from sentence_transformers import SentenceTransformer

from query_analysis import QUERIES, BASE_URL, convert_parameters_to_url, ROWS
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


def text_to_embedding(text):
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embedding = model.encode(text, convert_to_tensor=False).tolist()

    # Convert the embedding to the expected format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    return embedding_str


def solr_knn_query(base_url, embedding):
    data = {
        "q": f"{{!knn f=vector topK={ROWS}}}{embedding}",
        "fl": "title,content,date,origin,id",
        "rows": ROWS,
        "wt": "json"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(base_url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()


def get_excel_values(query):
    embedding = False
    try:
        if embedding:
            response = solr_knn_query(BASE_URL, text_to_embedding(query['query_name']))
            results = response['response']['docs']
        else:
            query_url = convert_parameters_to_url(BASE_URL, query['query'])
            response = requests.get(query_url)
            response.raise_for_status()
            results = response.json()['response']['docs']
        qrels = []

        with open(query['qrels_file'], 'r') as file:
            for line in file:
                qrels.append(int(line.strip()))

        with open('qrels_files/temp.json', 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
        sol = []
        for i in range(min(len(results), 60)):
            idx = int(results[i]['id'])
            if idx in qrels:
                sol.append(1)
            else:
                sol.append(0)

        return sol

    except requests.exceptions.RequestException as e:
        print(f"Error fetching results for query '{query['name']}': {e}")
        return


# get_best_boosts('metrics/thorough_analysis1699992951.csv')
for i in range(len(QUERIES)):
    print(get_excel_values(QUERIES[i]))
