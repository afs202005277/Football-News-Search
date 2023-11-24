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

QUERIES = [
    {
        "name": "Biggest Transfer 2019",
        "qrels_file": "qrels_files/transfer.txt",
        "query": {
            "q": "content:\"transferencia\"\ntitle:milionaria",
            "q.op": "OR",
            'fq': 'date:[2019-01-01T00:00:00Z TO 2019-12-31T00:00:00Z]',
            'rows': 30
            }
    },
    {
        "name": "Poor refereeing performance in important matches",
        "qrels_file": "qrels_files/arb.txt",
        "query": {
            "q": "content: arbitragem erros jogo importante",
            "q.op": "OR",
            'rows': 30
            }
    },
    {
        "name": "Visiting team scoring over three goals",
        "qrels_file": "qrels_files/3_goals.txt",
        "query": {
            'q': 'title: vs AND title:\\-3 \\-4 \\-5 \\-6 \\-7 \\-8 \\-9 \\-10',
            "q.op": "OR",
            'rows': 60
            }
    },
    {
        "name": "Benfica performance throughout matches",
        "qrels_file": "qrels_files/benfica.txt",
        "query": {
            'q': "title:Benfica AND content:(performance OR desempenho OR rendimento)",
            "q.op": "OR",
            'rows': 30
            }
    }
]

def find_best_booster(queries):

    combs = [
    thorough_analysis('qf', 'title^X content^Y', X=range(6), Y=range(6)), #field boost
    thorough_analysis('pf', 'title~X content~Y', X=range(6), Y=range(6)), #fuzziness
    ]

    best_acc = 0
    best_qf = None
    best_pf = None

    curr = 1
    for qf in combs[0]:
        for  pf in combs[1]:
            print(f'[{curr} / {len(combs[0]) * len(combs[1])}]')
            curr += 1
            average_precision = []
            for query in queries:
                if qf != None:
                    query['query']['qf'] = qf['qf']
                if pf != None:
                    query['query']['pf'] = pf['pf']
                vals = get_excel_values(query)
                precisions = []
                for i in range(1, len(vals)):
                    sub_list = vals[:i]
                    precisions.append(sum(sub_list) / i)

                average_precision.append(sum(precisions) / len(precisions))

            mean_average_precision = sum(average_precision) / len(queries)
            if mean_average_precision > best_acc:
                best_acc = mean_average_precision
                best_qf = qf
                best_pf = pf
                print(f'Current Best: {best_acc}')

    print(f'Best Precision: {best_acc} with ({best_qf}) ({best_pf})')



find_best_booster(QUERIES)