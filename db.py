"""Database for storing and retrieving messages.

We store messages in the JSON format defined in message.to_json
"""

import json
import os
import psycopg2

from settings import *
from message import to_json

class MessageDb(object):
    """Abstract base class."""

    def add_message(self, message):
        """Add a message to the db."""
        pass

    def get_all_messages(self):
        """Return a list of all messages."""
        return []

    def clear_all_messages(self):
        """Delete all messages from the db."""
        pass

class DummyDb(MessageDb):
    def __init__(self):
        super(DummyDb, self).__init__()

    def get_all_messages(self):
            # create a couple of amusing root nodes
            m1 = {'user': 'admin', 
                  'message': 'What do you think is the significance of coffee?',
                  'id': 0, 'parentid': -1,
                  'posttime': '14 April 2014 18:21'}
            m2 = {'user': 'admin',
                  'message': 'How important are the bananas in Timbuktu?',
                  'id': 1, 'parentid': -1,
                  'posttime': '14 April 2014 19:21'}
            return [m1, m2]

class FileDb(MessageDb):
    filename = 'data.out'
    def __init__(self):
        super(FileDb, self).__init__()
    
    def get_all_messages(self):
        if not os.path.exists(self.filename):
            f = open(self.filename, 'w')
            f.close()
            return []
        f = open(self.filename, 'r')
        lines = f.readlines()
        f.close()
        messages = [eval(lin) for lin in lines]
        return messages

    def add_message(self, mdict):
        smsg = json.dumps(mdict, default=to_json)
        f = open(self.filename, 'a')
        f.write(smsg + '\n')
        f.close()

class PostgresDb(MessageDb):
    database = 'testdb'
    user = 'jm0037'
    def __init__(self):
        self.conn = psycopg2.connect(database=self.database, user=self.user) 
        self.cursor = self.conn.cursor()
        self.cursor.execute('SELECT version()')
        ver = self.cursor.fetchone()

    def add_message(self, mdict):
        query = 'INSERT INTO messages VALUES(%s, %s, %s, %s, %s)'
        self.cursor.execute(query, (mdict['id'], mdict['user'], 
                                    mdict['message'], mdict['parentid'],
                                    mdict['posttime']))
        self.conn.commit()
    
    def get_all_messages(self):
        try:
            self.cursor.execute('SELECT * FROM messages')
            self.conn.commit()
        except psycopg2.ProgrammingError:
            try:
                self.create_tables()
            except psycopg2.ProgrammingError:
                if DEBUG:
                    print 'could not read messages from DB'
                return []
        self.cursor.execute('SELECT * FROM messages')
        messages = self.cursor.fetchall()
        return [{'id': m[0], 'user': m[1], 'message': m[2], 'parentid': m[3],
                 'posttime': m[4]} for m in messages]

    def create_tables(self):
        # note 'user' is a reserved work is psql so we use 'uname' instead
        self.cursor.execute('CREATE TABLE messages (id INT PRIMARY KEY, '
                            'uname VARCHAR(50), message TEXT, '
                            'parentid INT, posttime VARCHAR(50) )')
        self.conn.commit()

if (DB_TYPE == DB_FILE):
    message_database = FileDb
elif (DB_TYPE == DB_POSTGRES):
    message_database = PostgresDb
else:
    message_database = DummyDb
