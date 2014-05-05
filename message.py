"""Handle passing of messages between the server and client.

Messages are passed between client and server as JSON formatted
strings, which can be easily converted to and from Python dictionary
objects.

To be valid these dicts must satisfy certain criteria (see
validate_message below).

"""

import json
import datetime
from copy import deepcopy

from settings import *
from models import Message, Topic

ID_ALL = -1 # message id for a message to sent to all clients

K_TYPE = 'mtype'
K_ID = 'userid'
K_AUTH = 'auth_token'
K_TSTAMP = 'tstamp'

REQUIRED_MESSAGE_KEYS = [K_TYPE, K_ID, K_AUTH]

# messsage types
M_TEST = 'test'
# message types from server to client
M_MYHANDLE = 'myhandle'
M_NEWHANDLE = 'newhandle'
M_REMOVEHANDLE = 'removehandle'
M_FULLTREE = 'fulltree'
M_NEWMESSAGE = 'newmessage'
# message types from client to server
M_SETTOPIC = 'settopic'
M_RESPONSE = 'response'
M_HEARTBEAT = 'heartbeat'
# message types both ways
M_CHANGEHANDLE = 'changehandle'

ALLOWED_MESSAGES = [M_TEST, M_MYHANDLE, M_NEWHANDLE, M_REMOVEHANDLE,
                    M_FULLTREE, M_NEWMESSAGE, M_SETTOPIC, M_RESPONSE, 
                    M_HEARTBEAT, M_CHANGEHANDLE]


def message_changehandle(back, msg):
    """Called when the client changes his/her handle."""
    
    userid = msg["userid"]
    newhandle = msg["handle"]
    back.users[userid].handle = newhandle

    for uid in back.topics[back.users[userid].topicid].users:
        if (uid != userid):
            back.send_message({K_TYPE: M_CHANGEHANDLE, 'changeid': userid, 'newhandle': newhandle}, uid)


def message_response(back, msg):
    """Called when we receive a reply from the client."""

    userid = msg["userid"]
    user = back.users[userid].handle

    mnode = Message(user=user, message=msg["text"], 
                    parentid=msg["replyid"], topicid=msg["topicid"])
    # add to the message tree
    back.topics[msg["topicid"]].add_message(mnode)
    # add to the db
    back.db.add_message(mnode)

    # notify all clients of the new message
    sendmsg = {K_TYPE: M_NEWMESSAGE, 'message': mnode}

#    print back.users.keys(), back.topics.keys(), back.users[userid].topicid
    for uid in back.topics[back.users[userid].topicid].users:
        back.send_message(sendmsg, uid)


def message_ignore(back, msg):
    """Just ignore the message."""

    pass


def message_settopic(back, msg):
    back.set_topic_for_user(msg["userid"], msg["topicid"])


# callbacks
CALLBACKS = {M_RESPONSE: message_response,
             M_CHANGEHANDLE: message_changehandle,
             M_HEARTBEAT: message_ignore,
             M_SETTOPIC: message_settopic}


class InvalidMessageError(Exception):
    pass


def validate_message(mdict):
    """Validate a message passed as a Python dictionary.

    Each message dict should have the following keys:

    mtype - the message type, which should be one of ALLOWED_MESSAGES

    id    - the id of the client from whom the message is from/to.  For
            sending a message to all clients, the special id ID_ALL should
            be used.
    """

    for at in REQUIRED_MESSAGE_KEYS:
        if at not in mdict:
            raise InvalidMessageError, 'required attribute {0} not in message'.format(at)

    if mdict[K_TYPE] not in ALLOWED_MESSAGES:
        raise InvalidMessageError, 'message type {0} not allowed'.format(mdict[K_TYPE])
