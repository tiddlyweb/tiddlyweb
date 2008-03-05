"""
Save and retrieve TiddlyWeb things to and from some store.
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

    def save(self, bag_or_recipe, *tiddlers):
        """
        Save a thing. If we have one argument, save a recipe,
        otherwise, save one more tiddlers into a bag.
        """
        if bag_or_recipe and tiddlers:
            return self._save_tiddlers(bag_or_recipe, *tiddlers)
        if bag_or_recipe:
            return self._save_recipe(bag_or_recipe)
        raise TypeError, "save did not recieve good arguments *put more here*"

    def _save_recipe(self, recipe):
        recipe_put_func, recipe_get_func = self._figure_function(self.format, recipe)

        recipe_put_func(recipe)

    def _save_tiddlers(self, bag, *tiddlers):
        if len(tiddlers) == 1 and type(tiddlers[0]) == list:
            tiddlers = tiddlers[0]
        bag_put_func, bag_get_func = self._figure_function(self.format, bag)
        tiddler_put_func, tiddler_get_func = self._figure_function(self.format, tiddlers[0])

        # get the bag in place or rewrite it
        bag_put_func(bag)
        for tiddler in tiddlers:
            tiddler_put_func(bag, tiddler)

    def _figure_function(self, format, object):
        module = 'tiddlyweb.stores.%s' % format
        try:
            imported_module = __import__(module, fromlist=[format])
            put_func = getattr(imported_module, function_map[object.__class__][0])
            get_func = getattr(imported_module, function_map[object.__class__][1])
            return put_func, get_func
        except ImportError, err:
            raise ImportError("couldn't load %s: %s" % (module, err))

