"""
Serialize TiddlyWeb things for the sake of storage and the like.
"""

# this should come from some kind of config file

from serializers.text import recipe_as, tiddler_as

from recipe import Recipe
from tiddler import Tiddler

map = {
        Recipe: {
            'text': recipe_as
            },
        Tiddler: {
            'text': tiddler_as
            }
        }

class Serializer():

    def __init__(self, object, format):
        self.object = object
        self.function = self._figure_function(format)

    def __str__(self):
        return self.function(self.object)

    def _figure_function(self, format):
        return map[self.object.__class__][format]

    def to_string(self):
        return self.__str__()
