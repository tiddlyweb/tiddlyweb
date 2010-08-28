"""
Turn entities to and fro various representations.

This is the base Class and interface Class used to
transform strings of various forms to model objects
and model objects to strings of various forms.
"""

from tiddlyweb.serializer import NoSerializationError
from tiddlyweb.model.tiddler import string_to_tags_list


class SerializationInterface(object):
    """
    A Serialization is a collection of methods that
    either turn an input string into the object named
    by the method, or turn the object into a string
    form.

    The interface is fairly simple: For the data
    entities that exist in the TiddlyWeb system there
    (optionally) exists <entity>_as and as_<entity> methods
    in each Serialization.

    *_as returns a string form of the entity, perhaps as
    HTML, Text, YAML, Atom, whatever the Serialization does.

    as_* takes a provided entity and string and updates
    the skeletal entity to represent the information
    contained in the string (in the Serialization format).

    There are also three supporting methods, list_tiddlers,
    list_recipes() and list_bags() that provide convenience
    methods for presenting a collection of either in the
    Serialization form. A string is returned.

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
        Serialize a Recipe into this serializer's form.
        """
        raise NoSerializationError

    def as_recipe(self, recipe, input_string):
        """
        Take input_string, which is a serialized recipe
        and turn it into a Recipe (if possible).
        """
        raise NoSerializationError

    def bag_as(self, bag):
        """
        Serialize a Bag into this serializer's form.
        """
        raise NoSerializationError

    def as_bag(self, bag, input_string):
        """
        Take input_string, which is a serialized bag
        and turn it into a Bag (if possible).
        """
        raise NoSerializationError

    def tiddler_as(self, tiddler):
        """
        Serialize a Bag into this serializer's form.
        """
        raise NoSerializationError

    def as_tiddler(self, tiddler, input_string):
        """
        Take input_string, which is a serialized tiddler
        and turn it into a Tiddler (if possible).
        """
        raise NoSerializationError

    def list_tiddlers(self, bag):
        """
        Provided a bag, output the included tiddlers.
        """
        raise NoSerializationError

    def list_recipes(self, recipes):
        """
        Provided a List of RecipeS, make a serialized
        list of those recipes (e.g. a a list of HTML
        links).
        """
        raise NoSerializationError

    def list_bags(self, bags):
        """
        Provided a List of BagS, make a serialized
        list of those bags (e.g. a a list of HTML
        links).
        """
        raise NoSerializationError

    def as_tags(self, string):
        """
        Not called directly, put made public for future
        use. Turn a string into a list of tags.
        """
        return string_to_tags_list(string)

    def tags_as(self, tags):
        """
        Not called directly, put made public for future
        use. Turn a list of tags into a serialized list.
        """
        tag_string_list = []
        for tag in tags:
            if ' ' in tag:
                tag = '[[%s]]' % tag
            tag_string_list.append(tag)
        return u' '.join(tag_string_list)
