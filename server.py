"""Tornado WebSockets server for the q&a app."""

import time
import json
import os

import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.web

import message

# number of clients that have connected since starting the server.
_NCLIENTS = 0

# print messages received and sent
DEBUG = True

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(request):
        request.render('static/qanda.html')

class WebSocketHandler(tornado.websocket.WebSocketHandler):

    # the message tree stores all of the message information
    message_tree = message.MessageTree()

    # store WebSocketHandler instance for each client currently
    # connected. The key is the client id.
    listeners = {}

    def open(self):

        global _NCLIENTS

        if DEBUG:
            print 'OPEN'

        # use counter as client id
        clientid = _NCLIENTS
        self.listeners[clientid] = self
        handle = 'user{0}'.format(clientid)
        self.handle = handle

        # send handle (username) to client along with client id
        self.send_message_to_client({message.K_TYPE: message.M_MYHANDLE,
                                     'handle': handle, 'myid': clientid}, clientid)

        # send all other handles to client (could invent a new message
        # type to do this in a single message here)
        for lid, li in self.listeners.items():
            if lid != clientid:
                self.send_message_to_client({message.K_TYPE: message.M_NEWHANDLE,
                                             'handle': li.handle, 'id': lid}, 
                                            clientid)

        # send all messages in tree to client
        self.send_message_to_client({message.K_TYPE: message.M_FULLTREE,
                                     'tree': self.message_tree.get_all_messages()},
                                    clientid)

        # send new handle to all the other clients
        self.send_message_to_all_except({message.K_TYPE: message.M_NEWHANDLE,
                                         'handle': handle, 'id': clientid}, 
                                        clientid)
        _NCLIENTS += 1

    def on_close(self):

        if DEBUG:
            print 'CLOSE'

        # not ideal (probably)
        closeid = None
        for (k, v) in self.listeners.items():
            if (v == self):
                print "id closed is {}".format(k)
                closeid = k
                break

        if closeid is not None:
            self.send_message_to_all_except({message.K_TYPE: message.M_REMOVEHANDLE,
                                             'id': closeid},
                                            closeid)
            del self.listeners[closeid]
        else:
            print 'could not find id to close!'
        
    def on_message(self, mess):

        if DEBUG:
            print 'GOT MESSAGE: {}'.format(mess)

        msg = json.loads(mess)
        message.validate_message(msg)
        
        message.CALLBACKS[msg[message.K_TYPE]](self, msg)

    def send_message_to_client(self, messagedict, clientid):
        """Send all messages using this function."""

        # add timestamp and stringify the message
        messagedict[message.K_TSTAMP] = time.time()*1000
        jsonmsg = json.dumps(messagedict, default=message.to_json)

        if DEBUG:
            print 'SENDING MESSAGE: {}'.format(jsonmsg)

        self.listeners[clientid].write_message(jsonmsg)

    def send_message_to_all(self, message):
        for clientid in self.listeners:
            self.send_message_to_client(message, clientid)

    def send_message_to_all_except(self, message, clientex):
        for clientid in self.listeners:
            if (clientid != clientex):
                self.send_message_to_client(message, clientid)

if __name__ == "__main__":
    # path to all static data
    _dirname = os.path.dirname(__file__)
    static_path = os.path.join(_dirname, 'static')

    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
        (r'/ws', WebSocketHandler)
    ])

    http_server = tornado.httpserver.HTTPServer(app)
    port = int(os.environ.get("PORT", 5000))
    http_server.listen(port)
    main_loop = tornado.ioloop.IOLoop.instance()
    main_loop.start()
