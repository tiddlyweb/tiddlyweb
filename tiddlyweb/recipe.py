
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
    """

    def __init__(self, name):
        list.__init__(self)
        self.name = name
        self.store = None

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

