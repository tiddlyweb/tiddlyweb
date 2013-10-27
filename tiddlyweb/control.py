"""
control provides routines which integrate the basic :py:mod:`model classes
<tiddlyweb.model>` with the rest of the system. The model classes are
intentionally simple. The methods here act as controllers on those classes.

These are primarily related to handling :py:class:`recipes
<tiddlyweb.model.recipe.Recipe>`.
"""

import logging

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import ForbiddenError, UserRequiredError
from tiddlyweb.filters import (FilterIndexRefused, parse_for_filters,
        recursive_filter)
from tiddlyweb.store import NoBagError, StoreError
from tiddlyweb.specialbag import get_bag_retriever, SpecialBagError

from tiddlyweb.fixups import basestring


LOGGER = logging.getLogger(__name__)


def get_tiddlers_from_recipe(recipe, environ=None):
    """
    Return the list of tiddlers that result from processing the ``recipe``.

    This list of tiddlers is unique by title with tiddlers later in the
    recipe taking precedence over those earlier in the recipe.

    The tiddlers returned are empty objects (i.e. not loaded from the
    :py:mod:`store <tiddlyweb.store>`).
    """
    template = recipe_template(environ)
    store = recipe.store
    uniquifier = {}
    for bag, filter_string in recipe.get_recipe(template):

        if isinstance(bag, basestring):
            retriever = get_bag_retriever(environ, bag)
            if not retriever:
                bag = Bag(name=bag)
                retriever = store.list_bag_tiddlers
            else:
                retriever = retriever[0]
        else:
            retriever = store.list_bag_tiddlers

        try:
            for tiddler in filter_tiddlers(retriever(bag), filter_string,
                    environ=environ):
                uniquifier[tiddler.title] = tiddler
        except SpecialBagError as exc:
            raise NoBagError('unable to retrieve from special bag: %s, %s'
                    % (bag, exc))

    return uniquifier.values()


def determine_bag_from_recipe(recipe, tiddler, environ=None):
    """
    Given a ``recipe`` and a ``tiddler`` determine the :py:class:`bag
    <tiddlyweb.model.bag.Bag>` in which this :py:class:`tiddler
    <tiddlyweb.model.tiddler.Tiddler>` can be found. This is different from
    :py:func:`determine_bag_for_tiddler`. That one finds the bag the tiddler
    *could* be in. This is the bag the tiddler *is* in.

    This is done by reversing the recipe's list, and filtering each bag
    according to any :py:mod:`filters <tiddlyweb.filters>` present. The
    resulting tiddlers are checked.

    If an ``indexer`` is configured use the index to determine if a tiddler
    exists in a bag.
    """
    store = recipe.store
    template = recipe_template(environ)
    try:
        indexer = environ.get('tiddlyweb.config', {}).get('indexer', None)
        if indexer:
            index_module = __import__(indexer, {}, {}, ['index_query'])
        else:
            index_module = None
    except (AttributeError, KeyError):
        index_module = None

    for bag, filter_string in reversed(recipe.get_recipe(template)):
        bag = _look_for_tiddler_in_bag(tiddler, bag,
                filter_string, environ, store, index_module)
        if bag:
            return bag

    raise NoBagError('no suitable bag for %s' % tiddler.title)


def _look_for_tiddler_in_bag(tiddler, bag, filter_string,
        environ, store, index_module):
    """
    Look up the indicated tiddler in a bag, filtered by filter_string.
    """
    if isinstance(bag, basestring):
        bag = Bag(name=bag)
    if store:
        bag = store.get(bag)

    def _query_index(bag):
        """
        Try looking in an available index to see if the tiddler exists.
        """
        kwords = {'id': '%s:%s' % (bag.name, tiddler.title)}
        try:
            tiddlers = index_module.index_query(environ, **kwords)
            if list(tiddlers):
                LOGGER.debug(
                        'satisfied recipe bag query via filter index: %s:%s',
                        bag.name, tiddler.title)
                return bag
        except StoreError as exc:
            raise FilterIndexRefused('unable to index_query: %s' % exc)
        return None

    def _query_bag(bag):
        """
        Look in a bag to see if tiddler is in there.
        """
        for candidate_tiddler in _filter_tiddlers_from_bag(bag,
                filter_string, environ=environ):
            if tiddler.title == candidate_tiddler.title:
                return bag
        return None

    if not filter_string and index_module:
        try:
            found_bag = _query_index(bag)
        except FilterIndexRefused:
            LOGGER.debug('determined bag filter refused')
            found_bag = _query_bag(bag)
        if found_bag:
            return bag
    else:
        found_bag = _query_bag(bag)
        if found_bag:
            return found_bag

    return None


def readable_tiddlers_by_bag(store, tiddlers, usersign):
    """
    Yield those tiddlers which are readable by the current ``usersign``.
    This means, depending on the ``read`` constraint on the
    :py:class:`tiddler's <tiddlyweb.model.tiddler.Tiddler>`
    :py:class:`bag's <tiddlyweb.model.bag.Bag>` :py:class:`policy
    <tiddlyweb.model.policy.Policy>`, yield or not.
    """
    bag_readable = {}

    for tiddler in tiddlers:
        try:
            if bag_readable[tiddler.bag]:
                yield tiddler
        except KeyError:
            bag = Bag(tiddler.bag)
            try:
                bag = store.get(bag)
            except NoBagError:
                pass
            try:
                bag.policy.allows(usersign, 'read')
                bag_readable[tiddler.bag] = True
                yield tiddler
            except(ForbiddenError, UserRequiredError):
                bag_readable[tiddler.bag] = False


def determine_bag_for_tiddler(recipe, tiddler, environ=None):
    """
    Return the :py:class:`bag <tiddlyweb.model.bag.Bag>` which this
    :py:class:`tiddler <tiddlyweb.model.tiddler.Tiddler>` would be in
    if we were to save it to the named :py:class:`recipe
    <tiddlyweb.model.recipe.Recipe>` rather than to a bag.

    This is done reversing the recipe list and seeing if the
    tiddler passes the constraint of the bag and its associated
    :py:mod:`filter <tiddlyweb.filters>`. If bag+filter is true,
    return that bag.
    """
    template = recipe_template(environ)
    for bag, filter_string in reversed(recipe.get_recipe(template)):
        for candidate_tiddler in filter_tiddlers([tiddler],
                filter_string, environ=environ):
            if tiddler.title == candidate_tiddler.title:
                if isinstance(bag, basestring):
                    bag = Bag(name=bag)
                return bag

    raise NoBagError('no suitable bag for %s' % tiddler.title)


def get_tiddlers_from_bag(bag):
    """
    Yield the individual :py:class:`tiddlers <tiddlyweb.model.tiddler.Tiddler>`
    that are in a :py:class:`bag <tiddlyweb.model.bag.Bag>`.

    The tiddlers return are empty objects that have not been loaded from
    the :py:class:`store <tiddlyweb.store.Store>`.

    Rarely used, see :py:func:`tiddlyweb.store.Store.list_bag_tiddlers`.
    """
    for tiddler in bag.store.list_bag_tiddlers(bag):
        yield tiddler


def filter_tiddlers(tiddlers, filters, environ=None):
    """
    Return a generator of tiddlers resulting from filtering the provided
    iterator of tiddlers by the provided :py:mod:`filters <tiddlyweb.filters>`.

    If filters is a string, it will be :py:func:`parsed for filters
    <tiddlyweb.filters.parse_for_filters>`.
    """
    if isinstance(filters, basestring):
        filters, _ = parse_for_filters(filters, environ)
    return recursive_filter(filters, tiddlers)


def _filter_tiddlers_from_bag(bag, filters, environ=None):
    """
    Return the list of tiddlers resulting from filtering bag by filter.
    The filter is a string that will be parsed to a list of filters.
    """
    indexable = bag

    if isinstance(filters, basestring):
        filters, _ = parse_for_filters(filters, environ)
    return recursive_filter(filters, bag.store.list_bag_tiddlers(bag),
            indexable=indexable)


def recipe_template(environ):
    """
    Provide a means to specify custom ``{{ key }}`` values in
    :py:class:`recipes <tiddlyweb.model.recipe.Recipe>` which are then
    replaced with the value specified in
    ``environ['tiddlyweb.recipe_template']``.

    This allows recipes to be dynamic in the face of conditions in the
    current request.
    """
    template = {}
    if environ:
        template = environ.get('tiddlyweb.recipe_template', {})
        try:
            template['user'] = environ['tiddlyweb.usersign']['name']
        except KeyError:
            pass

    return template
