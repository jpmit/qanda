"""Data structures used in the backend."""

import uuid
import datetime

from settings import *

# users are not persistent at the moment, i.e. they are not stored in
# the database
class User(object):
    """Each user has the following attributes:

    userid     - a unique id assigned by the application
    handle     - username
    auth_token - an unique authentication token that the client needs
                 to send with every message
    """

    NO_TOPIC = -1
    nusers = 0 # number of users created so far (used as id)

    def __init__(self):
        self.userid = self.nusers
        self.handle = 'user{0}'.format(self.userid)
        self.auth_token = str(uuid.uuid4())
        # the current topic id of the user
        self.topicid = User.NO_TOPIC
        User.nusers += 1


class Topic(object):
    """Each topic has the following attributes:

    topicid - a unique id assigned by the application
    name    - the full name of the topic
    """

    # retured as topic id if the topic doesnt exist
    NOID = -1
    # number of topics created so far (used as id)
    ntopics = 0 

    def __init__(self, name, id=None):
        if id is None:
            self.topicid = Topic.ntopics
        else:
            self.topicid = id
        self.name = name
        self.urlname = name.replace(' ','-')
        self.nusers = 0
        Topic.ntopics += 1
        
        # tree of all messages for this topic
        self.message_tree = MessageTree([])

        # mapping of userids to user objects for this topic
        self.users = {}

    def add_user(self, userid):
        # we only store the ids here
        self.users[userid] = None
        self.nusers += 1

    def add_message(self, mnode):
        self.message_tree.add_message(mnode)

    def remove_user(self, userid):
        del self.users[userid]
        self.nusers -= 1

    def get_all_messages(self):
        return self.message_tree.get_all_messages()

class Message(object):

    # number of messages created so far (used as id)
    nmessages = 0

    def __init__(self, user, message, parentid, posttime=None, topicid=None, id=None):
        self.user = user
        self.message = message
        self.id = Message.nmessages if id is None else id
        self.topicid = Topic.NOID if topicid is None else topicid
        self.parentid = parentid
        if posttime is None:
            self.posttime = datetime.datetime.now()
        elif isinstance(posttime, str):
            # convert to datetime object
            self.posttime = datetime.datetime.strptime(posttime, DATE_FORMAT)
        else:
            self.posttime = posttime
        Message.nmessages += 1
        

class MessageTree(object):
    """Class to store all messages for a particular topic."""

    # a message with parentid of _PARENTID_ROOT is a root message
    _PARENTID_ROOT = -1

    def __init__(self, messages=[]):
        
        # store ids of the root nodes (in the correct display order)
        self._rootnodes = []
        # key is the node id, value is a list of children node ids (in
        # the correct display order)
        self._children = {}
        # keys are the node ids, values are the actual MessageNode objects
        self._messages = {}

        for msg in messages:
            self.add_message(msg)

    def add_message(self, mnode):
        mnodeid = mnode.id
        parentid = mnode.parentid
        if parentid == self._PARENTID_ROOT:
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
