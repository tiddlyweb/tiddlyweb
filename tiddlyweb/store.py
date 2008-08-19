"""
Put and Get TiddlyWeb things to and from some store.
"""


from tiddler import Tiddler
from bag import Bag
from recipe import Recipe
from user import User

from tiddlyweb.config import config

class StoreMethodNotImplemented(IOError):
    pass

class NoBagError(IOError):
    pass

class NoRecipeError(IOError):
    pass

class NoTiddlerError(IOError):
    pass

class NoUserError(IOError):
    pass

class StoreLockError(IOError):
    pass

class Store(object):

    def __init__(self, format, environ={'tiddlyweb.config': config}):
        self.format = format
        self.environ = environ
        self._import()

    def _import(self):
        try:
            imported_module = __import__('tiddlyweb.stores.%s' % self.format,
                    {}, {}, ['Store'])
        except ImportError, err:
            try:
                imported_module = __import__(self.format, {}, {}, ['Store'])
            except ImportError, err:
                raise ImportError("couldn't load store for %s: %s" % (self.format, err))
        self.storage = imported_module.Store(self.environ)

    def delete(self, thing):
        """
        Delete a know object.
        """
        func = self._figure_function('delete', thing)
        return func(thing)

    def get(self, thing):
        """
        get a thing, recipe, bag or tiddler

        Should there be handling here for things of
        wrong type?
        """
        func = self._figure_function('get', thing)
        thing.store = self
        return func(thing)

    def put(self, thing):
        """
        put a thing, recipe, bag or tiddler.

        Should there be handling here for things of
        wrong type?
        """
        func = self._figure_function('put', thing)
        return func(thing)

    def _figure_function(self, activity, object):
        lower_class = object.__class__.__name__.lower()
        try:
            func = getattr(self.storage, '%s_%s' % (lower_class, activity))
        except AttributeError, e:
            raise AttributeError('unable to figure function for %s: %s' % (lower_class, e))
        return func

    def list_tiddler_revisions(self, tiddler):
        list_func = getattr(self.storage, 'list_tiddler_revisions')
        return list_func(tiddler)

    def list_recipes(self):
        list_func = getattr(self.storage, 'list_recipes')
        return list_func()

    def list_bags(self):
        list_func = getattr(self.storage, 'list_bags')
        return list_func()

    def search(self, search_query):
        list_func = getattr(self.storage, 'search')
        return list_func(search_query)

