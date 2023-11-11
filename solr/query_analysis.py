# SETUP
import matplotlib.pyplot as plt
from sklearn.metrics import PrecisionRecallDisplay
import numpy as np
import json
import requests
import pandas as pd

# Search for testing is: (title: sporting vs benfica, origin: abola)

QUERIES = [
    {
        "name": "Biggest Transfer 2019",
        "qrels_file": "qrels_files/qrels_biggest_transfer.json",
        "query_url": "http://localhost:8983/solr/news_articles/select?q=content:%22transferencia%22%0Atitle:milionaria&q.op=OR&indent=true&rows=10&fq=date:%5B2019-01-01T00:00:00Z%20TO%202019-12-31T00:00:00Z%5D&useParams="
    },
    {
        "name": "Poor refereeing performance in important matches",
        "qrels_file": "qrels_files/qrels_poor_referee_performance.json",
        "query_url": "http://localhost:8983/solr/news_articles/select?q=content:%20arbitragem%20erros%20jogo%20importante&q.op=OR&indent=true&rows=30&useParams="
    },
    {   
        "name": "Visiting team scoring over three goals",
        "qrels_file": "qrels_files/qrels_away_more_than_3_goals.json",
        "query_url": "http://localhost:8983/solr/news_articles/select?indent=true&q.op=OR&q=title%3A%20vs%20AND%20title%3A%5C-3%20%5C-4%20%5C-5%20%5C-6%20%5C-7%20%5C-8%20%5C-9%20%5C-10&useParams="
    }
]

# Define metrics to be calculated
evaluation_metrics = {
    'ap': 'Average Precision',
    'p10': 'Precision at 10 (P@10)',
    'recall_at_10': 'Recall at 10 (R@10)',
    'f1': 'F1 Score',
    'map': 'Mean Average Precision',
    'ndcg': 'Normalized Discounted Cumulative Gain',
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
def map(results, relevant):
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
def ndcg(results, relevant):
    """Normalized Discounted Cumulative Gain"""
    ideal_order = sorted(relevant, key=lambda x: results.index(x))
    dcg = sum([(2**relevant_score - 1) / np.log2(rank + 1) for rank, relevant_score in enumerate(ideal_order)])
    idcg = sum([(2**1 - 1) / np.log2(rank + 1) for rank in range(1, len(relevant) + 1)])

    if idcg == 0:
        return 0.0

    return dcg / idcg


def calculate_metric(key, results, relevant):
    return metrics[key](results, relevant)


for query in QUERIES:

    QRELS_FILE = query['qrels_file']
    QUERY_URL = query['query_url']

    # Read qrels to extract relevant documents
    relevant = list(map(lambda el: el.strip(), open(QRELS_FILE).readlines()))
    # Get query results from Solr instance
    results = requests.get(QUERY_URL).json()['response']['docs']

    # Calculate all metrics and export results as LaTeX table
    df = pd.DataFrame([['Metric', 'Value']] +
                      [
                          [evaluation_metrics[m], calculate_metric(m, results, relevant)]
                          for m in evaluation_metrics
                      ]
                      )

    with open(f'metrics/results{"".join(query["name"].split(" "))}.tex', 'w') as tf:
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
    recall_values.extend([step for step in np.arange(0.1, 1.1, 0.1) if step not in recall_values])
    recall_values = sorted(set(recall_values))

    # Extend matching dict to include these new intermediate steps
    for idx, step in enumerate(recall_values):
        if step not in precision_recall_match:
            if recall_values[idx - 1] in precision_recall_match:
                precision_recall_match[step] = precision_recall_match[recall_values[idx - 1]]
            else:
                precision_recall_match[step] = precision_recall_match[recall_values[idx + 1]]

    disp = PrecisionRecallDisplay([precision_recall_match.get(r) for r in recall_values], recall_values)
    disp.plot()
    plt.savefig(f'metrics/precision_recall{"".join(query["name"].split(" "))}.pdf')
