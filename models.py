"""Models used in the backend."""

import uuid

from message import MessageTree


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


class Topic(object):
    """Each topic has the following attributes:

    topicid - a unique id assigned by the application
    name    - the full name of the topic
    """

    NOID = -1   # retured as topic id if the topic doesnt exist
    ntopics = 0 # number of topics created so far (used as id)

    def __init__(self, name, id=None):
        if id is None:
            self.topicid = self.ntopics
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
