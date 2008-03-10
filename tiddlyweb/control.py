"""
Routines that integrate the basic object classes.

Things like loading up all the tiddlers in a recipe.
"""

from tiddlyweb.bag import Bag
from tiddlyweb import filter


def get_tiddlers_from_recipe(recipe, store=None):
    """
    Return the list of tiddlers that result
    from processing the recipe.

    This list of tiddlers is unique by title with 
    tiddlers later in the recipe taking precedence
    over those earlier in the recipe.
    """
    uniquifier = {}
    for bag, filter_string in recipe:
        if type(bag) == str:
            bag = Bag(name=bag)
        if store:
            store.get(bag)
        for tiddler in filter.filter_bag(bag, filter_string):
            if store:
                store.get(tiddler)
            uniquifier[tiddler.title] = tiddler
    return uniquifier.values()


