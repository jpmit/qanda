"""Handle passing of messages between the server and client.

Messages are passed between client and server as JSON formatted
strings, which can be easily converted to and from Python dictionary
objects.

To be valid these dicts must satisfy certain criteria (see
validate_message below).

"""

import json
from copy import deepcopy

ID_ALL = -1 # message id for a message to sent to all clients

K_TYPE = 'mtype'
K_ID = 'id'
K_TSTAMP = 'tstamp'

REQUIRED_MESSAGE_KEYS = [K_TYPE, K_ID]

# messsage types
M_TEST = 'test'
# message types from server to client
M_MYHANDLE = 'myhandle'
M_NEWHANDLE = 'newhandle'
M_REMOVEHANDLE = 'removehandle'
M_FULLTREE = 'fulltree'
M_NEWMESSAGE = 'newmessage'
# message types from client to server
M_RESPONSE = 'response'

ALLOWED_MESSAGES = [M_TEST, M_MYHANDLE, M_NEWHANDLE, M_REMOVEHANDLE,
                    M_FULLTREE, M_NEWMESSAGE, M_RESPONSE]

def message_response(wshandler, msg):
    """Called when we receive a message from the client."""

    user = wshandler.listeners[msg["id"]].handle
    newmsg = wshandler.message_tree.add_message(msg["replyid"], user, msg["text"])

    # notify all clients of the new message
    sendmsg = {K_TYPE: M_NEWMESSAGE, 'message': newmsg} 
    wshandler.send_message_to_all(sendmsg)

# callbacks
CALLBACKS = {M_RESPONSE: message_response}

def to_json(pyo):
    if isinstance(pyo, MessageNode):
        return {'user': pyo.user,
                'message': pyo.message,
                'id': pyo.id,
                'parentid': pyo.parentid}

    raise TypeError(repr(pyo) + ' is not JSON serializable') 

# each message gets an ID (starts at zero)
_MESSAGE_ID = 0
# a message with parentid of _PARENTID_ROOT is a root message
_PARENTID_ROOT = -1

class MessageNode(object):
    def __init__(self, user, message, parentid):
        global _MESSAGE_ID
        self.user = user
        self.message = message
        self.id = _MESSAGE_ID
        self.parentid = parentid
        _MESSAGE_ID += 1

class MessageTree(object):
    """Class to store all messages in the Q&A session."""

    def __init__(self):
        
        # store ids of the root nodes (in the correct display order)
        self._rootnodes = []
        # key is the node id, value is a list of children node ids (in
        # the correct display order)
        self._children = {}
        # keys are the node ids, values are the actual MessageNode objects
        self._messages = {}

        # create a couple of amusing root nodes
        self.add_message(_PARENTID_ROOT, 'admin', 
                         'What do you think is the significance of coffee?')
        self.add_message(_PARENTID_ROOT, 'admin', 
                         'How important are the bananas in Timbuktu?')

    def add_message(self, parentid, user, message):
        mnode = MessageNode(user, message, parentid)
        mnodeid = mnode.id
        if parentid == _PARENTID_ROOT:
            self._rootnodes.append(mnodeid)
        else:
            self._children[parentid].append(mnodeid)
        self._children[mnodeid] = []
        self._messages[mnodeid] = mnode

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
