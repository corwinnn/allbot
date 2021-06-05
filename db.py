import os
import psycopg2

DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE = os.environ.get('DATABASE')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')


class SQLighter:

    def __init__(self):
        self.connection = psycopg2.connect(
            host=DATABASE_HOST,
            dbname=DATABASE,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD)
        self.cursor = self.connection.cursor()

    def add_user(self, uid, name):
        with self.connection:
            return self.cursor.execute(
                f'INSERT INTO subscriber (uid, username) VALUES({uid}, {name})')

    def subscriber_exists(self, uid):
        with self.connection:
            self.cursor.execute(
                f'SELECT * FROM subscriber WHERE uid = {uid}')
            result = self.cursor.fetchall()
            return len(result)
