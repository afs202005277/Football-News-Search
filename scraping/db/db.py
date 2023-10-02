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
        self.instance.execute('INSERT INTO new(title, content) VALUES(?, ?)', data)
        self.instance.commit()

    def insert_new_wiki(self, data):
        self.instance.execute('INSERT INTO team_info(name, content) VALUES(?, ?)', data)
        self.instance.commit()


    def close(self):
        self.instance.close()
        print('Database closed.')