"""The backend."""

import time
import json
import uuid
from tornado.websocket import WebSocketClosedError

from settings import *
import message
import db

class User(object):
    """Each user has the following attributes:

    userid     - a unique id assigned by the application
    handle     - username
    auth_token - an unique authentication token that the client needs
                 to send with every message
    """

    nusers = 0 # number of users created so far (used as id)

    def __init__(self):
        self.userid = self.nusers
        self.handle = 'user{0}'.format(self.userid)
        self.auth_token = str(uuid.uuid4())
        User.nusers += 1
        
class BackEnd(object):
    def __init__(self):
        self.users = {}
        self.db = db.message_database()
        self.message_tree = message.MessageTree(self.db.get_all_messages())
        
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

        # send all other handles to user
        for (userid, user) in self.users.items():
            if userid != u.userid:
                self.send_message({message.K_TYPE: message.M_NEWHANDLE,
                                   'handle': user.handle, 
                                   'userid': userid}, u.userid)

        # send all messages in tree to client
        self.send_message({message.K_TYPE: message.M_FULLTREE,
                           'tree': self.message_tree.get_all_messages()},
                          u.userid)

        # send new handle to all the other clients
        self.send_message_to_all_except({message.K_TYPE: message.M_NEWHANDLE,
                                         'handle': u.handle, 
                                         'userid': u.userid}, u.userid)

    def remove_user(self, handler):
        # not ideal (probably)
        closeid = None
        for (uid, u) in self.users.items():
            if (u._handler == handler):
                print "id closed is {}".format(uid)
                closeid = uid
                break

        if closeid is not None:
            self.send_message_to_all_except({message.K_TYPE: message.M_REMOVEHANDLE,
                                             'userid': closeid},
                                            closeid)
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

    def send_message_to_all_except(self, messagedict, userid):
        for uid in self.users:
            if (uid != userid):
                self.send_message(messagedict, uid)

    def send_message_to_all(self, messagedict):
        for uid in self.users:
            self.send_message(messagedict, uid)

    def send_message(self, messagedict, userid):
        # add timestamp and stringify the message
        messagedict[message.K_TSTAMP] = time.time()*1000
        jsonmsg = json.dumps(messagedict, default=message.to_json)
        if DEBUG:
            print 'SENDING MESSAGE: {}'.format(jsonmsg)
        
        try:
            self.users[userid]._handler.write_message(jsonmsg)
        except WebSocketClosedError:
            pass
