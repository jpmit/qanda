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
                    M_FULLTREE, M_NEWMESSAGE, M_SETTOPIC, M_RESPONSE, M_HEARTBEAT, M_CHANGEHANDLE]


def message_changehandle(back, msg):
    """Called when the client changes his/her handle."""
    
    userid = msg["userid"]
    newhandle = msg["handle"]
    back.users[userid].handle = newhandle

    for uid in back.topics[back.users[userid]._topicid].users:
        if (uid != userid):
            back.send_message({K_TYPE: M_CHANGEHANDLE, 'changeid': userid, 'newhandle': newhandle}, uid)


def message_response(back, msg):
    """Called when we receive a reply from the client."""

    userid = msg["userid"]
    user = back.users[userid].handle

    mnode = MessageNode(user, msg["text"], msg["replyid"])
    # add to the message tree
    back.topics[msg["topicid"]].add_message(mnode)
    # add to the db
    back.db.add_message(to_json(mnode), msg["topicid"])

    # notify all clients of the new message
    sendmsg = {K_TYPE: M_NEWMESSAGE, 'message': mnode}

    for uid in back.topics[back.users[userid]._topicid].users:
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
_POSTTIME_FORMAT = '%d %B %Y %H:%M'

def to_json(pyo):
    """Define JSON serialization for MessageNode object."""
    if isinstance(pyo, MessageNode):
        return {'user': pyo.user,
                'message': pyo.message,
                'id': pyo.id,
                'parentid': pyo.parentid,
                'posttime': pyo.posttime.strftime(_POSTTIME_FORMAT)}

    raise TypeError(repr(pyo) + ' is not JSON serializable') 

def mnode_from_json(msg):
    return MessageNode(msg['user'], msg['message'], msg['parentid'],
                       datetime.datetime.strptime(msg['posttime'],
                                                  _POSTTIME_FORMAT))

# a message with parentid of _PARENTID_ROOT is a root message
_PARENTID_ROOT = -1


class MessageNode(object):
    def __init__(self, user, message, parentid, posttime=None):
        self.user = user
        self.message = message
        self.id = MessageTree.num_messages
        self.parentid = parentid
        if posttime is None:
            posttime = datetime.datetime.now()
        self.posttime = posttime

class MessageTree(object):
    """Class to store all messages in the Q&A session."""

    # number of messages in tree
    num_messages = 0

    def __init__(self, messages=[]):
        
        # store ids of the root nodes (in the correct display order)
        self._rootnodes = []
        # key is the node id, value is a list of children node ids (in
        # the correct display order)
        self._children = {}
        # keys are the node ids, values are the actual MessageNode objects
        self._messages = {}

        for msg in messages:
            self.add_message(mnode_from_json(msg))

    def add_message(self, mnode):
        mnodeid = mnode.id
        parentid = mnode.parentid
        if parentid == _PARENTID_ROOT:
            self._rootnodes.append(mnodeid)
        else:
            self._children[parentid].append(mnodeid)
        self._children[mnodeid] = []
        self._messages[mnodeid] = mnode
        MessageTree.num_messages += 1

        return mnode

    def get_all_messages(self):
        return {'rootnodes': self._rootnodes, 
                'children': self._children, 
                'messages': self._messages}


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
