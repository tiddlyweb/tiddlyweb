"""
Store TiddlyWeb entities to a configured persistence layer.

This module provides the facade for accessing one of many possible
modules which provide storage for entities. It provides a general
interface to get, put, delete or list :py:mod:`entities <tiddlyweb.model>`.

Each of the single entity methods can be augmented with hooks
provided by plugins. This allows actions to be performed based on
data in the store being retrieved or updated, such as updating an
index.
"""

from copy import deepcopy

from tiddlyweb.specialbag import get_bag_retriever, SpecialBagError
from tiddlyweb.model.policy import Policy
from tiddlyweb.util import superclass_name

from tiddlyweb.fixups import basestring


class StoreError(IOError):
    """
    Base Exception for Store Exceptions.
    """
    def __str__(self):
        # self.args may or may not be a string, and when that
        # is the case is proving rather difficult to tell between
        # minor and micro versions of Python. woot!
        # So here we do some extra work.
        message = []
        for arg in self.args:
            if isinstance(arg, basestring):
                message.append(arg)
        return ' '.join(message)


class StoreMethodNotImplemented(StoreError):
    """
    A :py:class:`tiddlyweb.stores.StorageInterface` does not implement
    this method.
    """
    pass


class NoBagError(StoreError):
    """
    No :py:class:`tiddlyweb.model.bag.Bag` was found.
    """
    pass


class NoRecipeError(StoreError):
    """
    No :py:class:`tiddlyweb.model.recipe.Recipe` was found.
    """
    pass


class NoTiddlerError(StoreError):
    """
    No :py:class:`tiddlyweb.model.tiddler.Tiddler` was found.
    """
    pass


class NoUserError(StoreError):
    """
    No :py:class:`tiddlyweb.model.user.User` was found.
    """
    pass


class StoreLockError(StoreError):
    """
    This process was unable to get a lock on the store.
    """
    pass


class StoreEncodingError(StoreError):
    """
    Something about an entity made it impossible to be encoded to the
    form required by the store.
    """
    pass


EMPTY_HOOKS = {
        'put': [],
        'delete': [],
        'get': [],
}
HOOKS = {
        'recipe': deepcopy(EMPTY_HOOKS),
        'bag': deepcopy(EMPTY_HOOKS),
        'tiddler': deepcopy(EMPTY_HOOKS),
        'user': deepcopy(EMPTY_HOOKS),
}


class Store(object):
    """
    A Store is a facade to an implementation of
    :py:class:`tiddlyweb.stores.StorageInterface` to handle the storage
    and retrieval of all :py:mod:`entities <tiddlyweb.model>` in the
    TiddlyWeb system.

    Because of the facade system it is relatively straightforward to
    create diverse storage systems for all sorts of or multiple media. In
    addition stores can be layered to provide robust caching and
    reliability.

    The Store distinguishes between single entities and collections.
    With single entities, an entity is passed to the store and the
    store is asked to :py:meth:`get`, :py:meth:`put` or :py:meth:`delete`
    it. When :py:meth:`get` is used the provided object is updated in
    place in operation that could be described as population. Dispatch
    is based on the class of the provided entity.

    After any of those operations optional ``HOOKS`` are called.

    With collections there are specific ``list`` methods:

    * :py:meth:`list_bags`
    * :py:meth:`list_recipes`
    * :py:meth:`list_bag_tiddlers`
    * :py:meth:`list_tiddler_revisions`
    * :py:meth:`list_users`

    Finally a store may optionally provide a :py:meth:`search`. How
    search works and what it even means is up to the implementation.
    """

    def __init__(self, engine, config=None, environ=None):
        if config is None:
            config = {}
        self.engine = engine
        self.environ = environ
        self.storage = None
        self.config = config
        self._import()

    def _import(self):
        """
        Import the required :py:class:`tiddlyweb.stores.StorageInterface`.
        """
        try:
            imported_module = __import__('tiddlyweb.stores.%s' % self.engine,
                    {}, {}, ['Store'])
        except ImportError as err:
            err1 = err
            try:
                imported_module = __import__(self.engine, {}, {}, ['Store'])
            except ImportError as err:
                raise ImportError("couldn't load store for %s: %s, %s"
                        % (self.engine, err, err1))
        self.storage = imported_module.Store(self.config, self.environ)

    def delete(self, thing):
        """
        Delete a thing: recipe, bag, tiddler or user.
        """
        func = self._figure_function('delete', thing)
        result = func(thing)
        self._do_hook('delete', thing)
        return result

    def get(self, thing):
        """
        Get a thing: recipe, bag, tiddler or user.
        """
        lower_class = superclass_name(thing)
        if lower_class == 'tiddler':
            retriever = get_bag_retriever(self.environ, thing.bag)
            if retriever:
                try:
                    thing = retriever[1](thing)
                except SpecialBagError as exc:
                    raise NoTiddlerError(
                            'unable to get special tiddler: %s:%s:%s'
                            % (thing.bag, thing.title, exc))
                thing.store = self
                self._do_hook('get', thing)
                return thing
        elif lower_class == 'bag':
            if get_bag_retriever(self.environ, thing.name):
                policy = Policy(read=[], write=['NONE'], create=['NONE'],
                        delete=['NONE'], manage=['NONE'], accept=['NONE'])
                thing.policy = policy
                thing.store = self
                self._do_hook('get', thing)
                return thing
        func = self._figure_function('get', thing)
        thing = func(thing)
        thing.store = self
        self._do_hook('get', thing)
        return thing

    def put(self, thing):
        """
        Put a thing, recipe, bag, tiddler or user.
        """
        func = self._figure_function('put', thing)
        result = func(thing)
        self._do_hook('put', thing)
        return result

    def _figure_function(self, activity, storable):
        """
        Determine which function on the StorageInterface
        we should use to store or retrieve storable.
        """
        lower_class = superclass_name(storable)
        try:
            func = getattr(self.storage, '%s_%s' % (lower_class, activity))
        except AttributeError as exc:
            raise AttributeError('unable to figure function for %s: %s'
                    % (lower_class, exc))
        return func

    def list_bags(self):
        """
        List all the available bags in the system.
        """
        list_func = getattr(self.storage, 'list_bags')
        return list_func()

    def list_bag_tiddlers(self, bag):
        """
        List all the tiddlers in the bag.
        """
        retriever = get_bag_retriever(self.environ, bag.name)
        if retriever:
            try:
                return retriever[0](bag.name)
            except SpecialBagError as exc:
                raise NoBagError('unable to get special bag: %s: %s'
                        % (bag.name, exc))
        list_func = getattr(self.storage, 'list_bag_tiddlers')
        return list_func(bag)

    def list_recipes(self):
        """
        List all the available recipes in the system.
        """
        list_func = getattr(self.storage, 'list_recipes')
        return list_func()

    def list_tiddler_revisions(self, tiddler):
        """
        List the revision ids of the revisions of the indicated tiddler
        in reverse chronological older (newest first).
        """
        list_func = getattr(self.storage, 'list_tiddler_revisions')
        return list_func(tiddler)

    def list_users(self):
        """
        List all the available users in the system.
        """
        list_func = getattr(self.storage, 'list_users')
        return list_func()

    def search(self, search_query):
        """
        Search in the store, using a search algorithm
        specific to the :py:class:`tiddlyweb.stores.StorageInterface`
        implementation.
        """
        list_func = getattr(self.storage, 'search')
        return list_func(search_query)

    def _do_hook(self, method, thing):
        """
        Call the hook in HOOKS identified by method on thing.
        """
        hooked_class = superclass_name(thing)
        hooks = _get_hooks(method, hooked_class)
        for hook in hooks:
            hook(self, thing)


def get_entity(entity, store):
    """
    Load the provided entity from the store if it has not already
    been loaded. If it can't be found, still return the same entity,
    just keep it empty.

    This works for tiddlers, bags and recipes. Not users!
    """
    if store and not entity.store:
        try:
            try:
                stored_entity = entity.__class__(entity.title, entity.bag)
                if entity.revision:
                    stored_entity.revision = entity.revision
            except AttributeError:
                stored_entity = entity.__class__(entity.name)
            stored_entity = store.get(stored_entity)
        except (AttributeError, StoreError):
            stored_entity = entity
    else:
        stored_entity = entity
    return stored_entity


def _get_hooks(method, name):
    """
    Look in HOOKS for the list of functions to run
    for the class of things named by name when store
    method method is called.
    """
    try:
        return HOOKS[name][method]
    except KeyError:
        return []
