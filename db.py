"""Database for storing and retrieving messages.

We store messages in the JSON format defined in message.to_json
"""

import json
import os
import psycopg2
import urlparse

from settings import *
from message import to_json
# these are the only models that are persistent currently
from models import Topic, Message

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

    def add_message(self, msg):
        smsg = json.dumps(msg, default=to_json)
        f = open(self.filename, 'a')
        f.write(smsg + '\n')
        f.close()

class PostgresDb(MessageDb):
    def __init__(self):
        self.settings = self._get_connection_information()
        self.conn = psycopg2.connect(database=self.settings['database'],
                                     user=self.settings['user'],
                                     password=self.settings.get('password', None),
                                     host=self.settings.get('host', None),
                                     port=self.settings.get('port', None))
        self.cursor = self.conn.cursor()
        self.create_tables_if_not_exist()

    def _get_connection_information(self):
        """Set up settings dict."""
        dburl = os.environ.get("DATABASE_URL")
        if dburl is None:
            # local machine
            return {'database': 'testdb',
                    'user': 'jm0037'}
        else:
            # Heroku
            urlparse.uses_netloc.append("postgres")
            url = urlparse.urlparse(dburl)
            return {'database': url.path[1:],
                    'user': url.username,
                    'password': url.password,
                    'host': url.hostname,
                    'port': url.port}

    def add_message(self, msg):
        query = 'INSERT INTO messages VALUES(%s, %s, %s, %s, %s, %s)'
        self.cursor.execute(query, (msg.id, msg.user, 
                                    msg.message, msg.parentid,
                                    msg.posttime.strftime(DATE_FORMAT),
                                    msg.topicid))
        self.conn.commit()

    def add_topic(self, topic):
        query = 'INSERT INTO topics VALUES(%s, %s)'
        self.cursor.execute(query, (topic.topicid, topic.name))
        self.conn.commit()

    def get_all_topics(self):
        self.cursor.execute('SELECT * FROM topics')
        self.conn.commit()
        topics = self.cursor.fetchall()
        return [Topic(t[1], t[0]) for t in topics]
    
    def get_all_messages_for_topic(self, topicid):
        self.cursor.execute('SELECT * FROM messages WHERE topicid=%s', (topicid,))
        self.conn.commit()
        messages = self.cursor.fetchall()
        return [Message(user=m[1], message=m[2], parentid=m[3], 
                        posttime=m[4]) for m in messages]

    def create_tables_if_not_exist(self):
        try:
            self.cursor.execute('SELECT * FROM messages')
            self.conn.commit()
        except psycopg2.ProgrammingError:
            # this will clear the previous transaction
            self.conn.commit()
            self.create_tables()

    def create_tables(self):
        # note 'user' is a reserved work is psql so we use 'uname' instead
        self.cursor.execute('CREATE TABLE topics ('
                            'id       INT          NOT NULL PRIMARY KEY, '
                            'name     VARCHAR(100) NOT NULL' 
                            ')')
        self.cursor.execute('CREATE TABLE messages ('
                            'id       INT         NOT NULL PRIMARY KEY, '
                            'uname    VARCHAR(50) NOT NULL, '
                            'message  TEXT        NOT NULL, '
                            'parentid INT         NOT NULL, '
                            'posttime VARCHAR(50) NOT NULL, '
                            'topicid  INT references topics(id) '
                            ')')
        self.conn.commit()

if (DB_TYPE == DB_FILE):
    message_database = FileDb
elif (DB_TYPE == DB_POSTGRES):
    message_database = PostgresDb
else:
    message_database = DummyDb
