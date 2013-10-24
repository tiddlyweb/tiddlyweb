"""
Methods for accessing :py:class:`Bag <tiddlyweb.model.bag.Bag>` entities.
"""

from httpexceptor import HTTP400, HTTP404, HTTP409, HTTP415

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.collections import Tiddlers
from tiddlyweb.model.policy import create_policy_check
from tiddlyweb.store import NoBagError, StoreMethodNotImplemented
from tiddlyweb.serializer import (Serializer, NoSerializationError,
        BagFormatError)
from tiddlyweb.web import util as web
from tiddlyweb.web.sendentity import send_entity
from tiddlyweb.web.sendtiddlers import send_tiddlers
from tiddlyweb.web.listentities import list_entities
from tiddlyweb.web.validator import validate_bag, InvalidBagError


def delete(environ, start_response):
    """
    Handle ``DELETE`` on a single bag URI.

    Remove the :py:class:`bag <tiddlyweb.model.bag.Bag>` and the
    :py:class:`tiddlers <tiddlyweb.model.tiddler.Tiddler>` within
    from the :py:class:`store <tiddlyweb.store.Store>`.

    How the store chooses to handle remove and what it means is
    up to the store.
    """
    bag_name = web.get_route_value(environ, 'bag_name')
    bag_name = web.handle_extension(environ, bag_name)

    usersign = environ['tiddlyweb.usersign']

    bag = _get_bag(environ, bag_name)
    bag.policy.allows(usersign, 'manage')
    # reuse the store attribute that was set on the
    # bag when we "got" it.
    # we don't need to check for existence here because
    # the above get already did
    try:
        store = environ['tiddlyweb.store']
        store.delete(bag)
    except StoreMethodNotImplemented:
        raise HTTP400('Bag DELETE not supported')

    start_response("204 No Content", [])
    return []


def get(environ, start_response):
    """
    Handle ``GET`` on a single bag URI.

    Get a representation in some serialization determined by
    :py:mod:`tiddlyweb.web.negotiate` of a :py:class:`bag
    <tiddlyweb.model.bag.Bag>` (the bag itself, not the tiddlers within).
    """
    bag_name = web.get_route_value(environ, 'bag_name')
    bag_name = web.handle_extension(environ, bag_name)
    bag = _get_bag(environ, bag_name)

    bag.policy.allows(environ['tiddlyweb.usersign'], 'manage')

    return send_entity(environ, start_response, bag)


def get_tiddlers(environ, start_response):
    """
    Handle ``GET`` on a tiddlers-within-a-bag URI.

    Get a list representation of the :py:class:`tiddlers
    <tiddlyweb.model.tiddler.Tiddler>` in a :py:class:`bag
    <tiddlyweb.model.bag.Bag>`.

    The information sent is dependent on the serialization chosen
    via :py:mod:`tiddlyweb.web.negotiate`.
    """
    store = environ['tiddlyweb.store']
    filters = environ['tiddlyweb.filters']
    bag_name = web.get_route_value(environ, 'bag_name')
    bag = _get_bag(environ, bag_name)
    title = 'Tiddlers From Bag %s' % bag.name
    title = environ['tiddlyweb.query'].get('title', [title])[0]

    usersign = environ['tiddlyweb.usersign']
    # will raise exception if there are problems
    bag.policy.allows(usersign, 'read')

    tiddlers = Tiddlers(title=title)
    if not filters:
        tiddlers.store = store
    tiddlers.bag = bag_name

    # A special bag can raise NoBagError here.
    try:
        for tiddler in store.list_bag_tiddlers(bag):
            tiddlers.add(tiddler)
    except NoBagError as exc:
        raise HTTP404('%s not found, %s' % (bag.name, exc))

    tiddlers.link = '%s/tiddlers' % web.bag_url(environ, bag, full=False)

    return send_tiddlers(environ, start_response, tiddlers=tiddlers)


def list_bags(environ, start_response):
    """
    Handle ``GET`` on the bags URI.

    List all the :py:class:`bags <tiddlyweb.model.bag.Bag>` that are
    readable by the current usersign.

    The information sent is dependent on the serialization chosen
    via :py:mod:`tiddlyweb.web.negotiate`.
    """
    return list_entities(environ, start_response, 'list_bags')


def put(environ, start_response):
    """
    Handle ``PUT`` on a single bag URI.

    Put a :py:class:`bag <tiddlyweb.model.bag.Bag>` to the server,
    meaning the description and policy of the bag, if :py:class:`policy
    <tiddlyweb.model.policy.Policy>` allows.
    """
    bag_name = web.get_route_value(environ, 'bag_name')
    bag_name = web.handle_extension(environ, bag_name)

    bag = Bag(bag_name)
    store = environ['tiddlyweb.store']
    length, _ = web.content_length_and_type(environ)

    usersign = environ['tiddlyweb.usersign']

    try:
        bag = store.get(bag)
        bag.policy.allows(usersign, 'manage')
    except NoBagError:
        create_policy_check(environ, 'bag', usersign)

    try:
        serialize_type = web.get_serialize_type(environ)[0]
        serializer = Serializer(serialize_type, environ)
        serializer.object = bag
        content = web.read_request_body(environ, length)
        serializer.from_string(content.decode('utf-8'))

        bag.policy.owner = usersign['name']

        _validate_bag(environ, bag)
        store.put(bag)
    except BagFormatError as exc:
        raise HTTP400('unable to put bag: %s' % exc)
    except TypeError:
        raise HTTP400('Content-type header required')
    except NoSerializationError:
        raise HTTP415('Content type not supported: %s' % serialize_type)

    start_response("204 No Content",
            [('Location', web.bag_url(environ, bag))])

    return []


def _validate_bag(environ, bag):
    """
    Unless bag is valid raise a `409` with the reason why.
    """
    try:
        validate_bag(bag, environ)
    except InvalidBagError as exc:
        raise HTTP409('Bag content is invalid: %s' % exc)


def _get_bag(environ, bag_name):
    """
    Get the named bag out of the store.
    """
    store = environ['tiddlyweb.store']
    bag = Bag(bag_name)
    try:
        bag = store.get(bag)
    except NoBagError as exc:
        raise HTTP404('%s not found, %s' % (bag.name, exc))
    return bag
