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


def main():
    db = DB()
    num_news_articles = db.count_rows('new')
    num_wikipedia_descriptions = db.count_rows('team_info')
    num_game_reports = db.count_rows('game_reports')
    distribution_by_year_and_website(db)
    create_wordcloud(db.retrieve_text_for_wordcloud())
    db.close()


if __name__ == '__main__':
    main()
