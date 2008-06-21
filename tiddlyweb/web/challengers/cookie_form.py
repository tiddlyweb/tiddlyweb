"""
Present or validate a form for getting a username 
and password.
"""

import cgi 
import Cookie

from tiddlyweb.web.challengers import ChallengerInterface
from tiddlyweb.web.util import server_base_url

class Challenger(ChallengerInterface):

    def challenge(self, environ, start_response):
        request_info = cgi.parse_qs(environ.get('QUERY_STRING', ''))
        redirect = request_info.get('tiddlyweb_redirect', [''])[0]
        
        try:
            user = request_info['user'][0]
            password = request_info['password'][0]
            return self._validate_and_redirect(environ, start_response, user, password, redirect)
        except KeyError:
            return self._send_cookie_form(environ, start_response, redirect)

    def _send_cookie_form(self, environ, start_response, redirect, message=''):
        start_response('200 OK', [
            ('Content-Type', 'text/html')
            ])
        return [
"""
<html>
<head><title>Log In</title></head>
<body>
<pre>
%s
<form action="" method="GET">
User: <input name="user" size="40" />
Password <input type="password" name="password" size="40" />
<input type="hidden" name="tiddlyweb_redirect" value="%s" />
<input type="submit" value="submit" />
</form>
</pre>
</body>
</html>
""" % (message, redirect)]

    def _validate_and_redirect(self, environ, start_response, user, password, redirect):
        if user == password:
            uri = '%s%s' % (server_base_url(environ), redirect)
            cookie = Cookie.SimpleCookie()
            cookie['tiddlyweb_insecure_user'] = user
            cookie['tiddlyweb_insecure_user']['path'] = '/'
            start_response('303 See Other', [
                ('Set-Cookie', cookie.output(header='')),
                ('Location', uri)
                ])
            return [uri]
        else:
            return self._send_cookie_form(environ, start_response, redirect, 'User or Password no good')




