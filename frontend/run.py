from flask import Flask, request, render_template
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np
import requests
from urllib.parse import unquote

ROWS = 30

BASE_URL = 'http://localhost:8985/solr/news_articles_v3/select'  # SCHEMA 3

app = Flask(__name__)

SYNC_AFTER_N_REQUESTS = 100
nbrs_models = {
    'pos': None,
    'pos_docs': None,
    'neu': None,
    'neu_docs': None,
    'neg': None,
    'neg_docs': None,
    'counter': 0
}


def text_to_embedding(text, string=True):
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embedding = model.encode(text, convert_to_tensor=False).tolist()

    # Convert the embedding to the expected format
    if string:
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        return embedding_str
    else:
        return embedding


def solr_sentiment_knn_query(base_url, query, sentiment, rows=30):
    data = {
        "fl": "title,content,date,origin,id,sentiment,vector",
        "rows": 100000,
        "wt": "json"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    def train_model(data, headers):
        response = requests.post(base_url, data=data, headers=headers)
        response.raise_for_status()

        docs = response.json()['response']['docs']
        vectors = np.array([entry["vector"] for entry in docs])
        for doc in docs:
            del doc['vector']

        model = NearestNeighbors(n_neighbors=ROWS, algorithm='auto').fit(vectors)

        return docs, model

    global nbrs_models
    if sentiment == 'positive' and nbrs_models['pos'] is None:
        data['q'] = 'sentiment: [0.25 TO 1]'
        nbrs_models['pos_docs'], nbrs_models['pos'] = train_model(data, headers)
    elif sentiment == 'neutral' and nbrs_models['neu'] is None:
        data['q'] = 'sentiment: [-0.25 TO 0.25]'
        nbrs_models['neu_docs'], nbrs_models['neu'] = train_model(data, headers)
    elif sentiment == 'negative' and nbrs_models['neg'] is None:
        data['q'] = 'sentiment: [-1 TO -0.25]'
        nbrs_models['neg_docs'], nbrs_models['neg'] = train_model(data, headers)


    input_query = np.array(text_to_embedding(query, string=False))

    nearest_neighbors = {}
    if sentiment == 'positive':
        distances, indices = nbrs_models['pos'].kneighbors([input_query])
        nearest_neighbors = [nbrs_models['pos_docs'][i] for i in indices[0]]
    elif sentiment == 'neutral':
        distances, indices = nbrs_models['neu'].kneighbors([input_query])
        nearest_neighbors = [nbrs_models['neu_docs'][i] for i in indices[0]]
    elif sentiment == 'negative':
        distances, indices = nbrs_models['neg'].kneighbors([input_query])
        nearest_neighbors = [nbrs_models['neg_docs'][i] for i in indices[0]]

    nbrs_models['counter'] += 1

    if nbrs_models['counter'] > SYNC_AFTER_N_REQUESTS:
        nbrs_models = {
            'pos': None,
            'pos_docs': None,
            'neu': None,
            'neu_docs': None,
            'neg': None,
            'neg_docs': None,
            'counter': 0
        }

    return {
        'response': {
            'docs': nearest_neighbors
        }
    }


def solr_knn_query(base_url, embedding, rows=30):
    data = {
        "q": f"{{!knn f=vector topK={rows}}}{embedding}",
        "fl": "title,content,date,origin,id,sentiment",
        "rows": rows,
        "wt": "json"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(base_url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()


@app.route('/relatedContent/')
def relatedContent():
    document = unquote(request.query_string.decode('utf-8')).strip()
    print(document)

    response = solr_knn_query(BASE_URL, text_to_embedding(document), 4)

    return response['response']['docs']


@app.route('/solr/')
def solr():
    sentiment = request.args.get('sentiment')
    query = unquote(request.args.get('query')).strip()

    if sentiment == "":
        response = solr_knn_query(BASE_URL, text_to_embedding(query))
    else:
        response = solr_sentiment_knn_query(BASE_URL, query, sentiment)

    return response['response']['docs']


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
