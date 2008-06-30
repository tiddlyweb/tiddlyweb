import urllib
import cgi
from Cookie import SimpleCookie

from tiddlyweb.web.http import HTTP401, HTTP404
from tiddlyweb.web.util import server_base_url

def _challenger_url(environ, system):
    scheme = environ['wsgi.url_scheme']
    host = environ.get('HTTP_HOST', '')
    request_info = cgi.parse_qs(environ.get('QUERY_STRING', ''))
    redirect = request_info.get('tiddlyweb_redirect', [''])[0]
    if len(redirect):
        redirect = '?tiddlyweb_redirect=%s' % redirect
    else:
        redirect = ''
    return '%s/challenge/%s%s' % (server_base_url(environ), system, redirect)

def base(environ, start_response):
    auth_systems = environ['tiddlyweb.config']['auth_systems']
    start_response('401 Unauthorized', [
        ('Content-Type', 'text/html')
        ])
    return ['<li><a href="%s">%s</a></li>' % (uri, uri) for uri in \
            [_challenger_url(environ, system)  for system in auth_systems]]

def challenge_get(environ, start_response):
    challenger = _determine_challenger(environ, start_response)
    return challenger.challenge_get(environ, start_response)

def challenge_post(environ, start_response):
    challenger = _determine_challenger(environ, start_response)
    return challenger.challenge_post(environ, start_response)

def _determine_challenger(environ, start_response):
    challenger_name = environ['wsgiorg.routing_args'][1]['challenger']
    # If the challenger is not in config, do a 404, we don't want
    # to import any old code.
    if challenger_name not in environ['tiddlyweb.config']['auth_systems']:
        raise HTTP404, 'Challenger Not Found'
    try:
        imported_module = __import__('tiddlyweb.web.challengers.%s' % challenger_name,
                {}, {}, ['Challenger'])
    except ImportError:
        try:
            imported_module = __import__(challenger_name, {}, {}, ['Challenger'])
        except ImportError, e:
            raise HTTP404, 'Unable to import challenger %s: %s' % (challenger_name, e)
    return imported_module.Challenger()
