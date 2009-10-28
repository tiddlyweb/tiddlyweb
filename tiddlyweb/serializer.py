"""
Serialize TiddlyWeb things for the sake of storage and the like.
"""


class TiddlerFormatError(Exception):
    """
    The provided input is insufficient to form a valid Tiddler.
    """
    pass


class NoSerializationError(Exception):
    """
    There is a NoSerialization of this type for the entity.
    """
    pass


class Serializer(object):
    """
    You must set object after initialization.
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
        try:
            imported_module = __import__('tiddlyweb.serializations.%s' % self.engine,
                    {}, {}, ['Serialization'])
        except ImportError, err:
            err1 = err
            try:
                imported_module = __import__(self.engine, {}, {}, ['Serialization'])
            except ImportError, err:
                raise ImportError("couldn't load module for %s: %s, %s" % (self.engine, err, err1))
        self.serialization = imported_module.Serialization(self.environ)

    def __str__(self):
        lower_class = self.object.__class__.__name__.lower()
        try:
            string_func = getattr(self.serialization, '%s_as' % lower_class)
        except AttributeError, exc:
            raise AttributeError('unable to find to string function for %s: %s' % (lower_class, exc))
        return string_func(self.object)

    def to_string(self):
        """
        Provide a string representation of current TiddlyWeb entity object.
        """
        return self.__str__()

    def from_string(self, input_string):
        """
        Turn the provided input_string into a TiddlyWeb entity object of the
        type of self.object. That is: populate self.object based on input_string.
        """
        lower_class = self.object.__class__.__name__.lower()
        try:
            object_func = getattr(self.serialization, 'as_%s' % lower_class)
        except AttributeError, exc:
            raise AttributeError('unable to find from string function for %s: %s' % (lower_class, exc))
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

    def list_tiddlers(self, bag):
        """
        Provide a string representation of the tiddlers in the
        provided bag in the current serialization.
        """
        return self.serialization.list_tiddlers(bag)
