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

    def put(self, thing):
        """
        put a thing, recipe, bag or tiddler.

        Should there be handling here for things of
        wrong type?
        """
        put_func, get_func = self._figure_function(self.format, thing)
        return put_func(thing)

    def get(self, thing):
        """
        get a thing, recipe, bag or tiddler

        Should there be handling here for things of
        wrong type?
        """
        put_function , get_func = self._figure_function(self.format, thing)
        thing.store = self
        return get_func(thing)

    def _figure_function(self, format, object):
        module = 'tiddlyweb.stores.%s' % format
        try:
            imported_module = __import__(module, {}, {}, [format])
            put_func = getattr(imported_module, function_map[object.__class__][0])
            get_func = getattr(imported_module, function_map[object.__class__][1])
            return put_func, get_func
        except ImportError, err:
            raise ImportError("couldn't load %s: %s" % (module, err))

    def list_tiddler_revisions(self, tiddler):
        module = 'tiddlyweb.stores.%s' % self.format
        imported_module = __import__(module, {}, {}, [self.format])
        list_func = getattr(imported_module, 'list_tiddler_revisions')

        return list_func(tiddler)

    def list_recipes(self):
        module = 'tiddlyweb.stores.%s' % self.format
        imported_module = __import__(module, {}, {}, [self.format])
        list_func = getattr(imported_module, 'list_recipes')

        return list_func()

    def list_bags(self):
        """
        Dupe with the above, please FIXME.
        """
        module = 'tiddlyweb.stores.%s' % self.format
        imported_module = __import__(module, {}, {}, [self.format])
        list_func = getattr(imported_module, 'list_bags')

        return list_func()

