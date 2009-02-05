"""
Functions and Classes for running the TiddlyWeb
web server.
"""
import logging
import os
import selector

from tiddlyweb.config import config


def load_app():
    """
    Create our application from a series of layers. The innermost
    layer is a selector application based on url map in map. This
    is surround by wrappers, which either set something in the
    environment or modify the request, or transform output.
    """

    mapfile = config['urls_map']
    app = selector.Selector(mapfile=mapfile)
    config['selector'] = app

    try:
        plugins = config['system_plugins']
        for plugin in plugins:
            logging.debug('attempt to import system plugin %s' % plugin)
            # let the import fail with error if it does
            imported_module = __import__(plugin, {}, {}, ['init'])
            imported_module.init(config)
    except KeyError:
        pass # no plugins

    wrappers = []
    wrappers.extend(reversed(config['server_request_filters']))
    wrappers.append(Configurator) # required as the first app
    wrappers.extend(config['server_response_filters'])
    if wrappers:
        for wrapper in wrappers:
            logging.debug('wrapping app with %s' % wrapper)
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
    hostname = config['server_host']['host']
    port = int(config['server_host']['port'])
    httpd = WSGIServer((hostname, port), WSGIRequestHandler)
    httpd.set_app(load_app())
    print "Serving HTTP on %s port %s ..." % httpd.socket.getsockname()
    httpd.serve_forever()


def start_cherrypy():
    """
    Start a cherrypy webserver to run our app.

    Here for sake of testing %2F handling as well as
    seeing what happens in a threaded environment.
    """
    os.environ = {}
    from cherrypy import wsgiserver
    hostname = config['server_host']['host']
    port = int(config['server_host']['port'])
    server = wsgiserver.CherryPyWSGIServer((hostname, port),
            load_app())
    try:
        logging.debug('starting cherrypy at %s:%s' % (hostname, port))
        print "Starting CherryPy at %s:%s" % (hostname, port)
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
        logging.debug('starting "%s" request with path "%s" and query "%s"' % (
            environ.get('REQUEST_METHOD',''),
            environ.get('PATH_INFO', ''),
            environ.get('QUERY_STRING', '')))
        environ['tiddlyweb.config'] = config
        # XXX do this somewhere else
        # clean up the environment to protect against
        # different web servers on which we are mounted
        if environ.get('SCRIPT_NAME', '') != config['server_prefix']:
            if not environ.get('QUERY_STRING', ''):
                logging.debug('setting path info to %s' % environ['REQUEST_URI'])
                environ['PATH_INFO'] = environ['REQUEST_URI']
                environ['SCRIPT_NAME'] = ''
            else:
                environ['PATH_INFO'] = environ.get('SCRIPT_NAME', '') + environ.get('PATH_INFO', '')
                environ['SCRIPT_NAME'] = ''
        return self.application(environ, start_response)
