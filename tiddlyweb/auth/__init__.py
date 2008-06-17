"""
Routines for handling authN and authZ.

Stubs for now.
"""

from tiddlyweb.web.http import HTTP403, HTTP302

class ForbiddenError(Exception):
    pass

class UserRequiredError(Exception):
    pass


class PermissionsExceptor(object):

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        try:
            output = self.application(environ, start_response)
            return output
        except ForbiddenError, e:
            raise HTTP403, e
        except UserRequiredError, e:
            url = self._challenge_url(environ)
            raise HTTP302, url

    def _challenge_url(self, environ):
        scheme = environ['wsgi.url_scheme']
        host = environ.get('HTTP_HOST', '')
        return '%s://%s/challenge' % (scheme, host)



