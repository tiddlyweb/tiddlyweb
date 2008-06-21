
import Cookie

from tiddlyweb.web.extractors import ExtractorInterface

class Extractor(ExtractorInterface):

    def extract(self, environ, start_response):
        try:
            user_cookie = environ['HTTP_COOKIE']
            cookie = Cookie.SimpleCookie()
            cookie.load(user_cookie)
            usersign = cookie['tiddlyweb_insecure_user'].value
            return usersign
        except KeyError:
            return False
        return False

