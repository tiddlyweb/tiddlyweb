"""
Routines for managing the handling of authN and authZ.
"""

import urllib

from tiddlyweb.web.http import HTTP403, HTTP302

class ForbiddenError(Exception):
    pass

class UserRequiredError(Exception):
    pass


class PermissionsExceptor(object):

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response, exc_info=None):
        try:
            output = self.application(environ, start_response)
            return output
        except ForbiddenError, e:
            raise HTTP403, e
        except UserRequiredError, e:
            """
            We only send to the challenger on a GET 
            request. Otherwise we're in for major confusion
            on dealing with redirects and the like in 
            scripts and javascript, where follow 
            behavior is confused.
            """
            if environ['REQUEST_METHOD'] == 'GET':
                url = self._challenge_url(environ)
                raise HTTP302, url
            raise HTTP403, e

    def _challenge_url(self, environ):
        scheme = environ['wsgi.url_scheme']
        host = environ.get('HTTP_HOST', '')
        script_name = environ.get('SCRIPT_NAME', '')
        query_string = environ.get('QUERY_STRING', None)
        redirect = script_name
        if query_string:
            redirect += '?%s' % query_string
        redirect = urllib.quote(redirect)
        return '%s://%s/challenge?tiddlyweb_redirect=%s' % (scheme, host, redirect)



