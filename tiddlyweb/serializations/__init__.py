"""
Turn entities to and fro various representations.

This is the base class and interface class used to transform strings
of various forms to model objects and model objects to strings of various
forms.
"""

from tiddlyweb.serializer import NoSerializationError
from tiddlyweb.model.tiddler import tags_list_to_string, string_to_tags_list


class SerializationInterface(object):
    """
    A Serialization is a collection of methods that
    either turn an input string into the object named
    by the method, or turn the object into a string
    form. A Serialization is not called directly, instead
    a :py:class:`Serializer <tiddlyweb.serializer.Serializer>`
    facade is used.

    The interface is fairly simple: For the core
    entities that exist in the TiddlyWeb system (:py:class:`bags
    <tiddlyweb.model.bag.Bag>`, :py:class:`recipes
    <tiddlyweb.model.recipe.Recipe>` and :py:class:`tiddlers
    <tiddlyweb.model.tiddler.Tiddler>` there (optionally) exists
    ``<entity>_as`` and ``as_<entity>`` methods in each Serialization.

    ``*_as`` returns a string form of the entity, perhaps as
    HTML, Text, YAML, Atom, whatever the Serialization does.

    ``as_*`` takes a provided entity and string and updates
    the skeletal entity to use the information contained in the
    string (in the Serialization format).

    There are also three supporting methods, ``list_tiddlers()``,
    ``list_recipes()`` and ``list_bags()`` that provide convenience
    methods for presenting a collection of entities in the
    Serialization form. A string is returned.

    Strings are usually unicode.

    If a method doesn't exist a NoSerializationError is raised
    and the calling code is expected to do something intelligent
    when trapping it.
    """

    def __init__(self, environ=None):
        if environ is None:
            environ = {}
        self.environ = environ

    def recipe_as(self, recipe):
        """
        Serialize a :py::class:`Recipe <tiddlyweb.model.recipe.Recipe>`
        into this serializer's form.
        """
        raise NoSerializationError

    def as_recipe(self, recipe, input_string):
        """
        Take ``input_string`` which is a serialized recipe and use it
        to populate the :py:class:`Recipe <tiddlyweb.model.recipe.Recipe>`
        in ``recipe`` (if possible).
        """
        raise NoSerializationError

    def bag_as(self, bag):
        """
        Serialize a :py:class:`Bag <tiddlyweb.model.bag.Bag>` into
        this serializer's form.
        """
        raise NoSerializationError

    def as_bag(self, bag, input_string):
        """
        Take ``input_string`` which is a serialized bag and use it
        to populate the :py:class:`Bag <tiddlyweb.model.bag.Bag>` in
        ``bag`` (if possible).
        """
        raise NoSerializationError

    def tiddler_as(self, tiddler):
        """
        Serialize a :py:class:`Tiddler <tiddlyweb.model.tiddler.Tiddler>`
        into this serializer's form.
        """
        raise NoSerializationError

    def as_tiddler(self, tiddler, input_string):
        """
        Take ``input_string`` which is a serialized tiddler and use it
        to populate the :py:class:`Tiddler <tiddlyweb.model.tiddler.Tiddler>`
        in ``tiddler`` (if possible).
        """
        raise NoSerializationError

    def list_tiddlers(self, bag):
        """
        Provided a :py:class:`bag <tiddlyweb.model.bag.Bag>`, output the
        associated :py:class:`tiddlers <tiddlyweb.model.tiddler.Tiddler>`.
        """
        raise NoSerializationError

    def list_recipes(self, recipes):
        """
        Provided a list of :py:class:`recipes
        <tiddlyweb.model.recipe.Recipe>`, make a serialized list of those
        recipes (e.g. a a list of HTML links).
        """
        raise NoSerializationError

    def list_bags(self, bags):
        """
        Provided a list of :py:class:`bags <tiddlyweb.model.bag.Bag>`,
        make a serialized list of those bags (e.g. a a list of HTML
        links).
        """
        raise NoSerializationError

    def as_tags(self, string):
        """
        Not called directly, but made public for future
        use. Turn a string into a list of tags.
        """
        return string_to_tags_list(string)

    def tags_as(self, tags):
        """
        Not called directly, but made public for future
        use. Turn a list of tags into a serialized list.
        """
        return tags_list_to_string(tags)
