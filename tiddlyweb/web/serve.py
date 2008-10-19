"""
Functions and Classes for running the TiddlyWeb
web server.
"""
import os
import selector

from tiddlyweb.config import config


def load_app(host, port, map_filename):
    """
    Create our application from a series of layers. The innermost
    layer is a selector application based on url map in map. This
    is surround by wrappers, which either set something in the
    environment or modify the request, or transform output.
    """

    app = selector.Selector(mapfile=map_filename)
    config['selector'] = app

    try:
        plugins = config['system_plugins']
        for plugin in plugins:
            # let the import fail with error if it does
            imported_module = __import__(plugin, {}, {}, ['init'])
            imported_module.init(config)
    except KeyError:
        pass # no plugins

    config['server_host'] = dict(scheme='http', host=host, port=port)
    wrappers = []
    wrappers.extend(reversed(config['server_request_filters']))
    wrappers.append(Configurator) # required as the first app
    wrappers.extend(config['server_response_filters'])
    if wrappers:
        for wrapper in wrappers:
            app = wrapper(app)
    return app


def start_simple(filename, hostname, port):
    """
    Start a wsgiref.simple_server to run our app.

    Provides the simplest base for testing, debugging
    and development.
    """
    os.environ = {}
    from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
    httpd = WSGIServer((hostname, port), WSGIRequestHandler)
    httpd.set_app(load_app(hostname, port, filename))
    print "Serving HTTP on %s port %s ..." % httpd.socket.getsockname()
    httpd.serve_forever()


def start_cherrypy(filename, hostname, port):
    """
    Start a cherrypy webserver to run our app.

    Here for sake of testing %2F handling as well as
    seeing what happens in a threaded environment.
    """
    os.environ = {}
    from cherrypy import wsgiserver
    server = wsgiserver.CherryPyWSGIServer((hostname, port),
            load_app(hostname, port, filename))
    try:
        print "Starting CherryPy"
        server.start()
    except KeyboardInterrupt:
        server.stop()


class Configurator(object):
    """
    WSGI Middleware to handle setting a config dict
    for every request.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        environ['tiddlyweb.config'] = config
        return self.application(environ, start_response)
