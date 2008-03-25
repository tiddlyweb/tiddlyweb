
import os
import selector
from tiddlyweb.web.negotiate import Negotiate
from tiddlyweb.web.http import HTTPExceptor
from tiddlyweb.store import Store

def load_app(map, wrappers=[]):
    """
    Create our application from a series of layers. The innermost
    layer is a selector application based on url map in map. This
    is surround by wrappers, which either set something in the 
    environment or modify the request, or transform output.
    """
    app = selector.Selector(mapfile=map)
    if wrappers:
        for wrapper in wrappers:
            app = wrapper(app)
    return app

def start_simple(filename, port):
    """
    Start a wsgiref.simple_server to run our app.

    Provides the simplest base for testing, debugging
    and development.
    """
    os.environ = {}
    from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
    httpd = WSGIServer(('', port), WSGIRequestHandler)
    httpd.set_app(default_app(filename))
    print "Serving HTTP on %s port %s ..." % httpd.socket.getsockname()
    httpd.serve_forever()

def start_cherrypy(filename, port):
    """
    Start a cherrypy webserver to run our app.
    
    Here for sake of testing %2F handling as well as
    seeing what happens in a threaded environment.
    """
    os.environ = {}
    from cherrypy import wsgiserver
    server = wsgiserver.CherryPyWSGIServer(('127.0.0.1', port), default_app(filename))
    try:
        print "Starting CherryPy"
        server.start()
    except KeyboardInterrupt:
        server.stop()

def default_app(filename):
    """
    The pointer to our url map, plus the list of middleware 
    wrappers which we require.

    Eventually these should come from configuration. For now it
    is static, and consists of:

    StoreSet: set tiddlyweb.store in the environment to be a 
              tiddlyweb.store object.
    Negotiate: do content negotiation, setting tiddlyweb.type to
                the preferred Accept type, or to Content-Type (if
                this is not a GET).
    EncodeUTF8: encode internal unicode data as UTF-8 output .
    """
    return load_app(filename, [StoreSet, Negotiate, HTTPExceptor, EncodeUTF8])
    #return load_app(filename, [StoreSet, Negotiate])

class StoreSet(object):
    """
    WSGI Middleware that sets our choice of Store (tiddlyweb.store) in the environment.
    Eventually this can be used to configure the store per instance.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        db = Store('text')
        environ['tiddlyweb.store'] = db
        return self.application(environ, start_response)

class EncodeUTF8(object):
    """
    WSGI Middleware to ensure that the content we send out the pipe is encoded
    as UTF-8. Within the application content is _unicode_ (i.e. not encoded).
    """
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        return [x.encode('utf-8') for x in self.application(environ, start_response)]
