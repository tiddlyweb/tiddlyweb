"""
Present or validate a form for getting a username 
and password.
"""

import cgi 
import Cookie

from tiddlyweb.web.challengers import ChallengerInterface
from tiddlyweb.web.util import server_base_url
from tiddlyweb.user import User
from tiddlyweb.store import NoUserError
from sha import sha

class Challenger(ChallengerInterface):

    def challenge_get(self, environ, start_response):
        request_info = cgi.parse_qs(environ.get('QUERY_STRING', ''))
        redirect = request_info.get('tiddlyweb_redirect', [''])[0]
        return self._send_cookie_form(environ, start_response, redirect)

    def challenge_post(self, environ, start_response):
        request_info = cgi.parse_qs(environ['wsgi.input'].read())
        redirect = request_info.get('tiddlyweb_redirect', [''])[0]
        
        try:
            user = request_info['user'][0]
            password = request_info['password'][0]
            return self._validate_and_redirect(environ, start_response, user, password, redirect)
        except KeyError:
            return self._send_cookie_form(environ, start_response, redirect)

    def _send_cookie_form(self, environ, start_response, redirect, status='200 OK',  message=''):
        start_response(status, [
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

    def _validate_and_redirect(self, environ, start_response, username, password, redirect):
        status = '401 Unauthorized'
        try:
            store = environ['tiddlyweb.store']
            secret = environ['tiddlyweb.config']['secret']
            user = User(username)
            store.get(user)
            if user.check_password(password):
                uri = '%s%s' % (server_base_url(environ), redirect)
                cookie = Cookie.SimpleCookie()
                secret_string = sha('%s%s' % (user.usersign, secret)).hexdigest()
                cookie['tiddlyweb_user'] = '%s:%s' % (user.usersign, secret_string)
                cookie['tiddlyweb_user']['path'] = '/'
                start_response('303 See Other', [
                    ('Set-Cookie', cookie.output(header='')),
                    ('Location', uri)
                    ])
                return [uri]
        except KeyError:
            pass
        except NoUserError:
            pass
        return self._send_cookie_form(environ, start_response, redirect, status, 'User or Password no good')
