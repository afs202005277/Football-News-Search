import csv
from unidecode import unidecode
from scraping.db.db import DB
import numpy as np
import nltk
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import spacy

# Download the Portuguese stopwords if you haven't already
nltk.download('stopwords')
nlp = spacy.load("pt_core_news_lg")


def extract_year(date_string):
    return date_string[-4:]


def analyze_article_distribution_by_year_and_newspaper(db):
    years = {}
    newspapers = set()

    data = db.retrieve_data_distribution()
    for row in data:
        year = extract_year(row[0])
        newspaper = row[1]
        if year not in years:
            years[year] = {}
        if newspaper not in years[year]:
            years[year][newspaper] = 0
        years[year][newspaper] += 1
        newspapers.add(newspaper)
    return years, newspapers


def distribution_by_year_and_website(db):
    article_distribution, newspapers = analyze_article_distribution_by_year_and_newspaper(db)
    newspapers = sorted(newspapers)

    years = sorted(article_distribution.keys())
    data = {newspaper: [article_distribution[year].get(newspaper, 0) for year in years] for newspaper in newspapers}

    # Create a bar plot
    fig, ax = plt.subplots(figsize=(12, 6))
    width = 0.2  # Width of each bar

    x = np.arange(len(years))

    for i, newspaper in enumerate(newspapers):
        x_pos = x + i * width
        ax.bar(x_pos, data[newspaper], width=width, label=newspaper)

    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Articles')
    ax.set_title('Distribution of News Articles by Year and Newspaper')
    ax.set_xticks(x + (len(newspapers) - 1) * width / 2)
    ax.set_xticklabels(years)
    ax.legend(title='Newspaper')

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def create_wordcloud(text):
    stopwords = set(nltk.corpus.stopwords.words('portuguese'))
    stopwords.add("N")
    text = text.replace('\r', ' ')
    text = text.replace('\n', ' ')
    wordcloud = WordCloud(width=800, height=400, stopwords=stopwords, background_color='white').generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title("Word Cloud")
    plt.show()


def fetch_teams():
    file_name = 'game_reports.csv'
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    teams = set()

    for line in lines:
        csv_reader = csv.reader([line])
        parsed_line = next(csv_reader)
        teams.add(parsed_line[0])
        teams.add(parsed_line[1])
    return teams


def create_most_popular_teams(db):
    teams = fetch_teams()
    results = {team: 0 for team in teams}

    cursor = db.get_cursor()
    query = "SELECT title, content FROM article LIMIT ? OFFSET ?"

    batch_size = 100
    offset = 0

    while True:
        cursor.execute(query, (batch_size, offset))
        batch_rows = cursor.fetchall()
        if not batch_rows:
            break

        for row in batch_rows:
            title, contents = row
            for team in teams:
                if unidecode(team.lower()) in unidecode(title.lower()) or unidecode(team.lower()) in unidecode(
                        contents.lower()):
                    results[team] += 1
        offset += batch_size
    return results


def create_most_popular_team_plot(db):
    data = create_most_popular_teams(db)
    sorted_team_dict = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    plt.figure(figsize=(15, 6))
    plt.bar(sorted_team_dict.keys(), sorted_team_dict.values())
    plt.xlabel("Team")
    plt.ylabel("Count")
    plt.title("Mentions of Teams in News Articles")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def calculate_average_words_per_content(db, tables):
    total_words = 0
    total_contents = 0
    cursor = db.get_cursor()
    batch_size = 100
    offset = 0
    for table in tables:
        while True:
            query = f"SELECT content FROM {table} LIMIT ? OFFSET ?"
            cursor.execute(query, (batch_size, offset))
            batch_rows = cursor.fetchall()
            if not batch_rows:
                break
            for row in batch_rows:
                contents = row[0]
                total_words += len(contents.split())
                total_contents += 1
            offset += batch_size
        offset = 0
    if total_contents > 0:
        average_words_per_content = total_words / total_contents
    else:
        average_words_per_content = 0

    return average_words_per_content


def numeric_stats(db, tables):
    data = dict()
    data['Amount of news articles'] = db.count_rows('article')
    data['Amount of wikipedia descriptions'] = db.count_rows('team_info')
    data['Amount of game reports'] = db.count_rows('game_report')
    data['Average amount of words per text'] = calculate_average_words_per_content(db, tables)
    data['Number of articles from Record'] = db.get_num_articles('record')
    data['Number of articles from O Jogo'] = db.get_num_articles('ojogo')
    data['Number of articles from A Bola'] = db.get_num_articles('abola')

    plt.figure(figsize=(20, 6))
    plt.bar(data.keys(), data.values())
    for i, value in enumerate(data.values()):
        s = str(value)
        if isinstance(value, float):
            s = f'{value:.2f}'
        plt.text(i, value, s, ha='center', va='bottom')

    plt.xlabel("Data Type")
    plt.ylabel("Count / Average Words")
    plt.title("Data Summary")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Show the plot
    plt.show()


def most_popular_entities(db):
    cursor = db.get_cursor()
    batch_size = 100
    offset = 0
    queries = [f"SELECT title, content FROM article LIMIT ? OFFSET ?",
               f"SELECT name, content FROM team_info LIMIT ? OFFSET ?",
               f"SELECT home, away, content FROM game_report LIMIT ? OFFSET ?"]
    entity_counts = {}
    for query in queries:
        while True:
            cursor.execute(query, (batch_size, offset))
            batch_rows = cursor.fetchall()
            if not batch_rows:
                break
            for row in batch_rows:
                doc = nlp("\n".join(row))
                for ent in doc.ents:
                    entity_text = ent.text
                    entity_type = ent.label_
                    if entity_text not in entity_counts:
                        entity_counts[entity_text] = {"type": entity_type, "count": 1}
                    else:
                        entity_counts[entity_text]["count"] += 1
            offset += batch_size
        offset = 0
    return entity_counts


def most_popular_entities_plot(db):
    data = most_popular_entities(db)
    top_n = 20

    sorted_data = sorted(data.items(), key=lambda x: x[1]['count'], reverse=True)
    top_entities = sorted_data[:top_n]

    entities = [entity for entity, info in top_entities]
    counts = [info['count'] for entity, info in top_entities]

    plt.figure(figsize=(15, 6))
    plt.bar(entities, counts)
    plt.xlabel('Entities')
    plt.ylabel('Count')
    plt.title('Top {} Most Popular Entities'.format(top_n))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def main():
    db = DB()
    tables = ["article", "game_report", "team_info"]
    distribution_by_year_and_website(db)
    create_wordcloud(db.retrieve_text_for_wordcloud())
    create_most_popular_team_plot(db)
    numeric_stats(db, tables)
    most_popular_entities_plot(db)
    db.close()


if __name__ == '__main__':
    main()
