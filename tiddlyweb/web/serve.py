"""
Functions and Classes for running a TiddlyWeb server, including
optionally a built in web server.
"""
import logging
import selector

from tiddlyweb.util import std_error_message, initialize_logging


def load_app(app_prefix=None, dirname=None):
    """
    Create our application from a series of layers. The innermost
    layer is a selector application based on urls_map in config. This
    is surround by wrappers, which either set something in the
    environment, modify the request, or transform output.
    """
    from tiddlyweb.config import config
    if dirname:
        config['root_dir'] = dirname

    initialize_logging(config)

    mapfile = config['urls_map']
    if app_prefix != None:
        prefix = app_prefix
    else:
        prefix = config['server_prefix']
    app = selector.Selector(mapfile=mapfile, prefix=prefix)
    config['selector'] = app

    try:
        plugins = config['system_plugins']
        for plugin in plugins:
            logging.debug('attempt to import system plugin %s', plugin)
            # let the import fail with error if it does
            imported_module = __import__(plugin, {}, {}, ['init'])
            imported_module.init(config)
    except KeyError:
        pass  # no plugins

    wrappers = []
    wrappers.extend(reversed(config['server_request_filters']))
    wrappers.append(Environator)  # required as the first app
    wrappers.append(Configurator)  # required as the second app
    wrappers.extend(config['server_response_filters'])
    if wrappers:
        for wrapper in wrappers:
            logging.debug('wrapping app with %s', wrapper)
            if wrapper == Configurator:
                app = wrapper(app, config=config)
            else:
                app = wrapper(app)
    return app


def start_cherrypy(config):
    """
    Start a cherrypy webserver to run our app.
    """
    from cherrypy import wsgiserver
    hostname = config['server_host']['host']
    port = int(config['server_host']['port'])
    scheme = config['server_host']['scheme']
    app = load_app()
    server = wsgiserver.CherryPyWSGIServer((hostname, port), app)
    try:
        logging.debug('starting cherrypy at %s://%s:%s',
                scheme, hostname, port)
        std_error_message("Starting CherryPy at %s://%s:%s"
                % (scheme, hostname, port))
        server.start()
    except KeyboardInterrupt:
        server.stop()


class Environator(object):
    """
    WSGI Middleware that doctors the environment to make it satisfactory
    to Selector no matter what server has mounted us. This is likely to
    be riddled with bugs given that different servers behave differently
    with regard to SCRIPT_NAME, PATH_INFO and REQUEST_URI.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        request_method = environ.get('REQUEST_METHOD', None)
        request_uri = environ.get('REQUEST_URI', None)
        script_name = environ.get('SCRIPT_NAME', None)
        path_info = environ.get('PATH_INFO', None)
        query_string = environ.get('QUERY_STRING', None)
        logging.debug('starting "%s" request with uri "%s", script_name "%s"'
                ', path_info "%s" and query "%s"', request_method,
                request_uri, script_name, path_info, query_string)
        # do no cleaning for now
        return self.application(environ, start_response)


class Configurator(object):
    """
    WSGI Middleware to handle setting a config dict
    for every request.
    """

    def __init__(self, application, config):
        self.application = application
        self.config = config

    def __call__(self, environ, start_response):
        environ['tiddlyweb.config'] = self.config
        return self.application(environ, start_response)
