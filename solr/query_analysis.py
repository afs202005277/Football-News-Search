# SETUP
import time

import matplotlib.pyplot as plt
from sklearn.metrics import PrecisionRecallDisplay
import numpy as np
import requests
import pandas as pd

# Search for testing is: (title: sporting vs benfica, origin: abola)

QUERIES = [
    {
        "name": "Biggest Transfer 2019",
        "qrels_file": "qrels_files/v1/qrels_biggest_transfer.txt",
        "query_url": "http://localhost:8983/solr/news_articles_v1/select?q=content:%22transferencia%22%0Atitle:milionaria&q.op=OR&indent=true&rows=30&fq=date:%5B2019-01-01T00:00:00Z%20TO%202019-12-31T00:00:00Z%5D&useParams="
    },
    {
        "name": "Poor refereeing performance in important matches",
        "qrels_file": "qrels_files/v1/qrels_poor_referee_performance.txt",
        "query_url": "http://localhost:8983/solr/news_articles_v1/select?q=content:%20arbitragem%20erros%20jogo%20importante&q.op=OR&indent=true&rows=30&useParams="
    },
    {
        "name": "Visiting team scoring over three goals",
        "qrels_file": "qrels_files/v1/qrels_away_more_than_3_goals.txt",
        "query_url": "http://localhost:8983/solr/news_articles_v1/select?indent=true&q.op=OR&q=title%3A%20vs%20AND%20title%3A%5C-3%20%5C-4%20%5C-5%20%5C-6%20%5C-7%20%5C-8%20%5C-9%20%5C-10&rows=30&useParams="
    },
    {
        "name": "Benfica performance throughout matches",
        "qrels_file": "qrels_files/v1/qrels_benfica_performance.txt",
        "query_url": "http://localhost:8983/solr/news_articles_v1/select?defType=edismax&q=title%3ABenfica+AND+content%3A%28performance~+OR+desempenho~+OR+rendimento~%29&wt=json&qf=title%5E1.0+content%5E1.0&rows=30"
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



def main():
    for query in QUERIES:

        QRELS_FILE = query['qrels_file']
        QUERY_URL = query['query_url']

        # Read qrels to extract relevant documents
        relevant = list(map(lambda el: el.strip(), open(QRELS_FILE).readlines()))

        try:
            # Get query results from Solr instance
            response = requests.get(QUERY_URL)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            results = response.json()['response']['docs']
        except requests.exceptions.RequestException as e:
            print(f"Error fetching results for query {query['name']}: {e}")
            continue  # Skip to the next query if there's an error

        # Calculate all metrics and export results as LaTeX table
        df = pd.DataFrame([['Metric', 'Value']] +
                          [
                              [evaluation_metrics[m], calculate_metric(m, results, relevant)]
                              for m in evaluation_metrics
                          ]
                          )

        with open(f'metrics/results{"".join(query["name"].split(" "))}{time.time()}.tex', 'w') as tf:
            tf.write(df.to_latex())

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
        plt.savefig(f'metrics/precision_recall{"".join(query["name"].split(" "))}{time.time()}.pdf')


if __name__ == '__main__':
    main()
