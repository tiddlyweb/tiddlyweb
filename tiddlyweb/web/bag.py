"""
Methods for accessing Bag entities, GET the
tiddlers in the bag, list the available bags,
PUT a Bag as a JSON object.

These need some refactoring.
"""

import urllib
import cgi

from tiddlyweb.bag import Bag
from tiddlyweb.store import Store, NoBagError
from tiddlyweb.serializer import Serializer, NoSerializationError
from tiddlyweb import control
from tiddlyweb.web import util as web
from tiddlyweb.web.tiddlers import send_tiddlers
from tiddlyweb.web.http import HTTP400, HTTP404, HTTP415

def get(environ, start_response):
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag_name = unicode(bag_name, 'utf-8')
    bag_name = web.handle_extension(environ, bag_name)

    bag = _get_bag(environ, bag_name)

    try:
        serialize_type, mime_type = web.get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)
        serializer.object = bag

        content = serializer.to_string()
    except NoSerializationError:
        raise HTTP415, 'Content type not supported: %s' % mime_type

    start_response("200 Ok",
            [('Content-Type', mime_type)])

    return [content]

def get_tiddlers(environ, start_response):
    filter_string = environ['tiddlyweb.query'].get('filter',[''])[0]

    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag_name = unicode(bag_name, 'utf-8')
    bag = _get_bag(environ, bag_name)

    usersign = environ['tiddlyweb.usersign']
    # will raise exception if there are problems
    bag.policy.allows(usersign, 'read')

    tiddlers = control.filter_tiddlers_from_bag(bag, filter_string)
    tmp_bag = Bag('tmp_bag', tmpbag=True)
    for tiddler in tiddlers:
        tmp_bag.add_tiddler(tiddler)

    return send_tiddlers(environ, start_response, tmp_bag)

def import_wiki(environ, start_response):
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag_name = urllib.unquote(bag_name)
    bag_name = unicode(bag_name, 'utf-8')
    bag = _get_bag(environ, bag_name)
    length = environ['CONTENT_LENGTH']
    content = environ['wsgi.input'].read(int(length))
    try:
        serialize_type, mime_type = web.get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)
        serializer.object = bag

        serializer.from_string(content)
    except NoSerializationError:
        raise HTTP415, 'Content type not supported: %s' % mime_type
    except AttributeError, e:
        raise HTTP400, 'Content malformed: %s' % e

    start_response("204 No Content",
            [('Location', '%s/tiddlers' % web.bag_url(environ, bag))])
    return ['']

def list(environ, start_response):
    store = environ['tiddlyweb.store']
    bags = store.list_bags()

    try:
        serialize_type, mime_type = web.get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)

        content = serializer.list_bags(bags)

    except NoSerializationError:
        raise HTTP415, 'Content type not supported: %s' % mime_type

    start_response("200 OK",
            [('Content-Type', mime_type)])

    return [content]

def put(environ, start_response):
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag_name = urllib.unquote(bag_name)
    bag_name = unicode(bag_name, 'utf-8')
    bag_name = web.handle_extension(environ, bag_name)

    bag = Bag(bag_name)
    store = environ['tiddlyweb.store']
    length = environ['CONTENT_LENGTH']

    try:
        serialize_type, mime_type = web.get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)
        serializer.object = bag
        content = environ['wsgi.input'].read(int(length))
        serializer.from_string(content.decode('UTF-8'))

        bag.policy.owner = environ['tiddlyweb.usersign']

        store.put(bag)
    except NoSerializationError:
        raise HTTP415, 'Content type not supported: %s' % serialize_type

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
