# SETUP
import matplotlib.pyplot as plt
from sklearn.metrics import PrecisionRecallDisplay
import numpy as np
import json
import requests
import pandas as pd
import urllib.parse


def convert_parameters_to_url(base_url, parameters):
    # Combine the base URL and parameters
    url_parts = list(urllib.parse.urlparse(base_url))
    url_parts[4] = urllib.parse.urlencode(parameters)
    final_url = urllib.parse.urlunparse(url_parts)

    return final_url


QRELS_FILE = "information_systems_qrels.txt"
parameters1 = {
    'defType': 'edismax',
    'q': 'informação',
    'wt': 'json',
    'qf': " ".join(
        map(lambda x: x[0] + '^' + str(x[1]), [('title', 1.0), ('objectives', 1.0), ('learning_outcomes', 1.0)]))
}
# https://solr.apache.org/guide/8_3/function-queries.html#termfreq-function
parameters2 = {
    'defType': 'edismax',
    'q': 'informação',
    'wt': 'json',
    'qf': " ".join(
        map(lambda x: x[0] + '^' + str(x[1]), [('title', 1.0), ('objectives', 1.0), ('learning_outcomes', 1.0)])),
    'bq': 'title:informação^2.0',
    'bf': 'if(gt(termfreq(dados,\'title\'),0),2,1)'
}
parameters3 = {
    'defType': 'edismax',
    'q': 'title:Benfica AND content:(performance~ OR desempenho~ OR rendimento~)',
    'wt': 'json',
    'qf': " ".join(map(lambda x: x[0] + '^' + str(x[1]), [('title', 1.0), ('content', 1.0)])),
    'rows': '30'
}

parameters3 = {
    'q': "content:transferencia title:milionaria ",
    'wt': 'json',
    'rows': '60'
}

BASE_URL = 'http://localhost:8984/solr/news_articles_v2/select'
QUERY_URL = convert_parameters_to_url(BASE_URL, parameters3)
print(QUERY_URL)
exit(0)

# Read qrels to extract relevant documents
relevant = list(map(lambda el: el.strip(), open(QRELS_FILE).readlines()))
# Get query results from Solr instance
request = requests.get(QUERY_URL).json()
try:
    results = request['response']['docs']
except KeyError as e:
    print("ERROR: " + str(e))
finally:
    print(json.dumps(request, indent=4))

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


def calculate_metric(key, results, relevant):
    return metrics[key](results, relevant)


# Define metrics to be calculated
evaluation_metrics = {
    'ap': 'Average Precision',
    'p10': 'Precision at 10 (P@10)'
}

# Calculate all metrics and export results as LaTeX table
df = pd.DataFrame([['Metric', 'Value']] +
                  [
                      [evaluation_metrics[m], calculate_metric(m, results, relevant)]
                      for m in evaluation_metrics
                  ]
                  )

with open('results.tex', 'w') as tf:
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
plt.savefig('precision_recall.pdf')
