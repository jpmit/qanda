"""Database for storing and retrieving messages.

We store messages in the JSON format defined in message.to_json
"""

import json
import os
import psycopg2
import urlparse

from settings import *
# Topic and Message are the only models that are persistent currently
from models import Topic, Message, to_json

class MessageDb(object):
    """Abstract base class."""

    def add_message(self, message):
        """Add a message to the db."""
        pass

    def get_all_messages(self):
        """Return a list of all messages."""
        return []

    def add_topic(self, topic):
        """Add a topic to the db."""
        pass

    def get_all_topics(self):
        """Return a list of all topics."""
        return []

    def get_all_messages_for_topic(self, topicid):
        """Return a list of all messages for the particular topicid."""
        return []


class DummyDb(MessageDb):
    # if True, use dummy data, otherwise no data
    USE_DUMMY_DATA = True

    dummy_data = {'messages': [Message(user='admin',
                                       message='How do you do it?',
                                       topicid=1,
                                       parentid=-1,
                                       posttime='14 April 2014 18:21'),
                               Message(user='admin',
                                       message='How can I do it?',
                                       topicid=1,
                                       parentid=-1,
                                       posttime='14 April 2014 19:21')],
                  'topics': [Topic('How to maximise awesomeness', id=1)]}

    def __init__(self):
        super(DummyDb, self).__init__()

    def get_all_messages(self):
        if self.USE_DUMMY_DATA:
            return self.dummy_data['messages']
        else:
            return []
    
    def get_all_topics(self):
        if self.USE_DUMMY_DATA:
            return self.dummy_data['topics']
        else:
            return []

    def get_all_messages_for_topic(self, topicid):
        msgs = []
        if self.USE_DUMMY_DATA:
            for msg in self.dummy_data['messages']:
                if (msg.topicid == topicid):
                    msgs.append(msg)
        return msgs


class FileDb(MessageDb):
    mfilename   = 'message.db'
    tfilename   = 'topic.db'
    
    def __init__(self):
        super(FileDb, self).__init__()

        # create the files if they don't already exist (or want to drop them)
        for fn in [self.mfilename, self.tfilename]:
            if DB_DROP or not os.path.exists(fn):
                f = open(fn, 'w')
                f.close()

    def add_message(self, msg):
        smsg = json.dumps(msg, default=to_json)
        f = open(self.mfilename, 'a')
        f.write(smsg + '\n')
        f.close()

    def get_all_messages(self):
        f = open(self.mfilename, 'r')
        lines = f.readlines()
        f.close()
        mdicts = [eval(lin) for lin in lines]
        messages = [Message(m["user"], m["message"], m["parentid"],
                            m["posttime"], m["topicid"], m["id"]) 
                    for m in mdicts]
        return messages

    def add_topic(self, topic):
        stopic = json.dumps(topic, default=to_json)
        f = open(self.tfilename, 'a')
        f.write(stopic + '\n')
        f.close()

    def get_all_topics(self):
        f = open(self.tfilename, 'r')
        lines = f.readlines()
        f.close()
        tdicts = [eval(lin) for lin in lines]
        topics = [Topic(t["name"], t["id"]) for t in tdicts]
        return topics

    def get_all_messages_for_topic(self, topicid):
        msgs = []
        for m in self.get_all_messages():
            if (m.id == topicid):
                msgs.append(m)
        return msgs


class PostgresDb(MessageDb):
    def __init__(self):
        self.settings = self._get_connection_information()
        self.conn = psycopg2.connect(database=self.settings['database'],
                                     user=self.settings['user'],
                                     password=self.settings.get('password', None),
                                     host=self.settings.get('host', None),
                                     port=self.settings.get('port', None))
        self.cursor = self.conn.cursor()
        # drop all tables according to settings.py
        if DB_DROP:
            self._drop_all_tables()
        self._create_tables_if_not_exist()

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
        self.cursor.execute(query, (topic.id, topic.name))
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
    
    def _drop_all_tables(self):
        try:
            self.cursor.execute('DROP table messages')
            self.cursor.execute('DROP table topics')
            self.conn.commit()
        except psycopg2.ProgrammingError:
            self.conn.commit()

    def _create_tables_if_not_exist(self):
        try:
            self.cursor.execute('SELECT * FROM messages')
            self.conn.commit()
        except psycopg2.ProgrammingError:
            # this will clear the previous transaction
            self.conn.commit()
            self._create_tables()

    def _create_tables(self):
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
