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

class Store():

    def __init__(self, format):
        self.format = format

    def put(self, *things):
        """
        put a thing, recipe or one or more tiddlers.

        Should there be handling here for things of
        wrong type?
        """
        if type(things) == Recipe:
            return self._put_recipe(things)
        if type(things) == Bag:
            return self._put_bag(things)
        return self._put_tiddlers(*things)

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

