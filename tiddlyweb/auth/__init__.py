"""
Routines for managing the handling of authN and authZ.
"""

import urllib

from tiddlyweb.web.http import HTTP403, HTTP302
from tiddlyweb.web.util import server_base_url


class ForbiddenError(Exception):
    """
    The provided user cannot do this action.
    """
    pass


class UserRequiredError(Exception):
    """
    To do this action a user is required.
    """
    pass


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
