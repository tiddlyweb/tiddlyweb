"""
An :py:class:`extractor <tiddlyweb.web.extractors.ExtractorInterface>`
that looks at a cookie named ``tiddlyweb_user``.
"""

import Cookie
import logging

from httpexceptor import HTTP400

from tiddlyweb.web.extractors import ExtractorInterface
from tiddlyweb.util import sha


LOGGER = logging.getLogger(__name__)


class Extractor(ExtractorInterface):
    """
    Look in the headers for a cookie named ``tiddlyweb_user``.

    If it is there and the associated hashed value validates against
    a server side secret, return the indicated user.
    """

    def extract(self, environ, start_response):
        """
        Extract the cookie, if there, from the headers
        and attempt to validate its contents.
        """
        try:
            user_cookie = environ['HTTP_COOKIE']
            LOGGER.debug('simple_cookie looking at cookie string: %s',
                    user_cookie)
            cookie = Cookie.SimpleCookie()
            cookie.load(user_cookie.encode('utf-8'))
            cookie_value = cookie['tiddlyweb_user'].value
            secret = environ['tiddlyweb.config']['secret']
            usersign, cookie_secret = cookie_value.rsplit(':', 1)

            if cookie_secret == sha('%s%s' % (usersign, secret)).hexdigest():
                usersign = usersign.decode('utf-8')
                user = self.load_user(environ, usersign)
                return {"name": user.usersign, "roles": user.list_roles()}
        except Cookie.CookieError, exc:
            raise HTTP400('malformed cookie: %s' % exc)
        except (KeyError, ValueError):
            pass
        return False
