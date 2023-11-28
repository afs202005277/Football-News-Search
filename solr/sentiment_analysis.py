from nltk.sentiment import SentimentIntensityAnalyzer
import json

import nltk

nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()


def load_translation_data():
    f = open('./translations.json', 'r').read()
    return json.loads(f)

def load_data():
    f = open('./data.json', 'r').read()
    return json.loads(f)

def save_data(data):
    with open('./data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def analyze_sentiment(document):
    return sia.polarity_scores(document['content'])


def sentiment_analysis():
    translated_data = load_translation_data()
    real_data = load_data()
    for real_doc_id, document in enumerate(real_data):
        doc_id = document['id']
        r = analyze_sentiment(translated_data[doc_id])
        document['sentiment'] = r['compound']
        real_data[real_doc_id] = document

    save_data(real_data)


from documents_translate_to_en import translate_data

translate_data()
print("ALL FILES TRANSLATED")
sentiment_analysis()
print("SENTIMENT ANALYSIS ADDED TO DATA.JSON")