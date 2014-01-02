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
    collection of :py:class:`tiddlers <tiddlyweb.model.tiddler.Tiddler>`.

    Each line in the recipe is the combination of a :py:class:`bag
    <tiddlyweb.model.bag.Bag>` name and a :py:mod:`filter <tiddlyweb.filters>`
    string. This implementation uses list of tuples.

    In common usage a recipe contains only strings representing bags
    and filters, but for the sake of easy testing, the bag argument
    can be a :py:class:`Bag <tiddlyweb.model.bag.Bag>` object.

    A Recipe has a :py:class:`Policy <tiddlyweb.model.policy.Policy>`
    which can be used to control access to the Recipe. These controls are
    optional and are primarily designed for use within the :py:mod:`web
    handlers <tiddlyweb.web.handler>`.
    """

    def __init__(self, name, desc=u''):
        self._recipe = []
        self.name = name
        self.desc = desc
        self.store = None
        self.policy = Policy()

    def set_recipe(self, recipe_list):
        """
        Set the contents of the recipe list.
        """
        self._recipe = recipe_list

    def get_recipe(self, template=None):
        """
        Return the recipe list, as a list of tuple pairs.
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
                        value = re.sub(r'{{ [\w:]+ }}', value, item)
                        new_entry.append(value)
                    else:
                        new_entry.append(item)
                except TypeError:  # item is not a string
                    new_entry.append(item)

            real_list.append(new_entry)

        return real_list
