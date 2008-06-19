"""
Put and Get TiddlyWeb things to and from some store.
"""


from tiddler import Tiddler
from bag import Bag
from recipe import Recipe
from user import User

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

    def __init__(self, format):
        self.format = format
        self._import()

    def _import(self):
        try:
            imported_module = __import__('tiddlyweb.stores.%s' % self.format,
                    {}, {}, ['Store'])
        except ImportError, err:
            imported_module = __import__(self.format, {}, {}, ['Store'])
        except ImportError, err:
            raise ImportError("couldn't load %s: %s" % (module, err))
        self.storage = imported_module.Store()

    def put(self, thing):
        """
        put a thing, recipe, bag or tiddler.

        Should there be handling here for things of
        wrong type?
        """
        put_func, get_func = self._figure_function(thing)
        return put_func(thing)

    def get(self, thing):
        """
        get a thing, recipe, bag or tiddler

        Should there be handling here for things of
        wrong type?
        """
        put_function , get_func = self._figure_function(thing)
        thing.store = self
        return get_func(thing)

    def _figure_function(self, object):
        lower_class = object.__class__.__name__.lower()
        try:
            put_func = getattr(self.storage, '%s_put' % lower_class)
            get_func = getattr(self.storage, '%s_get' % lower_class)
        except AttributeError, e:
            raise AttributeError('unable to figure functions for %s: %s' % (lower_class, e))
        return put_func, get_func

    def list_tiddler_revisions(self, tiddler):
        list_func = getattr(self.storage, 'list_tiddler_revisions')
        return list_func(tiddler)

    def list_recipes(self):
        list_func = getattr(self.storage, 'list_recipes')
        return list_func()

    def list_bags(self):
        list_func = getattr(self.storage, 'list_bags')
        return list_func()
