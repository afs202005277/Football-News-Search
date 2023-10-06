import sqlite3
import os

import os

ROOT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)
SCHEMA = f'{ROOT_DIR}/schema.sql'
DB_PATH = f'{ROOT_DIR}/db.sqlite'


class DB:
    def __init__(self):
        # Run schema if db doesn't exists
        run_schema = not os.path.exists(DB_PATH)

        # Create or open database
        self.instance = sqlite3.connect(DB_PATH)
        cursor = self.instance.cursor()

        if run_schema:
            with open(SCHEMA, 'r') as sql_file:
                queries = sql_file.read()

            for statement in queries.split(';'):
                if statement.strip():
                    cursor.execute(statement)

            self.instance.commit()
            print("Database created and tables added.")
        print('Database initialized.')

    def insert_new(self, data):
        self.instance.execute('INSERT INTO new(title, content, publish_date, origin) VALUES(?, ?, ?, ?)', data)
        self.instance.commit()

    def insert_new_wiki(self, data):
        self.instance.execute('INSERT INTO team_info(name, content) VALUES(?, ?)', data)
        self.instance.commit()

    def insert_new_game_report(self, data):
        self.instance.execute('INSERT INTO game_reports(home, away, result, date, content) VALUES(?, ?, ?, ?, ?)', data)
        self.instance.commit()

    def count_rows(self, table_name):
        cursor = self.instance.cursor()
        cursor.execute('SELECT COUNT(*) FROM ' + table_name)
        count = cursor.fetchone()[0]
        return count

    def retrieve_data_distribution(self):
        cursor = self.instance.cursor()
        cursor.execute("SELECT publish_date, origin FROM new")
        return cursor.fetchall()

    def retrieve_text_for_wordcloud(self):
        cursor = self.instance.cursor()
        text = ''
        cursor.execute("SELECT content FROM new")
        text += ' '.join(row[0] for row in cursor.fetchall())
        cursor.execute("SELECT content FROM team_info")
        text += ' '.join(row[0] for row in cursor.fetchall())
        cursor.execute("SELECT content FROM game_reports")
        text += ' '.join(row[0] for row in cursor.fetchall())
        return text

    def close(self):
        self.instance.close()
        print('Database closed.')
