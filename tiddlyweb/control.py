"""
Routines that integrate the basic object classes.

Things like loading up all the tiddlers in a recipe,
listing tiddlers in a bag, and filtering tiddlers.

These are kept in here to avoid a having store
and serialize objects in filters and recipes and the
like.
"""

from tiddlyweb.model.bag import Bag
from tiddlyweb.filters import parse_for_filters, recursive_filter
from tiddlyweb.serializer import TiddlerFormatError
from tiddlyweb.store import NoBagError


def get_tiddlers_from_recipe(recipe, environ=None):
    """
    Return the list of tiddlers that result
    from processing the recipe.

    This list of tiddlers is unique by title with
    tiddlers later in the recipe taking precedence
    over those earlier in the recipe.
    """

    template = recipe_template(environ)
    store = recipe.store
    uniquifier = {}
    for bag, filter_string in recipe.get_recipe(template):
        if isinstance(bag, basestring):
            bag = Bag(name=bag)
        if store:
            bag = store.get(bag)
        for tiddler in filter_tiddlers_from_bag(bag, filter_string, environ=environ):
            uniquifier[tiddler.title] = tiddler
    return uniquifier.values()


def determine_bag_from_recipe(recipe, tiddler, environ=None):
    """
    We have a recipe and a tiddler. We need to
    know the bag in which this tiddler can be found.
    This is different from determine_bag_for_tiddler().
    That one finds the bag the tiddler _could_ be in.
    This is the bag the tiddler _is_ in.

    We reverse the recipe_list, and filter each bag
    according to the rule. Then we look in the list of
    tiddlers and see if ours is in there.
    """
    store = recipe.store
    template = recipe_template(environ)
    for bag, filter_string in reversed(recipe.get_recipe(template)):
        if isinstance(bag, basestring):
            bag = Bag(name=bag)
        if store:
            bag = store.get(bag)
        for candidate_tiddler in filter_tiddlers_from_bag(bag,
                filter_string, environ=environ):
            if tiddler.title == candidate_tiddler.title:
                return bag

    raise NoBagError('no suitable bag for %s' % tiddler.title)


def determine_bag_for_tiddler(recipe, tiddler, environ=None):
    """
    Return the bag which this tiddler would be in if we
    were to save it to the recipe rather than to a default
    bag.

    This is a matter of reversing the recipe list and seeing
    if the tiddler is a part of the bag + filter. If bag+filter
    is true, return that bag.
    """
    template = recipe_template(environ)
    for bag, filter_string in reversed(recipe.get_recipe(template)):
        # ignore the bag and make a new bag
        for candidate_tiddler in filter_tiddlers([tiddler], filter_string, environ=environ):
            if tiddler.title == candidate_tiddler.title:
                if isinstance(bag, basestring):
                    bag = Bag(name=bag)
                return bag

    raise NoBagError('no suitable bag for %s' % tiddler.title)


def get_tiddlers_from_bag(bag):
    """
    Return the list of tiddlers that are in a bag.
    """

    if bag.store:
        for tiddler in bag.store.list_bag_tiddlers(bag):
            if hasattr(tiddler, 'store') and tiddler.store:
                pass
            else:
                try:
                    tiddler = bag.store.get(tiddler)
                except TiddlerFormatError:
                    pass
            yield tiddler
    else:
        for tiddler in bag.tiddlers:
            yield tiddler


def filter_tiddlers(tiddlers, filters, environ=None):
    """
    Return a generator of tiddlers resulting from
    filtering the provided iterator of tiddlers by
    the provided filters.

    If filters is a string, it will be parsed for
    filters.
    """
    if isinstance(filters, basestring):
        filters, _ = parse_for_filters(filters, environ)
    return recursive_filter(filters, tiddlers)


def filter_tiddlers_from_bag(bag, filters, environ=None):
    """
    Return the list of tiddlers resulting from filtering
    bag by filter. The filter is a string that will be
    parsed to a list of filters.
    """
    indexable = bag

    if isinstance(filters, basestring):
        filters, _ = parse_for_filters(filters, environ)
    return recursive_filter(filters, get_tiddlers_from_bag(bag),
            indexable=indexable)


def recipe_template(environ):
    """
    provide a means to specify custom {{ key }} values in recipes
    which are then replaced with the value specified in
    environ['tiddlyweb.recipe_template']
    """
    template = {}
    if environ:
        template = environ.get('tiddlyweb.recipe_template', {})
        try:
            template['user'] = environ['tiddlyweb.usersign']['name']
        except KeyError:
            pass

    return template
