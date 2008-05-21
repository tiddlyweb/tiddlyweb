"""
Put and Get TiddlyWeb things to and from some store.
"""


from tiddler import Tiddler
from bag import Bag
from recipe import Recipe

function_map = {
        Recipe: ['recipe_put', 'recipe_get'],
        Tiddler: ['tiddler_put', 'tiddler_get'],
        Bag: ['bag_put', 'bag_get']
        }

class NoBagError(IOError):
    pass

class NoRecipeError(IOError):
    pass

class NoTiddlerError(IOError):
    pass

class StoreLockError(IOError):
    pass

class Store(object):

    def __init__(self, format):
        self.format = format
        self.imported_module = self._import()

    def _import(self):
        module = 'tiddlyweb.stores.%s' % self.format
        try:
            imported_module = __import__(module, {}, {}, [self.format])
        except ImportError, err:
            raise ImportError("couldn't load %s: %s" % (module, err))
        return imported_module

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
        put_func = getattr(self.imported_module, function_map[object.__class__][0])
        get_func = getattr(self.imported_module, function_map[object.__class__][1])
        return put_func, get_func

    def list_tiddler_revisions(self, tiddler):
        list_func = getattr(self.imported_module, 'list_tiddler_revisions')
        return list_func(tiddler)

    def list_recipes(self):
        list_func = getattr(self.imported_module, 'list_recipes')
        return list_func()

    def list_bags(self):
        list_func = getattr(self.imported_module, 'list_bags')
        return list_func()
