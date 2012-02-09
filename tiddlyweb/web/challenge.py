"""
WSGI App for running the base challenge system, which lists and links
the available challengers. If there is only one, redirect to it.
"""

import urllib

from tiddlyweb.web.http import HTTP302, HTTP404
from tiddlyweb.web.util import server_base_url, get_route_value


def base(environ, start_response):
    """
    The basic listing page that shows all available
    challenger systems. If there is only one, we
    redirect to that instead of listing.
    """
    auth_systems = environ['tiddlyweb.config']['auth_systems']
    if len(auth_systems) == 1:
        raise HTTP302(_challenger_url(environ, auth_systems[0]))
    start_response('401 Unauthorized', [('Content-Type', 'text/html')])
    environ['tiddlyweb.title'] = 'Login Challengers'

    challenger_info = []
    for system in auth_systems:
        uri = _challenger_url(environ, system)
        try:
            challenger = _get_challenger_module(system)
            label = getattr(challenger, 'desc', uri)
            challenger_info.append((uri, label))
        except ImportError:
            pass

    return ['<li><a href="%s">%s</a></li>' % (uri, label) for uri, label in
            challenger_info]


def challenge_get(environ, start_response):
    """
    Dispatch a GET request to the chosen challenger.
    """
    challenger = _determine_challenger(environ)
    return challenger.challenge_get(environ, start_response)


def challenge_post(environ, start_response):
    """
    Dispatch a POST request to the chosen challenger.
    """
    challenger = _determine_challenger(environ)
    return challenger.challenge_post(environ, start_response)


def _challenger_url(environ, system):
    """
    Return the proper URL for a specific challenger system.
    """
    default_redirect = '%s/' % environ['tiddlyweb.config']['server_prefix']
    redirect = (environ['tiddlyweb.query'].get('tiddlyweb_redirect',
            [default_redirect])[0])
    redirect = '?tiddlyweb_redirect=%s' % urllib.quote(
            redirect.encode('utf-8'), safe='')
    return '%s/challenge/%s%s' % (server_base_url(environ), system, redirect)


def _determine_challenger(environ, challenger_name=None):
    """
    Determine which challenger we are using and import it as necessary.
    """
    if challenger_name is None:
        challenger_name = get_route_value(environ, 'challenger')
    # If the challenger is not in config, do a 404, we don't want
    # to import any old code.
    if challenger_name not in environ['tiddlyweb.config']['auth_systems']:
        raise HTTP404('Challenger Not Found')
    try:
        return _get_challenger_module(challenger_name)
    except ImportError, exc:
        raise HTTP404('Unable to import challenger %s: %s' %
                (challenger_name, exc))


def _get_challenger_module(challenger_name):
    """
    Return given challenger's module, importing it as necessary.
    """
    try:
        imported_module = __import__('tiddlyweb.web.challengers.%s' %
                challenger_name, {}, {}, ['Challenger'])
    except ImportError:
        imported_module = __import__(challenger_name, {}, {}, ['Challenger'])
    return imported_module.Challenger()
