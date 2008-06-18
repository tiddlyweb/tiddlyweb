import urllib
import cgi
from Cookie import SimpleCookie

from tiddlyweb.web.http import HTTP401

auth_systems = ['cookie_form']

def _challenger_url(environ, system):
    scheme = environ['wsgi.url_scheme']
    host = environ.get('HTTP_HOST', '')
    request_info = cgi.parse_qs(environ.get('QUERY_STRING', ''))
    redirect = request_info.get('tiddlyweb_redirect', [''])[0]
    if len(redirect):
        redirect = '?tiddlyweb_redirect=%s' % redirect
    else:
        redirect = ''
    return '%s://%s/challenge/%s%s' % (scheme, host, system, redirect)

def base(environ, start_response):
    start_response('401 Unauthorized', [
        ('Content-Type', 'text/html')
        ])
    return ['<li><a href="%s">%s</a></li>' % (uri, uri) for uri in \
            [_challenger_url(environ, system)  for system in auth_systems]]

def challenge(environ, start_response):
    challenger = environ['wsgiorg.routing_args'][1]['challenger']
    # do something with the challenger when we have the hoops worked out
    return _cookie_form(environ, start_response)

def _cookie_form(environ, start_response):
    request_info = cgi.parse_qs(environ.get('QUERY_STRING', ''))
    redirect = request_info.get('tiddlyweb_redirect', [''])[0]
    
    try:
        user = request_info['user'][0]
        password = request_info['password'][0]
        return _validate_and_redirect(environ, start_response, user, password, redirect)
    except KeyError:
        return _send_cookie_form(environ, start_response, redirect)

def _send_cookie_form(environ, start_response, redirect, message=''):
    start_response('200 OK', [
        ('Content-Type', 'text/html')
        ])
    return ["""
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

def _validate_and_redirect(environ, start_response, user, password, redirect):
    if user == password:
        scheme = environ['wsgi.url_scheme']
        host = environ.get('HTTP_HOST', '')
        uri = '%s://%s%s' % (scheme, host, redirect)
        cookie = SimpleCookie()
        cookie['tiddlyweb_insecure_user'] = user
        cookie['tiddlyweb_insecure_user']['path'] = '/'
        start_response('303 See Other', [
            ('Set-Cookie', cookie.output(header='')),
            ('Location', uri)
            ])
        return [uri]
    else:
        return _send_cookie_form(environ, start_response, redirect, 'User or Password no good')




