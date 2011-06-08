"""
Routines for accessing a remote URI as if it where
a remote bag of tiddlers, for use in a recipe. The
idea is that if the bag portion of a line in a recipe
is a URI, then we'll get whatever is on the other end
as if it were tiddlers, and then filter accordingly, 
if the recipe line has a filter.

At first pass this is a way of federating bags on
disparate tiddlyweb servers, but one can imagine adapting
it to work with non tiddler or tiddlyweb things.
"""

import httplib2
import re
import simplejson

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.util import pseudo_binary
from tiddlyweb.web.util import encode_name
from tiddlyweb.serializer import Serializer


class RemoteBagError(Exception):
    pass


def is_remote(environ, uri):
    """
    Return the tool for retrieving remote if this is a remote bag.
    Otherwise None.
    """
    if uri.startswith('http:') or uri.startswith('https:'):

        def curry(environ, func):
            def actor(bag):
                return func(environ, bag)
            return actor

        return (curry(environ, get_remote_tiddlers),
                curry(environ, get_remote_tiddler))

    return None



def retrieve_remote(uri, accept=None):
    http = httplib2.Http('.cache')
    try:
        if accept:
            response, content = http.request(uri, headers={'Accept': accept})
        else:
            response, content = http.request(uri)
    except httplib2.HttpLib2Error, exc:
        raise RemoteBagError('unable to retrieve remote: %s: %s'
                % (uri, exc))

    if response['status'] == '200' or response['status'] == '304':
        return response, content
    else:
        raise RemoteBagError('bad response from remote: %s: %s: %s'
                % (uri, response['status'], content))


def get_remote_tiddlers(environ, uri):
    """
    Retrieve the tiddlers at uri, yield as skinny tiddlers.
    """
    handler = _determine_remote_handler(environ, uri)[0]
    return handler(environ, uri)


def get_remote_tiddler(environ, tiddler):
    """
    Retrieve the tiddler from its remote location.
    """
    uri = tiddler.bag
    handler = _determine_remote_handler(environ, uri)[1]
    return handler(environ, uri, tiddler.title)


def get_remote_tiddlers_html(environ, uri):
    """
    Retrieve a page of HTML as a single yielded tiddler.
    """
    response, content = retrieve_remote(uri)
    try:
        title = content.split('<title>', 1)[1].split('</title>', 1)[0]
    except IndexError:
        title = uri
    yield Tiddler(title, uri)


def get_remote_tiddler_html(environ, uri, title):
    """
    Retrieve a webpage as a tiddler. Type comes from
    content-type. Text is set to the body.
    TODO: use response metadata to set other attributes
    """
    response, content = retrieve_remote(uri)
    tiddler = Tiddler(title, uri)
    try:
        type = response['content-type'].split(';', 1)[0]
    except KeyError:
        type = 'text/html'
    if pseudo_binary(type):
        tiddler.text = content.decode('utf-8', 'replace')
    else:
        tiddler.text = content
    tiddler.type = type
    return tiddler


def _get_tiddlyweb_tiddler(environ, uri, title):
    url = uri + '/' + encode_name(title)
    response, content = retrieve_remote(url, accept='application/json')
    return _process_json_tiddler(environ, content, uri)


def _get_tiddlyweb_tiddlers(environ, uri):
    response, content = retrieve_remote(uri, accept='application/json')
    return _process_json_tiddlers(environ, content, uri)


PATTERNS = [(re.compile(r'.*/bags/[^/]+/tiddlers$'),
    (_get_tiddlyweb_tiddlers, _get_tiddlyweb_tiddler))]


def _determine_remote_handler(environ, uri):
    """
    Determine which remote handler to use for this uri.
    """
    config = environ['tiddlyweb.config']
    if len(PATTERNS) == 1:
        for rule, target in config.get('remote_handlers', []):
            PATTERNS.append((re.compile(rule), target))
    for pattern, target in PATTERNS:
        if pattern.search(uri):
            return target
    # do default, getting raw html
    return (get_remote_tiddlers_html, get_remote_tiddler_html)


def _process_json_tiddler(environ, content, uri):
    content = content.decode('utf-8')
    data = simplejson.loads(content)
    tiddler = Tiddler(data['title'], uri)
    serializer = Serializer('json', environ)
    serializer.object = tiddler
    return serializer.from_string(content)


def _process_json_tiddlers(environ, content, uri):
    data = simplejson.loads(content.decode('utf-8'))

    for item in data:
        tiddler = Tiddler(item['title'], uri)
        yield tiddler
