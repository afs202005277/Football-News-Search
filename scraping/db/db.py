import sqlite3

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA = f'{ROOT_DIR}/schema.sql'
DB_PATH = f'{ROOT_DIR}/merged_db.sqlite'


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
        self.instance.execute('INSERT INTO article(title, content, publish_date, origin) VALUES(?, ?, ?, ?)', data)
        self.instance.commit()

    def insert_new_wiki(self, data):
        self.instance.execute('INSERT INTO team_info(name, content) VALUES(?, ?)', data)
        self.instance.commit()

    def insert_new_game_report(self, data):
        self.instance.execute('INSERT INTO game_report(home, away, result, date, content, home_goals, away_goals) VALUES(?, ?, ?, ?, ?, ?, ?)', data)
        self.instance.commit()

    def clear_articles(self):
        self.instance.execute("DELETE FROM article WHERE TRIM(content) = ''")
        self.instance.commit()

    def count_rows(self, table_name):
        cursor = self.instance.cursor()
        cursor.execute('SELECT COUNT(*) FROM ' + table_name)
        count = cursor.fetchone()[0]
        return count

    def retrieve_data_distribution(self):
        cursor = self.instance.cursor()
        cursor.execute("SELECT publish_date, origin FROM article")
        return cursor.fetchall()

    def fetch_articles(self):
        cursor = self.instance.cursor()
        cursor.execute("SELECT * FROM article")
        return cursor.fetchall(), [desc[0] for desc in cursor.description]

    def fetch_game_reports(self):
        cursor = self.instance.cursor()
        cursor.execute("SELECT * FROM game_report")
        return cursor.fetchall(), [desc[0] for desc in cursor.description]

    def retrieve_text_for_wordcloud(self):
        cursor = self.instance.cursor()
        text = ''
        cursor.execute("SELECT content FROM article")
        text += ' '.join(row[0] for row in cursor.fetchall())
        return text

    def get_cursor(self):
        return self.instance.cursor()

    def get_num_articles(self, table_name):
        cursor = self.instance.cursor()
        cursor.execute("SELECT COUNT(*) FROM article WHERE origin=?", (table_name,))
        return (cursor.fetchone())[0]
    
    def clear_articles(self):
        cursor = self.instance.cursor()
        cursor.execute("SELECT id, title, content FROM article")
        rows = cursor.fetchall()
        for row in rows:
            article_id, title, content = row
            updated_content = content.replace("\u00A0", " ")
            cursor.execute("UPDATE article SET content = ? WHERE id = ?", (updated_content, article_id))

            if title.strip() == '' or len(content.strip()) < 20:
                cursor.execute("DELETE FROM article WHERE id = ?", (article_id, ))


        self.instance.commit()


    def clear_games(self):
        cursor = self.instance.cursor()
        cursor.execute("SELECT id, content FROM game_report")
        rows = cursor.fetchall()
        for row in rows:
            article_id, content = row
            if content.strip() == '':
                cursor.execute("DELETE FROM game_report WHERE id = ?", (article_id, ))


        self.instance.commit()

    def close(self):
        self.instance.close()
        print('Database closed.')


# Function to create the schema for the merged database using an external SQL file
def create_merged_schema(conn):
    with open("schema.sql", "r") as schema_file:
        schema_sql = schema_file.read()
    conn.executescript(schema_sql)


# Function to merge data from one database to another
def merge_databases(source_conn, target_conn, reset_db):
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    if reset_db:
        create_merged_schema(target_conn)

    source_cursor.execute("SELECT * FROM article")
    rows = source_cursor.fetchall()
    last_publish_date = None

    for row in rows:
        id, title, content, publish_date, origin = row

        if ':' in publish_date:
            publish_date = last_publish_date
        else:
            last_publish_date = publish_date

        try:
            target_cursor.execute(
                "INSERT INTO article (title, content, publish_date, origin) VALUES (?, ?, ?, ?)",
                (title, content, publish_date, origin)
            )
        except sqlite3.IntegrityError as e:
            print(f"Error inserting row with duplicate title: {title}")
    target_conn.commit()


def main():
    # Connect to the source and target databases
    source_conn = sqlite3.connect('db_fonseca.sqlite')
    target_conn = sqlite3.connect('merged_db.sqlite')

    # Merge the data from the source database to the target database
    merge_databases(source_conn, target_conn, True)

    # Close the database connections
    source_conn.close()
    target_conn.close()

    source_conn = sqlite3.connect('db_andre.sqlite')
    target_conn = sqlite3.connect('merged_db.sqlite')

    # Merge the data from the source database to the target database
    merge_databases(source_conn, target_conn, False)

    # Close the database connections
    source_conn.close()
    target_conn.close()


def merge_with_record():
    source_conn = sqlite3.connect('record.sqlite')
    target_conn = sqlite3.connect('merged_db.sqlite')

    merge_databases(source_conn, target_conn, False)

    source_conn.close()
    target_conn.close()

# if __name__ == '__main__':
#    merge_with_record()

# Remove faulty rows: DELETE FROM article WHERE id IN (4, 18, 19, 21, 22);
# DELETE FROM article WHERE TRIM(content) = '';
