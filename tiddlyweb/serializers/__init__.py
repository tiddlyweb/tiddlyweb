
class SerializationInterface(object):
    """
    A Serialization is a collection of methods that 
    either turn an input string into the object named
    by the method, or turn the object into a string
    form.
    """

    def recipe_as(self, recipe):
        """
        Serialize a Recipe into this serializer's form.
        """
        pass

    def as_recipe(self, recipe, input_string):
        """
        Take input_string, which is a serialized recipe
        and turn it into a Recipe (if possible).
        """
        pass

    def bag_as(self, bag):
        """
        Serialize a Bag into this serializer's form.
        """
        pass

    def as_bag(self, bag, input_string):
        """
        Take input_string, which is a serialized bag
        and turn it into a Bag (if possible).
        """
        pass

    def tiddler_as(self, tiddler):
        """
        Serialize a Bag into this serializer's form.
        """
        pass

    def as_tiddler(self, tiddler, input_string):
        """
        Take input_string, which is a serialized tiddler
        and turn it into a Tiddler (if possible).
        """
        pass

    def list_recipes(self, recipes):
        """
        Provided a List of RecipeS, make a serialized
        list of those recipes (e.g. a a list of HTML
        links).
        """
        pass

    def list_bags(self, bags):
        """
        Provided a List of BagS, make a serialized
        list of those bags (e.g. a a list of HTML
        links).
        """
        pass

    def as_tags(self, string):
        """
        Not called directly, put made public for future
        use. Turn a string into a list of tags.
        """
        pass

    def tags_as(self, tags):
        """
        Not called directly, put made public for future
        use. Turn a list of tags into a serialized list.
        """
        pass
