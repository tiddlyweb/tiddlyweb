
import cgi 

from google.appengine.api import users
from tiddlyweb.web.challengers import ChallengerInterface
from tiddlyweb.web.http import HTTP302

class Challenger(ChallengerInterface):

    def challenge_get(self, environ, start_response):
        request_info = cgi.parse_qs(environ.get('QUERY_STRING', ''))
        redirect = request_info.get('tiddlyweb_redirect', [''])[0]
        
        url = users.create_login_url(redirect)
        raise HTTP302, url
