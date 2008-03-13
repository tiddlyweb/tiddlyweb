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

    def __init__(self, object, format, sortkey=None):
        self.object = object
        list_func, object_func, sort_func = self._figure_function(format)
        if sortkey:
            sort_func = sortkey
        self.serial_function = list_func
        self.object_function = object_func
        self.sortkey = sort_func

    def __str__(self):
        return self.serial_function(self.object, sortkey=self.sortkey)

    def _figure_function(self, format):
        module = 'tiddlyweb.serializers.%s' % format
        try:
            imported_module = __import__(module, fromlist=[format])
            list_func = getattr(imported_module, function_map[self.object.__class__][0])
            object_func = getattr(imported_module, function_map[self.object.__class__][1])
            sort_func = function_map[self.object.__class__][2]
            return list_func, object_func, sort_func
        except ImportError, err:
            raise ImportError("couldn't load %s: %s" % (module, err))

    def to_string(self):
        return self.__str__()

    def from_string(self, input_string):
        return self.object_function(self.object, input_string)
