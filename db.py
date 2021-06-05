import os
import psycopg2

from itertools import chain, repeat

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

    def add_subscriber(self, uid, name):
        with self.connection:
            return self.cursor.execute(
                'INSERT INTO subscriber (uid, username) VALUES(%s, %s)',
                (uid, name)
            )

    def add_member(self, cid, username, alias):
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM member WHERE cid = %s AND username = %s AND alias = %s',
                (cid, username, alias)
            )
            result = self.cursor.fetchall()
            if not result:
                self.cursor.execute(
                    'INSERT INTO member (cid, username, alias) VALUES(%s, %s, %s)',
                    (cid, username, alias)
                )

    def subscriber_exists(self, uid):
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM subscriber WHERE uid = %s',
                (uid,)
            )
            result = self.cursor.fetchall()
            return len(result)

    def member_exists(self, cid, username, alias):
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM member WHERE cid = %s AND username = %s AND alias = %s',
                (cid, username, alias)
            )
            result = self.cursor.fetchall()
            return len(result)

    def create_alias(self, cid, alias, names):
        with self.connection:
            self.cursor.execute(
                'DELETE FROM member WHERE alias = %s',
                (alias,)
            )

            self.cursor.execute(
                'INSERT into member (cid, username, alias) VALUES' + ', '.join(['(%s, %s)' for _ in range(len(names))]),
                tuple(chain(*zip(repeat(cid), names, repeat(alias))))
            )

    def get_alias_list(self, cid, alias):
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM member WHERE cid = %s AND alias = %s',
                (cid, alias)
            )
            result = self.cursor.fetchall()
            return [res[2] for res in result]

