"""
A chronicle is a stack of tiddlers, usually revisions of
one tiddler. By POSTing a chronicle of tiddlers originally
named A to tiddler B, we can effectively rename a tiddler
while preserving history.
"""

import simplejson 

from httpexceptor import HTTP400, HTTP409, HTTP412, HTTP415

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.store import NoTiddlerError
from tiddlyweb.web.util import (get_route_value, content_length_and_type,
        tiddler_url, check_bag_constraint)
from tiddlyweb.web.handler.tiddler import validate_tiddler_headers


def post_revisions(environ, start_response):
    """
    Take a collection of JSON tiddlers, each with a
    text key and value, and process them into the store.
    That collection is known as a TiddlerChronicle.
    """
    tiddler_name = get_route_value(environ, 'tiddler_name')
    bag_name = get_route_value(environ, 'bag_name')
    tiddler = Tiddler(tiddler_name, bag_name)
    return _post_tiddler_revisions(environ, start_response, tiddler)


def _post_tiddler_revisions(environ, start_response, tiddler):
    """
    We have a list of revisions, put them in a new place.
    """
    length, content_type = content_length_and_type(environ)

    if content_type != 'application/json':
        raise HTTP415('application/json required')

    # we need a matching etag in order to be able to do
    # this operation. This will raise exception if there
    # isn't a valid etag.
    _require_valid_etag_for_write(environ, tiddler)

    bag = Bag(tiddler.bag)
    #  both create and write required for this action
    check_bag_constraint(environ, bag, 'create')
    check_bag_constraint(environ, bag, 'write')

    content = environ['wsgi.input'].read(int(length))

    _store_tiddler_revisions(environ, content, tiddler)

    response = [('Location', tiddler_url(environ, tiddler))]
    start_response("204 No Content", response)

    return []


def _require_valid_etag_for_write(environ, tiddler):
    """
    Unless there is an etag and it is valid
    we send a 412.
    """
    incoming_etag = environ.get('HTTP_IF_MATCH', None)
    if not incoming_etag:
        raise HTTP412('If Match header required to update tiddlers.')
    tiddler_copy = Tiddler(tiddler.title, tiddler.bag)
    try:
        tiddler_copy = environ['tiddlyweb.store'].get(tiddler_copy)
    except NoTiddlerError:
        tiddler_copy.revision = 0
    return validate_tiddler_headers(environ, tiddler_copy)


def _store_tiddler_revisions(environ, content, tiddler):
    """
    Given json revisions in content, store them
    as a revision history to tiddler.
    """
    try:
        json_tiddlers = simplejson.loads(content)
    except ValueError, exc:
        raise HTTP409('unable to handle json: %s' % exc)

    store = environ['tiddlyweb.store']
    serializer = Serializer('json', environ)
    serializer.object = tiddler
    try:
        for json_tiddler in reversed(json_tiddlers):
            json_string = simplejson.dumps(json_tiddler)
            serializer.from_string(json_string.decode('utf-8'))
            store.put(tiddler)
    except NoTiddlerError, exc:
        raise HTTP400('Unable to store tiddler revisions: %s', exc)
