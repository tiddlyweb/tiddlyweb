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

class NoBagError(Exception):
    pass

class NoRecipeError(Exception):
    pass

class NoTiddlerError(Exception):
    pass

class Store():

    def __init__(self, format):
        self.format = format

    def put(self, *things):
        """
        put a thing, recipe, bag or one or more tiddlers.

        Should there be handling here for things of
        wrong type?

        Look at how simple get() is, can we be more like that?
        """
        if type(things) == Recipe:
            return self._put_recipe(things)
        if type(things) == Bag:
            return self._put_bag(things)
        return self._put_tiddlers(*things)

    def get(self, thing):
        """
        get a thing, recipe, bag or tiddler

        Should there be handling here for things of
        wrong type?
        """
        put_function , get_func = self._figure_function(self.format, thing)
        thing.store = self
        return get_func(thing)

    def _put_recipe(self, recipe):
        recipe_put_func, recipe_get_func = self._figure_function(self.format, recipe)

        recipe_put_func(recipe)

    def _put_bag(self, bag):
        bag_put_func, bag_get_func = self._figure_function(self.format, bag)

        bag_put_func(bag)

    def _put_tiddlers(self, *tiddlers):
        if len(tiddlers) == 1 and type(tiddlers[0]) == list:
            tiddlers = tiddlers[0]
        tiddler_put_func, tiddler_get_func = self._figure_function(self.format, tiddlers[0])

        for tiddler in tiddlers:
            tiddler_put_func(tiddler)

    def _figure_function(self, format, object):
        module = 'tiddlyweb.stores.%s' % format
        try:
            imported_module = __import__(module, fromlist=[format])
            put_func = getattr(imported_module, function_map[object.__class__][0])
            get_func = getattr(imported_module, function_map[object.__class__][1])
            return put_func, get_func
        except ImportError, err:
            raise ImportError("couldn't load %s: %s" % (module, err))

    def list_recipes(self):
        module = 'tiddlyweb.stores.%s' % self.format
        imported_module = __import__(module, fromlist=[self.format])
        list_func = getattr(imported_module, 'list_recipes')

        return list_func()

    def list_bags(self):
        """
        Dupe with the above, please FIXME.
        """
        module = 'tiddlyweb.stores.%s' % self.format
        imported_module = __import__(module, fromlist=[self.format])
        list_func = getattr(imported_module, 'list_bags')

        return list_func()

