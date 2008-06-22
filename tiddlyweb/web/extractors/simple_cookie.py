"""
An extractor for looking at a cookie
named 'tiddlyweb_insecure_user'. Thus
named because the value in the cookie cannot
be considered secure because it is easily 
spoofed.

Here for testing and development.
"""

import Cookie

from tiddlyweb.web.extractors import ExtractorInterface
from tiddlyweb.user import User

class Extractor(ExtractorInterface):

    def extract(self, environ, start_response):
        try:
            user_cookie = environ['HTTP_COOKIE']
            cookie = Cookie.SimpleCookie()
            cookie.load(user_cookie)
            usersign = cookie['tiddlyweb_insecure_user'].value
            user = User(usersign)
            store = environ['tiddlyweb.store']
            store.get(user)
            return user.usersign
        except KeyError:
            pass
        except NoUserError:
            pass
        return False

