
import sys
import time
import urllib

from tiddlyweb.store import Store
from tiddlyweb.web.util import get_serialize_type

class HTMLPresenter(object):
    """
    Take the core app output, see if it is text/html,
    and if it is, add some framework.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        output = self.application(environ, start_response)
        if environ.has_key('tiddlyweb.title'):
            output = ''.join(output)
            return [self._header(environ), output, self._footer(environ)]
        return output

    def _header(self, environ):
        css = ''
        if environ['tiddlyweb.config'].has_key('css_uri'):
            css = '<link rel="stylesheet" href="%s" type="text/css" />' % environ['tiddlyweb.config']['css_uri']
        try:
            links = '\n'.join(environ['tiddlyweb.links'])
        except KeyError:
            links = ''
        return """
<html>
<head>
<title>TiddlyWeb - %s</title>
%s
%s
</head>
<body>
<div id="header"></div>
""" % (environ['tiddlyweb.title'], css, links)

    def _footer(self, environ):
        return """
<div id="footer">
<div id="badge">This is <a href="http://www.tiddlywiki.org/wiki/TiddlyWeb">TiddlyWeb</a></div>
<div id="usergreet">User %s.</div>
</div>
</body>
</html>
""" % environ['tiddlyweb.usersign']['name']

class SimpleLog(object):
    """
    WSGI Middleware to write a very simple log to stdout.

    Borrowed from Paste Translogger
    """

    format = ('%(REMOTE_ADDR)s - %(REMOTE_USER)s [%(time)s] '
            '"%(REQUEST_METHOD)s %(REQUEST_URI)s %(HTTP_VERSION)s" '
            '%(status)s %(bytes)s "%(HTTP_REFERER)s" "%(HTTP_USER_AGENT)s"')

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        req_uri = urllib.quote(environ.get('SCRIPT_NAME', '')
                + environ.get('PATH_INFO', ''))
        if environ.get('QUERY_STRING'):
            req_uri += '?'+environ['QUERY_STRING']
        def replacement_start_response(status, headers, exc_info=None):
            bytes = None
            for name, value in headers:
                if name.lower() == 'content-length':
                    bytes = value
            self.write_log(environ, req_uri, status, bytes)
            return start_response(status, headers, exc_info)
        return self.application(environ, replacement_start_response)

    def write_log(self, environ, req_uri, status, bytes):
        environ['REMOTE_USER'] = None
        try:
            environ['REMOTE_USER'] = environ['tiddlyweb.usersign']['name']
        except KeyError:
            pass
        if bytes is None:
            bytes = '-'
        d = {
                'REMOTE_ADDR': environ.get('REMOTE_ADDR') or '-',
                'REMOTE_USER': environ.get('REMOTE_USER') or '-',
                'REQUEST_METHOD': environ['REQUEST_METHOD'],
                'REQUEST_URI': req_uri,
                'HTTP_VERSION': environ.get('SERVER_PROTOCOL'),
                'time': time.strftime('%d/%b/%Y:%H:%M:%S ', time.localtime()),
                'status': status.split(None, 1)[0],
                'bytes': bytes,
                'HTTP_REFERER': environ.get('HTTP_REFERER', '-'),
                'HTTP_USER_AGENT': environ.get('HTTP_USER_AGENT', '-'),
                }
        message = self.format % d
        print message
        sys.stdout.flush()

class StoreSet(object):
    """
    WSGI Middleware that sets our choice of Store (tiddlyweb.store) in the environment.
    Eventually this can be used to configure the store per instance.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        db = Store(environ['tiddlyweb.config']['server_store'][0], environ)
        environ['tiddlyweb.store'] = db
        return self.application(environ, start_response)

class EncodeUTF8(object):
    """
    WSGI Middleware to ensure that the content we send out the pipe is encoded
    as UTF-8. Within the application content is _unicode_ (i.e. not encoded).
    """
    def __init__(self, application):
        self.application = application

    def _encoder(self, string):
        # if we are currently unicode, encode to utf-8
        if type(string) == unicode:
            string = string.encode('utf-8')
        return string

    def _yielder(self, environ, start_response):
        for output in self.application(environ, start_response):
            yield self._encoder(output)

    def __call__(self, environ, start_response):
        return self._yielder(environ, start_response)
