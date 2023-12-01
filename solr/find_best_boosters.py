# SETUP
import copy
import time
import urllib

import numpy as np
import requests
import pandas as pd
from itertools import product
from query_analysis import BASE_URL, convert_parameters_to_url, thorough_analysis
from excel_analysis import get_excel_values
import itertools
import threading


def getQuery(query, b1, b2, f1, f2):
    # 1 - TITLE | 2 - CONTENT
    if query['name'] == "Biggest Transfer 2019":
        return {
            "name": "Biggest Transfer 2019",
            "qrels_file": "qrels_files/transfer.txt",
            "query": {
                "q": f"content:\"transferencia\"~{f2}^{b2}\ntitle:milionaria~{f1}^{b1}",
                "q.op": "OR",
                'fq': 'date:[2019-01-01T00:00:00Z TO 2019-12-31T00:00:00Z]',
                'rows': 30
                }
        }
    elif query['name'] == "Poor refereeing performance in important matches":
        return {
            "name": "Poor refereeing performance in important matches",
            "qrels_file": "qrels_files/arb.txt",
            "query": {
                "q": f"content: arbitragem erros jogo importante~{f2}^{b2}",
                "q.op": "OR",
                'rows': 30
                }
        }
    elif query['name'] == "Visiting team scoring over three goals": 
        return {
            "name": "Visiting team scoring over three goals",
            "qrels_file": "qrels_files/3_goals.txt",
            "query": {
                'q': f'title: vs AND title:\\-3 \\-4 \\-5 \\-6 \\-7 \\-8 \\-9 \\-10',
                "q.op": "OR",
                'rows': 60
                }
        }
    elif query['name'] == "Benfica performance throughout matches":
        return {
            "name": "Benfica performance throughout matches",
            "qrels_file": "qrels_files/benfica.txt",
            "query": {
                'q': f"title:Benfica~{f1}^{b1} AND content:performance~{f2}^{b2} OR desempenho~{f2}^{b2} OR rendimento~{f2}^{b2}",
                "q.op": "OR",
                'rows': 30
                }
        }

QUERIES = [
    {
        "name": "Biggest Transfer 2019",
    },
    {
        "name": "Poor refereeing performance in important matches",
    },
    {
        "name": "Visiting team scoring over three goals",
    },
    {
        "name": "Benfica performance throughout matches",
    }
]

def process_combinations(queries, combs_part):
    best_acc = 0
    best_b1 = None
    best_b2 = None
    best_f1 = None
    best_f2 = None
    curr = 0
    for title_fuzz, content_fuzz, title_boost, content_boost in combs_part:

        print(f'[{curr} / 1000] [{title_fuzz}, {content_fuzz}, {title_boost}, {content_boost}] best: [{best_f1}, {best_f2}, {best_b1}, {best_b2}]')
        curr += 1
        average_precision = []
        for query in queries:

            query = getQuery(query, title_boost, content_boost, title_fuzz, content_fuzz)
            vals = get_excel_values(query)
            precisions = []
            for i in range(1, len(vals)):
                sub_list = vals[:i]
                precisions.append(sum(sub_list) / i)

            average_precision.append(sum(precisions) / len(precisions))

        mean_average_precision = sum(average_precision) / len(queries)
        if mean_average_precision > best_acc:
            best_acc = mean_average_precision
            best_b1 = title_boost
            best_b2 = content_boost
            best_f1 = title_fuzz
            best_f2 = content_fuzz
            print(f'Current Best: {best_acc}')

def find_best_booster(queries):


    best_acc = 0
    best_b1 = None
    best_b2 = None
    best_f1 = None
    best_f2 = None

    curr = 1
    combs = list(itertools.product(range(10), range(10), range(10), range(10)))

    # Number of threads
    num_threads = 10

    # Split combinations into chunks for each thread
    chunk_size = len(combs) // num_threads
    combs_chunks = [combs[i:i + chunk_size] for i in range(0, len(combs), chunk_size)]

    # Create threads
    threads = []
    for chunk in combs_chunks:
        thread = threading.Thread(target=process_combinations, args=(queries,chunk))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()



find_best_booster(QUERIES)