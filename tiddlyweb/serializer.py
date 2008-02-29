"""
Serialize TiddlyWeb things for the sake of storage and the like.
"""


from recipe import Recipe
from tiddler import Tiddler

function_map = {
        Recipe: 'recipe_as',
        Tiddler: 'tiddler_as'
        }

class Serializer():

    def __init__(self, object, format):
        self.object = object
        self.function = self._figure_function(format)

    def __str__(self):
        return self.function(self.object)

    def _figure_function(self, format):
        module = 'tiddlyweb.serializers.%s' % format
        try:
            imported_module = __import__(module, fromlist=['format'])
            return getattr(imported_module, function_map[self.object.__class__])
        except ImportError, err:
            raise ImportError("couldn't load %s: %s" % (module, err))

    def to_string(self):
        return self.__str__()
