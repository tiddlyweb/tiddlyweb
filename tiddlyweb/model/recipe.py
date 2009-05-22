"""
The Recipe class.
"""

from tiddlyweb.model.policy import Policy


class Recipe(list):
    """
    A Recipe is an ordered list that represents
    a program for creating a collection of tiddlers.

    Each line in the recipe is the combination of a
    bag and a filter string. For this implementation
    we have a list of lists.

    In common usage a recipe contains only strings
    representing bags and filters, but for the
    sake of easy testing, the bag argument can
    be a Bag.

    A Recipe has a Policy (see tiddlyweb.policy) which may be
    used to control access to the Recipe. These controls are
    optional and are primarily designed for use within the
    web handlers.
    """

    def __init__(self, name, desc=''):
        list.__init__(self)
        self.name = unicode(name)
        self.desc = unicode(desc)
        self.store = None
        self.policy = Policy()

    def set_recipe(self, recipe_list):
        """
        Set the contents of the list.
        """
        list.__init__(self, recipe_list)

    def get_recipe(self, template=None):
        """
        Return the recipe list, as a list.
        """
        if not template:
            template = {}

        our_list = self
        real_list = []

        for bag_name, filter_string in our_list:
            for key, value in template.items():
                bag_name = bag_name.replace('{{ ' + key + ' }}', value)
            real_list.append([bag_name, filter_string])

        return real_list
