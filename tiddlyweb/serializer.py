"""
Serialize TiddlyWeb things for the sake of storage and the like.
"""


from recipe import Recipe
from tiddler import Tiddler
from bag import Bag

class TiddlerFormatError(Exception):
    pass

function_map = {
        Recipe: ['recipe_as', 'as_recipe'],
        Tiddler: ['tiddler_as', 'as_tiddler'],
        Bag: ['bag_as', 'as_bag']
        }

class Serializer(object):
    """
    You must set object after initialization.
    """

    def __init__(self, format):
        self.format = format
        self.object = None
        self._figure_serialization()

    def _figure_serialization(self):
        module = 'tiddlyweb.serializations.%s' % self.format
        try:
            imported_module = __import__(module, {}, {}, ['Serialization'])
            self.serialization = imported_module.Serialization()
        except ImportError, err:
            raise ImportError("couldn't load %s: %s" % (module, err))

    def __str__(self):
        string_func = getattr(self.serialization, function_map[self.object.__class__][0])
        return string_func(self.object)

    def to_string(self):
        return self.__str__()

    def from_string(self, input_string):
        object_func = getattr(self.serialization, function_map[self.object.__class__][1])
        return object_func(self.object, input_string)

    def list_recipes(self, recipes):
        return self.serialization.list_recipes(recipes)

    def list_bags(self, bags):
        return self.serialization.list_bags(bags)

