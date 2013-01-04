from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import tornado.wsgi
import tornado.web

from mediagoblin.app import MediaGoblinApp

if __name__ == '__main__':
    app = MediaGoblinApp('mediagoblin_local.ini')

    wsgi_app = tornado.wsgi.WSGIContainer(app)

    tornado_app = tornado.web.Application([
        ('/mgoblin_media/(.*)', tornado.web.StaticFileHandler,
         {'path': 'user_dev/media/public'}),
        ('/mgoblin_static/(.*)', tornado.web.StaticFileHandler,
         {'path': 'mediagoblin/static'}),
        ('/theme_static/(.*)', tornado.web.StaticFileHandler,
         {'path': 'user_dev/theme_static'}),
        ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app))])

    server = HTTPServer(tornado_app)
    server.listen(8181)

    IOLoop.instance().start()
