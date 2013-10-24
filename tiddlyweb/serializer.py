"""
Serialize TiddlyWeb entities for the sake of taking input and sending
output.

This module provides the facade for accessing the possibly many modules
which act as serializations. It is asked by calling code to provide a
serialization for a given MIME type. Plugins may override what MIME
types are handled and by what modules. See :py:mod:`tiddlyweb.config`
for related configuration settings.
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
    A Serializer is a facade to a Serialization which implements the
    :py:class:`tiddlyweb.serializations.SerializationInterface` to turn a
    TiddlyWeb :py:mod:`entity <tiddlyweb.model>` into a particular
    representation or vice versa.

    A Serializer can also list collections of entities in a particular
    representation.

    A single Serializer is a reusable tool which can serialize more than
    one object. You must set serializer.object after initialization and
    then again for each subsequent object being serialized.

    The following example turns the :py:class:`tiddler
    <tiddlyweb.model.tiddler.Tiddler>` into JSON and vice-versa::

        tiddler = Tiddler('cow', 'bag')
        tiddler.text = 'moo'
        serializer = Serializer('json', environ)
        serializer.object = tiddler
        json_string = serializer.to_string()
        assert '"text": "moo"' in json_string
        new_string = json_string.replace('moo', 'meow')
        serializer.from_string(new_string)
        assert tiddler.text == 'meow'

    Note that :py:meth:`to_string` and :py:meth:`from_string` operate on the
    Serializer which dispatches to a method in the SerializationInterface
    implementation based on the class of the object being serialized.
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
        except ImportError as err:
            err1 = err
            try:
                imported_module = __import__(self.engine, {}, {},
                        ['Serialization'])
            except ImportError as err:
                raise ImportError("couldn't load module for %s: %s, %s"
                        % (self.engine, err, err1))
        self.serialization = imported_module.Serialization(self.environ)

    def __str__(self):
        lower_class = superclass_name(self.object)
        try:
            string_func = getattr(self.serialization, '%s_as' % lower_class)
        except AttributeError as exc:
            raise AttributeError(
                    'unable to find to string function for %s: %s'
                    % (lower_class, exc))
        return string_func(self.object)

    def to_string(self):
        """
        Provide a (usually unicode) string representation of the
        :py:class:`bag <tiddlyweb.model.bag.Bag>`, :py:class:`recipe
        <tiddlyweb.model.recipe.Recipe>` or :py:class:`tiddler
        <tiddlyweb.model.tiddler.Tiddler>` at ``self.object``.
        """
        return self.__str__()

    def from_string(self, input_string):
        """
        Turn the provided ``input_string`` into a TiddlyWeb entity object
        of the type of ``self.object``. That is: populate ``self.object``
        based on ``input_string``.
        """
        lower_class = superclass_name(self.object)
        try:
            object_func = getattr(self.serialization, 'as_%s' % lower_class)
        except AttributeError as exc:
            raise AttributeError(
                    'unable to find from string function for %s: %s'
                    % (lower_class, exc))
        return object_func(self.object, input_string)

    def list_recipes(self, recipes):
        """
        Provide a (usually unicode) string representation of the provided
        :py:class:`recipes <tiddlyweb.model.recipe.Recipe>` in the current
        serialization.
        """
        return self.serialization.list_recipes(recipes)

    def list_bags(self, bags):
        """
        Provide a (usually unicode) string representation of the provided
        :py:class:`bags <tiddlyweb.model.bag.Bag>` in the current
        serialization.
        """
        return self.serialization.list_bags(bags)

    def list_tiddlers(self, tiddlers):
        """
        Provide a (usually unicode) string representation of the
        :py:class:`tiddlers <tiddlyweb.model.tiddler.Tiddler>` in the
        provided :py:class:`Tiddlers collection
        <tiddlyweb.model.collections.Tiddlers>`.
        """
        return self.serialization.list_tiddlers(tiddlers)
