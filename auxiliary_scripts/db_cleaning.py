import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(f'{ROOT_DIR}/../scraping/db')

from db import DB

db = DB()

db.clear_articles()

db.clear_games()

db.close()