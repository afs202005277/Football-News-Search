# SETUP
import copy
import time
import urllib

import matplotlib.pyplot as plt
from sklearn.metrics import PrecisionRecallDisplay
import numpy as np
import requests
import pandas as pd
from itertools import product

def convert_parameters_to_url(base_url, parameters):
    # Combine the base URL and parameters
    url_parts = list(urllib.parse.urlparse(base_url))
    url_parts[4] = urllib.parse.urlencode(parameters)
    final_url = urllib.parse.urlunparse(url_parts)

    return final_url

def thorough_analysis(title, content, **substitutes):
    keys = substitutes.keys()
    combinations = list(product(*substitutes.values()))

    to_be_tried = [None]
    for combination in combinations:
        content_copy = content
        for ind, k in enumerate(keys):
            content_copy = content_copy.replace(k, str(combination[ind]))
        to_be_tried.append({title: content_copy})

    return to_be_tried


BASE_URL = 'http://localhost:8983/solr/news_articles_v1/select'
ROWS = 30

QUERIES = [
    {
        "name": "Biggest Transfer 2019",
        "qrels_file": "qrels_files/v1/qrels_biggest_transfer.txt",
        "query": {
            "q": "content:\"transferencia\"\ntitle:milionaria",
            "indent": "true",
            "q.op": "OR",
            'fq': 'date:[2019-01-01T00:00:00Z TO 2019-12-31T00:00:00Z]',
            'qf': 'title^2 content^5',
            'pf': 'title~2 content~5',
            'rows': ROWS
            }
    },
    {
        "name": "Poor refereeing performance in important matches",
        "qrels_file": "qrels_files/v1/qrels_poor_referee_performance.txt",
        "query": {
            "q": "content: arbitragem erros jogo importante",
            "indent": "true",
            "q.op": "OR",
            'qf': 'title^2 content^5',
            'pf': 'title~2 content~5',
            'rows': ROWS
            }
    },
    {
        "name": "Visiting team scoring over three goals",
        "qrels_file": "qrels_files/v1/qrels_away_more_than_3_goals.txt",
        "query": {
            'q': 'title: vs AND title:\\-3 \\-4 \\-5 \\-6 \\-7 \\-8 \\-9 \\-10',
            "indent": "true",
            "q.op": "OR",
            'qf': 'title^2 content^5',
            'pf': 'title~2 content~5',
            'rows': ROWS
            }
    },
    {
        "name": "Benfica performance throughout matches",
        "qrels_file": "qrels_files/v1/qrels_benfica_performance.txt",
        "query": {
            'defType': 'edismax',
            'q': "title:Benfica AND content:(performance~ OR desempenho~ OR rendimento~)",
            'qf': 'title^2 content^5',
            'pf': 'title~2 content~5',
            'rows': ROWS
            }
    }
]

# Define metrics to be calculated
evaluation_metrics = {
    'ap': 'Average Precision',
    'p10': 'Precision at 10 (P@10)',
    'recall_at_n': 'Recall at 10 (R@10)',
    'f1': 'F1 Score',
    'mean_ap': 'Mean Average Precision',
    'r_precision': 'R-Precision',
    'mrr': 'Mean Reciprocal Rank',
    'p5': 'Precision at 5 (P@5)',
}

testing_parameters = [
    thorough_analysis('qf', 'title^X content^Y', X=range(6), Y=range(6)), #field boost
    thorough_analysis('pf', 'title~X content~Y', X=range(6), Y=range(6)), #fuzziness
    [{'q': '*'}], #wildcard
]

# METRICS TABLE
# Define custom decorator to automatically calculate metric based on key
metrics = {}
metric = lambda f: metrics.setdefault(f.__name__, f)


@metric
def ap(results, relevant):
    """Average Precision"""
    precision_values = []
    relevant_count = 0

    for idx, doc in enumerate(results):
        if doc['id'] in relevant:
            relevant_count += 1
            precision_at_k = relevant_count / (idx + 1)
            precision_values.append(precision_at_k)

    if not precision_values:
        return 0.0

    return sum(precision_values) / len(precision_values)


@metric
def p10(results, relevant, n=10):
    """Precision at N"""
    return len([doc for doc in results[:n] if doc['id'] in relevant]) / n


@metric
def recall_at_n(results, relevant, n=10):
    """Recall at N"""
    relevant_count = sum([1 for doc in results[:n] if doc['id'] in relevant])
    total_relevant = len(relevant)

    if total_relevant == 0:
        return 0.0

    return relevant_count / total_relevant


@metric
def f1(results, relevant):
    """F1 Score"""
    precision = calculate_metric('precision_at_n', results, relevant)
    recall = calculate_metric('recall_at_n', results, relevant)

    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)


@metric
def mean_ap(results, relevant):
    """Mean Average Precision"""
    precision_values = []
    relevant_count = 0

    for idx, doc in enumerate(results):
        if doc['id'] in relevant:
            relevant_count += 1
            precision_at_k = relevant_count / (idx + 1)
            precision_values.append(precision_at_k)

    if not precision_values:
        return 0.0

    return sum(precision_values) / len(precision_values)


@metric
def r_precision(results, relevant):
    """R-Precision"""
    return len([doc for doc in results[:len(relevant)] if doc['id'] in relevant]) / len(relevant)


@metric
def mrr(results, relevant):
    """Mean Reciprocal Rank"""
    for idx, doc in enumerate(results, start=1):
        if doc['id'] in relevant:
            return 1 / idx
    return 0.0


@metric
def p5(results, relevant, n=5):
    """Precision at 5"""
    return p10(results, relevant, n=n)


def calculate_metric(key, results, relevant):
    # Change 'precision_at_n' to 'p10'
    return metrics['p10'](results, relevant) if key == 'precision_at_n' else metrics[key](results, relevant)


def create_precision_recall_graph(query, precision_values, recall_values, save=False):
    precision_recall_match = {k: v for k, v in zip(recall_values, precision_values)}

    # Extend recall_values to include traditional steps for a better curve (0.1, 0.2 ...)
    recall_values_extended = sorted(set(recall_values + list(np.arange(0.1, 1.1, 0.1))))

    # Extend matching dict to include these new intermediate steps
    for step in recall_values_extended:
        if step not in precision_recall_match:
            closest_lower = max([s for s in precision_recall_match.keys() if s < step], default=None)
            closest_higher = min([s for s in precision_recall_match.keys() if s > step], default=None)

            if closest_lower is not None and closest_higher is not None:
                precision_recall_match[step] = (precision_recall_match[closest_lower] + precision_recall_match[
                    closest_higher]) / 2
            elif closest_lower is not None:
                precision_recall_match[step] = precision_recall_match[closest_lower]
            elif closest_higher is not None:
                precision_recall_match[step] = precision_recall_match[closest_higher]

    disp = PrecisionRecallDisplay([precision_recall_match.get(r) for r in recall_values], recall_values)
    disp.plot()
    if save:
        plt.savefig(f'metrics/precision_recall{"".join(query["name"].split(" "))}{int(time.time())}.pdf')

    return disp

def main():
    csv_content = []
    prec_recall_columns = 0

    combinations = list(product(*testing_parameters))
    for comb_ind, comb in enumerate(combinations):

        metrics_values = []

        for query_ind, query in enumerate(QUERIES):
            temp_query = copy.deepcopy(query)

            QRELS_FILE = query['qrels_file']

            # Read qrels to extract relevant documents
            relevant = list(map(lambda el: el.strip(), open(QRELS_FILE).readlines()))

            for param in comb:
                if param is None:
                    continue
                for key in param.keys():
                    if key == 'q':
                        temp_query['query']['q'] = temp_query['query']['q'].replace(' ', param[key] + ' ')
                    else:
                        temp_query['query'][key] = param[key]

            QUERY_URL = convert_parameters_to_url(BASE_URL, temp_query['query'])

            try:
                # Get query results from Solr instance
                response = requests.get(QUERY_URL)
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
                results = response.json()['response']['docs']
                if len(results) > prec_recall_columns:
                    prec_recall_columns = len(results)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching results for query {temp_query['name']}: {e}")
                continue  # Skip to the next query if there's an error

            # Calculate all metrics and export results as LaTeX table
            df = pd.DataFrame([['Metric', 'Value']] +
                              [
                                  [evaluation_metrics[m], calculate_metric(m, results, relevant)]
                                  for m in evaluation_metrics
                              ]
                              )

            # PRECISION-RECALL CURVE
            # Calculate precision and recall values as we move down the ranked list
            precision_values = [
                len([
                    doc
                    for doc in results[:idx]
                    if doc['id'] in relevant
                ]) / idx
                for idx, _ in enumerate(results, start=1)
            ]

            recall_values = [
                len([
                    doc for doc in results[:idx]
                    if doc['id'] in relevant
                ]) / len(relevant)
                for idx, _ in enumerate(results, start=1)
            ]

            temp = df.iloc[1:, 1].tolist()
            metrics_values.append(temp + precision_values + recall_values)

            """with open(f'metrics/results{"".join(query["name"].split(" "))}{time.time()}.tex', 'w') as tf:
                tf.write(df.to_latex())

            create_precision_recall_graph(query, precision_values, recall_values, save=True)"""

        if comb_ind % 10 == 0:
            print(f"{(query_ind + comb_ind * len(QUERIES)) / (len(combinations) * len(QUERIES)) * 100.0}% DONE")

        metrics_values = [str(sum(l)/len(l)) for l in list(zip(*metrics_values))]
        name = str(comb)
        csv_content.append(name + ';' + ';'.join(metrics_values) + '\n')

    with open(f'metrics/thorough_analysis{int(time.time())}.csv', 'w') as thorough_metrics_file:
        csv_columns = 'Metrics Tested' + ';' + ';'.join(evaluation_metrics.values()) + ';' + ';'.join([f'precision_w_{i}' for i in range(1, prec_recall_columns+1)]) + ';' + ';'.join([f'recall_w_{i}' for i in range(1, prec_recall_columns+1)]) + '\n'
        thorough_metrics_file.write(csv_columns)
        thorough_metrics_file.writelines(csv_content)




if __name__ == '__main__':
    main()
