import json

from scraping.db.db import DB
import nltk
from nltk.corpus import stopwords


def main(db):
    articles, columns = db.fetch_articles()

    data = []
    for article in articles:
        tmp_row = dict(zip(columns, article))
        new_dict = dict()
        new_dict['title'] = tmp_row['title']
        new_dict['content'] = tmp_row['content']
        new_dict['date'] = tmp_row['publish_date']
        new_dict['origin'] = tmp_row['origin']
        data.append(new_dict)

    reports, columns = db.fetch_game_reports()
    for report in reports:
        tmp_row = dict(zip(columns, report))
        new_dict = dict()
        new_dict['title'] = tmp_row['home'] + ' vs ' + tmp_row['away'] + ": " + (
            (tmp_row[tmp_row['result']] + ' Wins!') if tmp_row['result'] != 'draw' else 'Draw.')
        new_dict['content'] = tmp_row['content']
        new_dict['date'] = (tmp_row['date'].replace('.', '-'))[:tmp_row['date'].find(' ')]
        new_dict['origin'] = 'kaggle'
        data.append(new_dict)

    with open('../solr/data.json', 'w', encoding='iso-8859-1') as json_file:
        json.dump(data, json_file, indent=4)

    nltk.download("stopwords")

    stop_words_portuguese = stopwords.words("portuguese")

    with open("../solr/stopwords.txt", "w") as file:
        for word in stop_words_portuguese:
            file.write(word + "\n")
    return data


if __name__ == '__main__':
    main(DB())

# momentos decisivos de 1 jogador
# maior transferencia MONETARIA
# jogos com mais de 3 golos da equipa visitante
