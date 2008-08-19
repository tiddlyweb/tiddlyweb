"""
An extractor for looking at a cookie
named 'tiddlyweb_user'.
"""

import Cookie

from tiddlyweb.web.extractors import ExtractorInterface
from sha import sha

class Extractor(ExtractorInterface):

    def extract(self, environ, start_response):
        try:
            user_cookie = environ['HTTP_COOKIE']
            cookie = Cookie.SimpleCookie()
            cookie.load(user_cookie)
            cookie_value = cookie['tiddlyweb_user'].value
            secret = environ['tiddlyweb.config']['secret']
            usersign, cookie_secret = cookie_value.split(':')

            if cookie_secret == sha('%s%s' % (usersign, secret)).hexdigest():
                return usersign
        except KeyError:
            pass
        return False

