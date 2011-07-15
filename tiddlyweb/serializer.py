"""
Serialize TiddlyWeb entities for the sake of taking input, sending
output, or formatting entities for storage.

This module provides the facade for accessing the possibly many modules
which act as serializations. It is asked by calling code to provide a
serialization for a given MIME type. Plugins may override what MIME
types are handled and by what modules.
"""

from tiddlyweb.util import superclass_name


class TiddlerFormatError(Exception):
    """
    The provided input is insufficient to form a valid Tiddler.
    """
    pass


class BagFormatError(Exception):
    """
    The provided input is insufficient to form a valid Bag.
    """
    pass


class RecipeFormatError(Exception):
    """
    The provided input is insufficient to form a valid Recipe.
    """
    pass


class NoSerializationError(Exception):
    """
    There is a NoSerialization of this type for the entity.
    """
    pass


class Serializer(object):
    """
    You must set serializer.object after initialization.
    """

    def __init__(self, engine, environ=None):
        if environ is None:
            environ = {}
        self.engine = engine
        self.object = None
        self.environ = environ
        self.serialization = None
        self._figure_serialization()

    def _figure_serialization(self):
        """
        Import the required Serialization.
        """
        if self.engine is None:
            raise NoSerializationError
        try:
            imported_module = __import__('tiddlyweb.serializations.%s'
                    % self.engine, {}, {}, ['Serialization'])
        except ImportError, err:
            err1 = err
            try:
                imported_module = __import__(self.engine, {}, {},
                        ['Serialization'])
            except ImportError, err:
                raise ImportError("couldn't load module for %s: %s, %s"
                        % (self.engine, err, err1))
        self.serialization = imported_module.Serialization(self.environ)

    def __str__(self):
        lower_class = superclass_name(self.object)
        try:
            string_func = getattr(self.serialization, '%s_as' % lower_class)
        except AttributeError, exc:
            raise AttributeError(
                    'unable to find to string function for %s: %s'
                    % (lower_class, exc))
        return string_func(self.object)

    def to_string(self):
        """
        Provide a string representation of current TiddlyWeb entity object.
        """
        return self.__str__()

    def from_string(self, input_string):
        """
        Turn the provided input_string into a TiddlyWeb entity object of the
        type of self.object. That is: populate self.object based on
        input_string.
        """
        lower_class = superclass_name(self.object)
        try:
            object_func = getattr(self.serialization, 'as_%s' % lower_class)
        except AttributeError, exc:
            raise AttributeError(
                    'unable to find from string function for %s: %s'
                    % (lower_class, exc))
        return object_func(self.object, input_string)

    def list_recipes(self, recipes):
        """
        Provide a string representation of the provided recipes
        in the current serialization.
        """
        return self.serialization.list_recipes(recipes)

    def list_bags(self, bags):
        """
        Provide a string representation of the provided bags
        in the current serialization.
        """
        return self.serialization.list_bags(bags)

    def list_tiddlers(self, tiddlers):
        """
        Provide a string representation of the tiddlers in the
        provided Tiddlers collection.
        """
        return self.serialization.list_tiddlers(tiddlers)
