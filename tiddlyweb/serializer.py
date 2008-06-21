"""
Serialize TiddlyWeb things for the sake of storage and the like.
"""

from recipe import Recipe
from tiddler import Tiddler
from bag import Bag

class TiddlerFormatError(Exception):
    pass

class Serializer(object):
    """
    You must set object after initialization.
    """

    def __init__(self, format, environ={}):
        self.format = format
        self.object = None
        self.environ = environ
        self._figure_serialization()

    def _figure_serialization(self):
        try:
            imported_module = __import__('tiddlyweb.serializations.%s' % self.format,
                    {}, {}, ['Serialization'])
        except ImportError, err:
            try:
                imported_module = __import__(self.format, {}, {}, ['Serialization'])
            except ImportError, err:
                raise ImportError("couldn't load module for %s: %s" % (self.format, err))
        self.serialization = imported_module.Serialization(self.environ)

    def __str__(self):
        lower_class = self.object.__class__.__name__.lower()
        try:
            string_func = getattr(self.serialization, '%s_as' % lower_class)
        except AttributeError, e:
            raise AttributeError('unable to find to string function for %s' % lower_class)
        return string_func(self.object)

    def to_string(self):
        return self.__str__()

    def from_string(self, input_string):
        lower_class = self.object.__class__.__name__.lower()
        try:
            object_func = getattr(self.serialization, 'as_%s' % lower_class)
        except AttributeError, e:
            raise AttributeError('unable to find from string function for %s' % lower_class)
        return object_func(self.object, input_string)

    def list_recipes(self, recipes):
        return self.serialization.list_recipes(recipes)

    def list_bags(self, bags):
        return self.serialization.list_bags(bags)

