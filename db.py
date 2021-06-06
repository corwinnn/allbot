import psycopg2

from itertools import chain, repeat

from configs import DATABASE_PASSWORD, DATABASE_USER, DATABASE, DATABASE_HOST


class SQLighter:

    def __init__(self):
        self.connection = psycopg2.connect(
            host=DATABASE_HOST,
            dbname=DATABASE,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD)
        self.cursor = self.connection.cursor()

    def add_subscriber(self, uid, name):
        """
        Add bot user
        :param uid: telegram user id
        :param name: telegram user name
        """
        with self.connection:
            return self.cursor.execute(
                'INSERT INTO subscriber (uid, username) VALUES(%s, %s)',
                (uid, name)
            )

    def add_member(self, cid, username, alias):
        """
        Add chat member with an alias
        :param cid: telegram chat id
        :param username: telegram user name
        :param alias: alias of a group the user is a member of
        """
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
        """
        Check if user already in database
        :param uid: telegram user id
        :return: if user already in database
        """
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM subscriber WHERE uid = %s',
                (uid,)
            )
            result = self.cursor.fetchall()
            return len(result)

    def member_exists(self, cid, username, alias):
        """
        Check if user has such an alias in this chat
        :param cid: telegram chat id
        :param username: telegram user name
        :param alias: group alias
        :return:
        """
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM member WHERE cid = %s AND username = %s AND alias = %s',
                (cid, username, alias)
            )
            result = self.cursor.fetchall()
            return len(result)

    def create_alias(self, cid, alias, names):
        """
        Create new alias
        :param cid: telegram chat id
        :param alias: alias for a new group
        :param names: list of group members' user names
        """
        with self.connection:
            self.cursor.execute(
                'DELETE FROM member WHERE alias = %s',
                (alias,)
            )

            self.cursor.execute(
                'INSERT into member (cid, username, alias) VALUES' + ', '.join(
                    ['(%s, %s, %s)' for _ in range(len(names))]),
                tuple(chain(*zip(repeat(cid), names, repeat(alias))))
            )

    def get_alias_list(self, cid, alias):
        """
        Get list of group members under this alias
        :param cid: telegram chat id
        :param alias: alias for a group
        :return: list of group members' user names
        """
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM member WHERE cid = %s AND alias = %s',
                (cid, alias)
            )
            result = self.cursor.fetchall()
            return [res[2] for res in result]

    def member_group_list(self, cid):
        """
        Get list of all members' aliases in the chat
        :param cid: telegram chat id
        :return: list of all pairs (username, alias) for this chat
        """
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM member WHERE cid = %s',
                (cid,)
            )
            result = self.cursor.fetchall()
            return [(res[2], res[3]) for res in result]
