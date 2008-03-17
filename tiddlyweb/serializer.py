"""
Serialize TiddlyWeb things for the sake of storage and the like.
"""


from recipe import Recipe
from tiddler import Tiddler
from bag import Bag

class TiddlerFormatError(Exception):
    pass

function_map = {
        Recipe: ['recipe_as', 'as_recipe', None],
        Tiddler: ['tiddler_as', 'as_tiddler', lambda x: x.strip('[]')],
        Bag: ['bag_as', 'as_bag', lambda x: x.title]
        }

class Serializer():
    """
    You must set object after initialization.
    You may set sortkey after initialization.
    """

    def __init__(self, format):
        self.format = format
        self.sortkey = None
        self.object = None

    def _figure_function(self):
        module = 'tiddlyweb.serializers.%s' % self.format
        try:
            imported_module = __import__(module, fromlist=[self.format])
            string_func = getattr(imported_module, function_map[self.object.__class__][0])
            sort_func = function_map[self.object.__class__][2]
            object_func = getattr(imported_module, function_map[self.object.__class__][1])
            print 's: %s, s: %s, o: %s' % (string_func, sort_func, object_func)
            return string_func, sort_func, object_func
        except ImportError, err:
            raise ImportError("couldn't load %s: %s" % (module, err))

    def __str__(self):
        string_func, sort_func, object_func = self._figure_function()
        if not self.sortkey:
            self.sortkey = sort_func
        return string_func(self.object, sortkey=self.sortkey)

    def to_string(self):
        return self.__str__()

    def from_string(self, input_string):
        string_func, sort_func, object_func = self._figure_function()
        return object_func(self.object, input_string)

    def list_recipes(self, recipes):
        module = 'tiddlyweb.serializers.%s' % self.format
        imported_module = __import__(module, fromlist=[self.format])
        list_func = getattr(imported_module, 'list_recipes')

        return list_func(recipes)

