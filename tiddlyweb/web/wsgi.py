
import sys
import time
import urllib

from tiddlyweb.policy import UserRequiredError, ForbiddenError
from tiddlyweb.store import Store
from tiddlyweb.web.http import HTTP403, HTTP302
from tiddlyweb.web.util import server_base_url


class HTMLPresenter(object):
    """
    Take the core app output, see if it is text/html,
    and if it is, add some framework.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        output = self.application(environ, start_response)
        if 'tiddlyweb.title' in environ and 'Mozilla' in environ['HTTP_USER_AGENT']:
            output = ''.join(output)
            return [self._header(environ), output, self._footer(environ)]
        return output

    def _header(self, environ):
        css = ''
        if 'css_uri' in environ['tiddlyweb.config']:
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
<div id="header">%s</div>
""" % (environ['tiddlyweb.title'], css, links, environ['tiddlyweb.title'])

    def _footer(self, environ):
        edit_link = self._edit_link(environ)
        return """
<div id="footer">
%s
<div id="badge">This is <a href="http://www.tiddlywiki.org/wiki/TiddlyWeb">TiddlyWeb</a></div>
<div id="usergreet">User %s.</div>
</div>
</body>
</html>
""" % (edit_link, environ['tiddlyweb.usersign']['name'])

    def _edit_link(self, environ):

        if 'editor_tiddlers' in environ['tiddlyweb.config']:
            tiddler_name = environ['wsgiorg.routing_args'][1].get('tiddler_name', None)
            recipe_name = environ['wsgiorg.routing_args'][1].get('recipe_name', '')
            bag_name = environ['wsgiorg.routing_args'][1].get('bag_name', '')
            revision = environ['wsgiorg.routing_args'][1].get('revision', None)

            if tiddler_name and not revision:
                return '<div id="edit"><a href="/edit?tiddler=%s;bag=%s;recipe=%s">Edit</a></div>' \
                        % (tiddler_name, bag_name, recipe_name)

        return ''


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
        log_format = {
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
        message = self.format % log_format
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
        database = Store(environ['tiddlyweb.config']['server_store'][0], environ)
        environ['tiddlyweb.store'] = database
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


class PermissionsExceptor(object):
    """
    Trap permissions exceptions and turn them into HTTP
    exceptions so the errors are propagated to client
    code.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        try:
            output = self.application(environ, start_response)
            return output
        except ForbiddenError, exc:
            raise HTTP403(exc)
        except UserRequiredError, exc:
            # We only send to the challenger on a GET
            # request. Otherwise we're in for major confusion
            # on dealing with redirects and the like in
            # scripts and javascript, where follow
            # behavior is inconsistent.
            if environ['REQUEST_METHOD'] == 'GET':
                url = self._challenge_url(environ)
                raise HTTP302(url)
            raise HTTP403(exc)

    def _challenge_url(self, environ):
        """
        Generate the URL of the challenge system
        so that GET requests are redirected to the
        right place.
        """
        script_name = environ.get('SCRIPT_NAME', '')
        query_string = environ.get('QUERY_STRING', None)
        redirect = script_name
        if query_string:
            redirect += '?%s' % query_string
        redirect = urllib.quote(redirect)
        return '%s/challenge?tiddlyweb_redirect=%s' % (server_base_url(environ), redirect)
