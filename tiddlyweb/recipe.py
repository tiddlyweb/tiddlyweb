
"""
A Recipe is an ordered list that represents 
a program for creating a collection of tiddlers.

Each line in the recipe is the combination of a
bag and a filter string. For this implementation
we have a list of lists.

The resulting list of tiddlers can be used to 
create a Tiddlywiki.
"""

import filter
from bag import Bag

class Recipe(list):

    def __init__(self, name):
        list.__init__(self)
        self.name = name

    def set_recipe(self, recipe_list):
        """
        Set the contents of the list.
        """
        list.__init__(self, recipe_list)

    def get_recipe(self):
        """
        Return the recipe list, as a list.
        """
        return self

    def get_tiddlers(self):
        """
        Return the list of tiddlers that result
        from processing the recipe.

        This list of tiddlers is unique by name with 
        tiddlers later in the recipe taking precedence
        over those earlier in the recipe.

        We use a temporary Bag in which to build our
        tiddlers.
        """
        store_bag = Bag(name='tmpstore')
        for bag, filter_string in self:
            if type(bag) == '':
                bag = Bag(name=bag)
            for tiddler in filter.filter_bag(bag, filter_string):
                store_bag.add_tiddler(tiddler)
        return store_bag.list_tiddlers()

    def determine_bag(self, tiddler):
        """
        Return the bag which this tiddler would be in if we 
        were to save it to the recipe rather than to a default
        bag.

        This is a matter of reversing the recipe list and seeing
        if the tiddler is a part of the bag + filter. If bag+filter
        is true, return that bag.
        """
# duplication here with get_tiddlers, so can probalby do something
# meta somewhere
        for bag, filter_string in reversed(self):
            if type(bag) == '':
                bag = Bag(name=bag)
            tiddlers = filter.filter_bag(bag, filter_string)
            if tiddler in tiddlers:
                return bag

        return None

    
