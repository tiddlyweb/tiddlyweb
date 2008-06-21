
from base64 import b64decode

from tiddlyweb.web.extractors import ExtractorInterface

class Extractor(ExtractorInterface):

    def extract(self, environ, start_response):
        user_info = environ.get('HTTP_AUTHORIZATION', None)
        if user_info is None:
            return False
        if user_info.startswith('Basic'):
            user_info = user_info.strip().split(' ')[1]
            candidate_username, password = b64decode(user_info).split(':')
            if candidate_username == password:
                return candidate_username
        return False

