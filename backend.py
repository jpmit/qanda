"""The backend."""

import time
import json
from tornado.websocket import WebSocketClosedError

from settings import *
import message
import db
from models import Topic, User, MessageTree, to_json

        
class BackEnd(object):
    def __init__(self):

        self.db = db.message_database()
        # userids as keys, user objects as values
        self.users = {}
        # topicids as keys, topic objects as values
        self.topics = {}
        # load all existing topics and their messages
        topics = self.db.get_all_topics()
        for t in topics:
            t.message_tree = MessageTree(self.db.get_all_messages_for_topic(t.id))
            self.topics[t.id] = t

    def add_topic(self, name):
        """Return True if successfully added topic."""

        for t in self.topics.values():
            if (t.name == name):
                return False
        newt = Topic(name)
        self.topics[newt.id] = newt
        # add to db
        self.db.add_topic(newt)
        return True

    def set_topic_for_user(self, userid, topicid):
        try:
            u = self.users[userid]
        except:
            # user must have disconnected
            pass
        else:
            u.topicid = topicid
            t = self.topics[topicid]
            t.add_user(userid)
            # send all other handles to user
            for uid in self.topics[topicid].users:
                if uid != userid:
                    user = self.users[uid]
                    self.send_message({message.K_TYPE: message.M_NEWHANDLE,
                                       'handle': user.handle, 
                                       'userid': uid}, userid)

            # send all messages in topic message tree to client
            self.send_message({message.K_TYPE: message.M_FULLTREE,
                               'tree': t.get_all_messages()},
                              userid)

            # send new handle to all the other clients on this topic
            for uid in self.topics[topicid].users:
                if uid != userid:
                    self.send_message({message.K_TYPE: message.M_NEWHANDLE,
                                       'handle': u.handle, 
                                       'userid': userid}, uid)

    def get_topics(self):
        return self.topics.values()

    def get_topicid_from_url(self, url):
        for t in self.topics.values():
            if (t.urlname == url):
                return t.id
        return Topic.NOID
        
    def add_user(self, handler):
        """handler is an instance of tornado.websocket.WebSocketHandler.

        We can send a message to the user by calling handler.write_message
        """

        u = User()
        u._handler = handler
        self.users[u.userid] = u

        # send handle to user along with user id
        self.send_message({message.K_TYPE: message.M_MYHANDLE,
                           'handle': u.handle, 'userid': u.userid,
                           'auth_token': u.auth_token}, u.userid)

    def remove_user(self, handler):
        # not ideal (probably)
        closeid = None
        for (uid, u) in self.users.items():
            if (u._handler == handler):
                print "id closed is {}".format(uid)
                closeid = uid
                break

        if closeid is not None:
            u = self.users[closeid]
            for uid in self.topics[u.topicid].users:
                if uid != closeid:
                    self.send_message({message.K_TYPE: message.M_REMOVEHANDLE,
                                       'userid': closeid},
                                      uid)
            self.topics[u.topicid].remove_user(closeid)
            del self.users[closeid]
        else:
            if DEBUG:
                print 'could not find id to close!'

    def on_message(self, mess):

        if DEBUG:
            print 'GOT MESSAGE: {}'.format(mess)

        msg = json.loads(mess)

        # check the message has all the required keys
        message.validate_message(msg)
        
        # check that the auth_token is correct for the client
        uid = msg[message.K_ID]
        if (msg[message.K_AUTH] != self.users[uid].auth_token):
            if DEBUG:
                print 'received incorrect auth_token for client {0}'\
                    .format(uid)
            return
        
        # message ok, execute callback
        message.CALLBACKS[msg[message.K_TYPE]](self, msg)

    def send_message(self, messagedict, userid):
        # add timestamp and stringify the message
        messagedict[message.K_TSTAMP] = time.time()*1000
        jsonmsg = json.dumps(messagedict, default=to_json)
        if DEBUG:
            print 'SENDING MESSAGE: {}'.format(jsonmsg)
        
        try:
            self.users[userid]._handler.write_message(jsonmsg)
        except WebSocketClosedError:
            pass
