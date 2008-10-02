"""
Methods for accessing Bag entities, GET the
tiddlers in the bag, list the available bags,
PUT a Bag as a JSON object.

These need some refactoring.
"""

import urllib

from tiddlyweb.bag import Bag
from tiddlyweb.store import NoBagError, StoreMethodNotImplemented
from tiddlyweb.serializer import Serializer, NoSerializationError
from tiddlyweb import control
from tiddlyweb.web import util as web
from tiddlyweb.web.tiddlers import send_tiddlers
from tiddlyweb.web.http import HTTP400, HTTP404, HTTP415


def delete(environ, start_response):
    # XXX refactor out a _determine_bag or _determine_bag_name
    # lots of duplication going on here.
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag_name = urllib.unquote(bag_name)
    bag_name = unicode(bag_name, 'utf-8')
    bag_name = web.handle_extension(environ, bag_name)

    usersign = environ['tiddlyweb.usersign']

    bag = _get_bag(environ, bag_name)
    bag.policy.allows(usersign, 'delete')
    # reuse the store attribute that was set on the
    # bag when we "got" it.
    # we don't need to check for existence here because
    # the above get already did
    try:
        bag.store.delete(bag)
    except StoreMethodNotImplemented:
        raise HTTP400('Bag DELETE not supported')

    start_response("204 No Content", [])
    return []


def get(environ, start_response):
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag_name = urllib.unquote(bag_name)
    bag_name = unicode(bag_name, 'utf-8')
    bag_name = web.handle_extension(environ, bag_name)

    bag = _get_bag(environ, bag_name)

    try:
        serialize_type, mime_type = web.get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)
        serializer.object = bag

        content = serializer.to_string()
    except NoSerializationError:
        raise HTTP415('Content type not supported: %s' % mime_type)

    start_response("200 Ok",
            [('Content-Type', mime_type)])

    return [content]


def get_tiddlers(environ, start_response):
    filter_string = web.filter_query_string(environ)

    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag_name = urllib.unquote(bag_name)
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
        raise HTTP415('Content type not supported: %s' % mime_type)
    except AttributeError, e:
        raise HTTP400('Content malformed: %s' % e)

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
        raise HTTP415('Content type not supported: %s' % mime_type)

    start_response("200 OK",
            [('Content-Type', mime_type)])

    return [content]

def bag_createp(environ, usersign):
    return True;
    # raise UserRequiredError
    # raise ForbiddenError

def put(environ, start_response):
    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag_name = urllib.unquote(bag_name)
    bag_name = unicode(bag_name, 'utf-8')
    bag_name = web.handle_extension(environ, bag_name)

    bag = Bag(bag_name)
    store = environ['tiddlyweb.store']
    length = environ['CONTENT_LENGTH']

    usersign = environ['tiddlyweb.usersign']

    try:
        store.get(bag)
        bag.policy.allows(usersign, 'manage')
    except NoBagError:
        bag_createp(environ, usersign)

    try:
        serialize_type, mime_type = web.get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)
        serializer.object = bag
        content = environ['wsgi.input'].read(int(length))
        serializer.from_string(content.decode('UTF-8'))

        bag.policy.owner = usersign['name']

        store.put(bag)
    except NoSerializationError:
        raise HTTP415('Content type not supported: %s' % serialize_type)

    start_response("204 No Content",
            [('Location', web.bag_url(environ, bag))])

    return []


def _get_bag(environ, bag_name):
    bag = Bag(bag_name)
    store = environ['tiddlyweb.store']
    try:
        store.get(bag)
    except NoBagError, e:
        raise HTTP404('%s not found, %s' % (bag.name, e))
    return bag
