"""
Methods for accessing Bag entities, GET the
tiddlers in the bag, list the available bags,
PUT a Bag as a JSON object.

These need some refactoring.
"""

import urllib

from tiddlyweb.bag import Bag
from tiddlyweb.store import Store, NoBagError
from tiddlyweb.serializer import Serializer
from tiddlyweb import control
from tiddlyweb import web
from tiddlyweb.web.http import HTTP404, HTTP415, HTTP403

def get(environ, start_response):
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag_name = web.handle_extension(environ, bag_name)

    bag = _get_bag(environ, bag_name)

    serialize_type, mime_type = web.get_serialize_type(environ)
    if serialize_type not in ['json', 'html', 'text']:
        raise HTTP415, '%s not supported' % serialize_type
    serializer = Serializer(serialize_type)
    serializer.object = bag

    content = serializer.to_string()

    start_response("200 Ok",
            [('Content-Type', mime_type)])

    return [content]

def get_tiddlers(environ, start_response):
    filter_string = urllib.unquote(environ['QUERY_STRING'])

    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag = _get_bag(environ, bag_name)

    usersign = environ['tiddlyweb.usersign']
    if not bag.policy.allows(usersign, 'read'):
        raise HTTP403, '%s may not read on %s' % (usersign, bag.name)

    tiddlers = control.filter_tiddlers_from_bag(bag, filter_string)
    tmp_bag = Bag('tmp_bag', tmpbag=True)
    for tiddler in tiddlers:
        tmp_bag.add_tiddler(tiddler)

    last_modified = None
    if tiddlers:
         last_modified = web.http_date_from_timestamp(_last_modified_tiddler(tmp_bag.list_tiddlers()))
         last_modified = ('Last-Modified', last_modified)

    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)
    serializer.object = tmp_bag

    response = [('Content-Type', mime_type),
            ('Set-Cookie', 'chkHttpReadOnly=false')]

    if last_modified:
        response.append(last_modified)

    start_response("200 OK", response)
    return [serializer.to_string()]

def _last_modified_tiddler(tiddlers):
    return str(max([int(tiddler.modified) for tiddler in tiddlers]))

def list(environ, start_response):
    store = environ['tiddlyweb.store']
    bags = store.list_bags()

    serialize_type, mime_type = web.get_serialize_type(environ)
    if serialize_type not in ['json', 'html', 'text']:
        raise HTTP415, '%s not supported' % serialize_type
    serializer = Serializer(serialize_type)

    start_response("200 OK",
            [('Content-Type', mime_type)])

    return [ serializer.list_bags(bags) ]

def put(environ, start_response):
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag_name = web.handle_extension(environ, bag_name)

    bag = Bag(bag_name)
    store = environ['tiddlyweb.store']
    length = environ['CONTENT_LENGTH']

    serialize_type, mime_type = web.get_serialize_type(environ)
    if serialize_type not in ['json']:
        raise HTTP415, '%s not supported' % serialize_type
    serializer = Serializer(serialize_type)
    serializer.object = bag
    content = environ['wsgi.input'].read(int(length))
    serializer.from_string(content.decode('UTF-8'))

    store.put(bag)

    start_response("204 No Content",
            [('Location', web.bag_url(environ, bag))])

    return []

def _get_bag(environ, bag_name):
    bag = Bag(bag_name)
    store = environ['tiddlyweb.store']
    try:
        store.get(bag)
    except NoBagError, e:
        raise HTTP404, '%s not found, %s' % (bag.name, e)
    return bag

