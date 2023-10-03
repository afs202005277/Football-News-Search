import sqlite3
import os

SCHEMA = '../db/schema.sql'
DB_PATH = '../db/db.sqlite'

class DB:
    def __init__(self):
        # Run schema if db doesn't exists
        run_schema = not os.path.exists(DB_PATH)

        # Create or open databas
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
        self.instance.execute('INSERT INTO new(title, content, timestamp, origin) VALUES(?, ?, ?, ?)', data)
        self.instance.commit()

    def close(self):
        self.instance.close()
        print('Database closed.')