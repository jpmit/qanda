"""Tornado WebSockets server for the q&a app."""

import os

import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.web

import backend
import settings

# print messages received and sent
_DEBUG = settings.DEBUG

# the backend handles all application logic
_backend = backend.BackEnd()

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(request):
        request.render('index.html')

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

        if _DEBUG:
            print 'OPEN'

        _backend.add_user(self)

    def on_close(self):

        if _DEBUG:
            print 'CLOSE'

        _backend.remove_user(self)
        
    def on_message(self, mess):

        _backend.on_message(mess)

if __name__ == "__main__":
    # path to all static data
    _dirname = os.path.dirname(__file__)
    static_path = os.path.join(_dirname, 'static')

    app = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/static/(.*)', MyStaticFileHandler, {'path': static_path}),
        (r'/ws', WebSocketHandler)
    ])

    http_server = tornado.httpserver.HTTPServer(app)
    # using environment variable means we will work on Heroku
    port = int(os.environ.get("PORT", 9500))
    http_server.listen(port)
    main_loop = tornado.ioloop.IOLoop.instance()
    main_loop.start()
