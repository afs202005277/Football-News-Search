from scraping.db.db import DB
import numpy as np
import nltk
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# Download the Portuguese stopwords if you haven't already
nltk.download('stopwords')


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
    return ['Porto']


def create_most_popular_teams(db):
    teams = fetch_teams()
    results = {team: 0 for team in teams}
    cursor = db.get_cursor()
    query = "SELECT title, contents FROM new LIMIT ? OFFSET ?"

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
                if team.lower() in title.lower() or team.lower() in contents.lower():
                    results[team] += 1
        offset += batch_size
    return results


def create_most_popular_team_plot(db):
    data = create_most_popular_teams(db)
    plt.figure(figsize=(10, 6))
    plt.bar(data.keys(), data.values())
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
            query = f"SELECT contents FROM {table} LIMIT ? OFFSET ?"
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


def numeric_stats(db):
    data = dict()
    data['Amount of news articles'] = db.count_rows('new')
    data['Amount of wikipedia descriptions'] = db.count_rows('team_info')
    data['Amount of game reports'] = db.count_rows('game_reports')
    data['Average amount of words per text'] = calculate_average_words_per_content(db, ["new", "game_reports", "team_info"])

    plt.figure(figsize=(10, 6))
    plt.bar(data.keys(), data.values())
    plt.xlabel("Data Type")
    plt.ylabel("Count / Average Words")
    plt.title("Data Summary")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Show the plot
    plt.show()



def main():
    db = DB()
    distribution_by_year_and_website(db)
    create_wordcloud(db.retrieve_text_for_wordcloud())
    create_most_popular_team_plot(db)
    db.close()


if __name__ == '__main__':
    main()
