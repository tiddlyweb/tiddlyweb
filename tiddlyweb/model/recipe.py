"""
The Recipe class.
"""

import re

from tiddlyweb.model.policy import Policy

RECIPE_TEMPLATE_RE = re.compile(r'{{ (\w+) }}')
RECIPE_TEMPLATE_DEFAULT_RE = re.compile(r'{{ (\w+):(\w+) }}')


class Recipe(object):
    """
    A Recipe is an ordered list that represents a program for creating a
    collection of tiddlers.

    Each line in the recipe is the combination of a bag and a filter
    string. For this implementation we have a list of tuples.

    In common usage a recipe contains only strings representing bags
    and filters, but for the sake of easy testing, the bag argument
    can be a Bag.

    A Recipe has a Policy (see tiddlyweb.policy) which may be used to
    control access to the Recipe. These controls are optional and are
    primarily designed for use within the web handlers.
    """

    def __init__(self, name, desc=u''):
        self._recipe = []
        self.name = unicode(name)
        self.desc = unicode(desc)
        self.store = None
        self.policy = Policy()

    def set_recipe(self, recipe_list):
        """
        Set the contents of the list.
        """
        self._recipe = recipe_list

    def get_recipe(self, template=None):
        """
        Return the recipe list, as a list.
        """
        our_list = self._recipe
        real_list = []

        # If no template is provided the below
        # will fail over to not doing template
        # processing. Which is what we want.

        for entry in our_list:
            new_entry = []
            for item in entry:
                value = None
                try:
                    match = RECIPE_TEMPLATE_DEFAULT_RE.search(item)
                    if match:
                        keyname = match.group(1)
                        default = match.group(2)
                        try:
                            value = template[keyname]
                        except KeyError:
                            value = default
                    match = RECIPE_TEMPLATE_RE.search(item)
                    if match:
                        keyname = match.group(1)
                        value = template[keyname]
                    if value:
                        value = re.sub('{{ [\w:]+ }}', value, item)
                        new_entry.append(value)
                    else:
                        new_entry.append(item)
                except TypeError:  # item is not a string
                    new_entry.append(item)

            real_list.append(new_entry)

        return real_list
