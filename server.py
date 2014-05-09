"""Tornado WebSockets server for the q&a app."""

import os
import urlparse

import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.web

import backend
from settings import DEBUG

# the backend handles all application logic
_backend = backend.BackEnd()

class LobbyHandler(tornado.web.RequestHandler):
    def get(self):
        return self._render()

    def post(self):
        # get name of topic to add
        tname = self._get_topic_name()
        if tname:
            added = _backend.add_topic(tname)
        self._render(**{'error': not added, 'topicname': tname})

    def _render(self, **kwargs):
        kwargs['topics'] = _backend.get_topics()
        if 'error' not in kwargs:
            kwargs['error'] = False
        if 'topicname' not in kwargs:
            kwargs['topicname'] = 'meaning of life'
        self.render('index.html', **kwargs)

    def _get_topic_name(self):
        """Return topic name to add from raw data, or None if postdata invalid."""
        try:
            tname = urlparse.parse_qs(self.request.body)['topic'][0]
        except KeyError, IndexError:
            tname = None
        return tname

    def set_extra_headers(self, path):
        """Disable caching."""
        self.set_header('Cache-Control', 
                        'no-store, no-cache, must-revalidate, max-age=0')

class QaHandler(tornado.web.RequestHandler):
    def get(self, slug):
        t = _backend.get_topic_from_id(int(slug))

        self.render('qa.html', topic=t)

    def set_extra_headers(self, path):
        """Disable caching."""
        self.set_header('Cache-Control', 
                        'no-store, no-cache, must-revalidate, max-age=0')

class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        """Disable caching."""
        self.set_header('Cache-Control', 
                        'no-store, no-cache, must-revalidate, max-age=0')

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):

        if DEBUG:
            print 'OPEN'

        _backend.add_user(self)

    def on_close(self):

        if DEBUG:
            print 'CLOSE'

        _backend.remove_user(self)
        
    def on_message(self, mess):

        _backend.on_message(mess)

if __name__ == "__main__":
    # path to all static data
    _dirname = os.path.dirname(__file__)
    static_path = os.path.join(_dirname, 'static')

    app = tornado.web.Application([
        (r'/', LobbyHandler),
        (r'/\?\(.*\)', LobbyHandler),
        (r'/qa-(.*)', QaHandler),
        (r'/static/(.*)', MyStaticFileHandler, {'path': static_path}),
        (r'/ws/[\d+]', WebSocketHandler)
    ])

    http_server = tornado.httpserver.HTTPServer(app)
    # PORT is for Heroku deployment
    port = int(os.environ.get("PORT", 9500))
    http_server.listen(port)
    main_loop = tornado.ioloop.IOLoop.instance()
    main_loop.start()
