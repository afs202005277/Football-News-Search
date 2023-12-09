from flask import Flask, request, render_template
from sentence_transformers import SentenceTransformer
import requests
from urllib.parse import unquote

ROWS = 30

BASE_URL = 'http://localhost:8985/solr/news_articles_v3/select'  # SCHEMA 3

app = Flask(__name__)


def text_to_embedding(text):
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    embedding = model.encode(text, convert_to_tensor=False).tolist()

    # Convert the embedding to the expected format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    return embedding_str


def solr_knn_query(base_url, embedding, rows=30):
    data = {
        "q": f"{{!knn f=vector topK={rows}}}{embedding}",
        "fl": "title,content,date,origin,id",
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
    query = unquote(request.query_string.decode('utf-8')).strip()
    print(query)

    response = solr_knn_query(BASE_URL, text_to_embedding(query))
    return response['response']['docs']

    """
    query = request.query_string.decode('utf-8')
    response = requests.get(f'http://localhost:8983/solr/news_articles/select?{query}')
    response.raise_for_status()
    return response.json()['response']['docs']
    """


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
