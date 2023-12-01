from flask import Flask, request, render_template
import requests

app = Flask(__name__)

@app.route('/solr/')
def solr():
    query = request.query_string.decode('utf-8')
    response = requests.get(f'http://localhost:8983/solr/news_articles/select?{query}')
    response.raise_for_status()
    return response.json()['response']['docs']

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

