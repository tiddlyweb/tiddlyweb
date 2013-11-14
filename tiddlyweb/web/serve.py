"""
Functions and Classes for running a TiddlyWeb server, including
optionally a built in web server.
"""
import logging

from selector import Selector

from tiddlyweb.util import std_error_message, initialize_logging


LOGGER = logging.getLogger(__name__)


def load_app(app_prefix=None, dirname=None):
    """
    Create our application from a series of layers. The innermost
    layer is a Selector application based on ``urls_map`` defined in
    :py:mod:`config <tiddlyweb.config>`. This is surrounded by wrappers,
    which either set something in the environment, modify the request,
    or transform the response. The wrappers are WSGI middleware defined
    by ``server_request_filters`` and ``server_response_filters`` in
    :py:mod:`tiddlyweb.config`.
    """
    from tiddlyweb.config import config
    if dirname:
        config['root_dir'] = dirname

    # If the logger is not already initialized (from twanager),
    # let's initialize it.
    if LOGGER.parent.name is not 'tiddlyweb':
        initialize_logging(config, server=True)

    mapfile = config['urls_map']
    if app_prefix is not None:
        prefix = app_prefix
    else:
        prefix = config['server_prefix']
    app = Selector(mapfile=mapfile, prefix=prefix)
    config['selector'] = app

    try:
        plugins = config['system_plugins']
        for plugin in plugins:
            LOGGER.debug('attempt to import system plugin %s', plugin)
            # let the import fail with error if it does
            imported_module = __import__(plugin, {}, {}, ['init'])
            imported_module.init(config)
    except KeyError:
        pass  # no plugins

    wrappers = []
    wrappers.extend(reversed(config['server_request_filters']))
    wrappers.append(RequestStarter)  # required as the first app
    wrappers.append(Configurator)  # required as the second app
    wrappers.extend(config['server_response_filters'])
    if wrappers:
        for wrapper in wrappers:
            LOGGER.debug('wrapping app with %s', wrapper)
            if wrapper == Configurator:
                app = wrapper(app, config=config)
            else:
                app = wrapper(app)
    return app


def start_server(config):
    """
    Start a simple webserver, from ``wsgiref``, to run our app.
    """

    import sys
    from wsgiref.simple_server import make_server, WSGIRequestHandler

    class NoLogRequestHandler(WSGIRequestHandler):
        def log_request(self, code='-', size='-'):
            pass

    hostname = config['server_host']['host']
    port = int(config['server_host']['port'])
    scheme = config['server_host']['scheme']
    httpd = make_server(hostname, port, load_app(),
            handler_class=NoLogRequestHandler)

    LOGGER.debug('starting wsgi server at %s://%s:%s',
            scheme, hostname, port)
    std_error_message("starting wsgi server at %s://%s:%s"
            % (scheme, hostname, port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)


class RequestStarter(object):
    """
    WSGI middleware that logs basic request information and cleans
    ``PATH_INFO`` in the environment.

    ``PATH_INFO`` cleaning is done to ensure that there is a
    well known encoding of special characters and to support
    ``/`` in entity names (see :py:func:`clean_path_info`).
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        LOGGER.debug('starting %s request with URI "%s", script_name "%s"'
                ', path_info "%s" and query "%s"',
                environ.get('REQUEST_METHOD', None),
                environ.get('REQUEST_URI', None),
                environ.get('SCRIPT_NAME', None),
                environ.get('PATH_INFO', None),
                environ.get('QUERY_STRING', None))
        self.clean_path_info(environ)
        return self.application(environ, start_response)

    def clean_path_info(self, environ):
        """
        Clean ``PATH_INFO`` in the environment.

        This is necessary because WSGI servers tend to decode
        the URI before putting it in ``PATH_INFO``. This means that
        uri encoded data, such as the ``%2F`` encoding of ``/``
        will be decoded before we get to route dispatch handling,
        by which time the ``/`` is treated as a separator. People
        say that the right thing to do here is not use ``%2F``.
        This is hogwash. The right thing to do is not decode
        ``PATH_INFO``. In this solution if ``REQUEST_URI`` is present
        we use a portion of it to set ``PATH_INFO``.
        """
        request_uri = environ.get('REQUEST_URI', environ.get('RAW_URI', ''))

        if request_uri:
            request_uri = request_uri.decode()
            path_info = environ.get('PATH_INFO', '')
            script_name = environ.get('SCRIPT_NAME', '')
            query_string = environ.get('QUERY_STRING', '')

            path_info = request_uri.replace(script_name, "", 1)
            path_info = path_info.replace('?' + query_string, "", 1)
            environ['PATH_INFO'] = path_info


class Configurator(object):
    """
    WSGI middleware to set ``tiddlyweb.config`` in ``environ`` for
    every request from :py:mod:`config <tiddlyweb.config>`.
    """

    def __init__(self, application, config):
        self.application = application
        self.config = config

    def __call__(self, environ, start_response):
        environ['tiddlyweb.config'] = self.config
        return self.application(environ, start_response)
