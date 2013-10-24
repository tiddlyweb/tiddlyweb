"""
Methods for accessing :py:class:`Recipe
<tiddlyweb.model.recipe.Recipe>` entities.
"""

from httpexceptor import HTTP400, HTTP409, HTTP415, HTTP404

from tiddlyweb.filters import FilterError
from tiddlyweb.model.collections import Tiddlers
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.policy import create_policy_check
from tiddlyweb.store import (NoRecipeError, NoBagError,
        StoreMethodNotImplemented)
from tiddlyweb.serializer import (Serializer, NoSerializationError,
        RecipeFormatError)
from tiddlyweb.web.sendentity import send_entity
from tiddlyweb.web.sendtiddlers import send_tiddlers
from tiddlyweb.web.listentities import list_entities
from tiddlyweb import control
from tiddlyweb.web import util as web
from tiddlyweb.web.validator import validate_recipe, InvalidBagError


def delete(environ, start_response):
    """
    Handle ``DELETE`` on a single recipe URI.

    Delete a :py:class:`recipe <tiddlyweb.model.recipe.Recipe>`.
    This just removes the recipe, not any associated :py:class:`bags
    <tiddlyweb.model.bag.Bag>` or :py:class:`tiddlers
    <tiddlyweb.model.tiddler.Tiddler>`.
    """
    recipe = _determine_recipe(environ)
    store = environ['tiddlyweb.store']

    recipe.policy.allows(environ['tiddlyweb.usersign'], 'manage')

    try:
        store.delete(recipe)
    except StoreMethodNotImplemented:
        raise HTTP400('Recipe DELETE not supported')

    start_response("204 No Content", [])
    return []


def get(environ, start_response):
    """
    Handle ``GET`` on a single recipe URI.

    Get a representation in some serialization determined by
    :py:mod:`tiddlyweb.web.negotiate` of a :py:class:`recipe
    <tiddlyweb.model.recipe.Recipe>` (just the recipe itself,
    not the tiddlers it can produce).
    """
    recipe = _determine_recipe(environ)
    recipe.policy.allows(environ['tiddlyweb.usersign'], 'read')
    return send_entity(environ, start_response, recipe)


def get_tiddlers(environ, start_response):
    """
    Handle ``GET`` on a tiddlers-within-a-recipe URI.

    Get a list representation of the :py:class:`tiddlers
    <tiddlyweb.model.tiddler.Tiddler>` generated from a :py:class:`recipe
    <tiddlyweb.model.recipe.Recipe>`.

    The information sent is dependent on the serialization chosen
    via :py:mod:`tiddlyweb.web.negotiate`.
    """
    usersign = environ['tiddlyweb.usersign']
    store = environ['tiddlyweb.store']
    filters = environ['tiddlyweb.filters']
    recipe = _determine_recipe(environ)
    title = 'Tiddlers From Recipe %s' % recipe.name
    title = environ['tiddlyweb.query'].get('title', [title])[0]

    # check the recipe can be read
    recipe.policy.allows(usersign, 'read')

    # check the bags in the recipe can be read
    try:
        template = control.recipe_template(environ)
        for bag_name, _ in recipe.get_recipe(template):
            bag = Bag(bag_name)
            bag = store.get(bag)
            bag.policy.allows(usersign, 'read')
    except NoBagError as exc:
        raise HTTP404('recipe %s lists an unknown bag: %s' %
                (recipe.name, exc))

    # from this point forward we know the tiddlers are
    # readable

    # get the tiddlers from the recipe and uniquify them
    try:
        candidate_tiddlers = control.get_tiddlers_from_recipe(recipe, environ)
    except NoBagError as exc:
        raise HTTP404('recipe %s lists an unknown bag: %s' %
                (recipe.name, exc))
    except FilterError as exc:
        raise HTTP400('malformed filter: %s' % exc)

    tiddlers = Tiddlers(title=title)
    if not filters:
        tiddlers.store = store
    tiddlers.recipe = recipe.name

    for tiddler in candidate_tiddlers:
        tiddler.recipe = recipe.name
        tiddlers.add(tiddler)

    tiddlers.link = '%s/tiddlers' % web.recipe_url(environ, recipe,
            full=False)

    return send_tiddlers(environ, start_response, tiddlers=tiddlers)


def list_recipes(environ, start_response):
    """
    Handle ``GET`` on the recipes URI.

    List all the :py:class:`recipes <tiddlyweb.model.recipe.Recipe>` that are
    readable by the current usersign.

    The information sent is dependent on the serialization chosen
    via :py:mod:`tiddlyweb.web.negotiate`.
    """
    return list_entities(environ, start_response, 'list_recipes')


def put(environ, start_response):
    """
    Handle ``PUT`` on a single recipe URI.

    Put a :py:class:`recipe <tiddlyweb.model.recipe.Recipe>` to the server,
    meaning the description, policy and recipe list of the recipe,
    if :py:class:`policy <tiddlyweb.model.policy.Policy>` allows.
    """
    recipe_name = web.get_route_value(environ, 'recipe_name')
    recipe_name = web.handle_extension(environ, recipe_name)

    recipe = Recipe(recipe_name)
    store = environ['tiddlyweb.store']
    length, _ = web.content_length_and_type(environ)

    usersign = environ['tiddlyweb.usersign']

    try:
        recipe = store.get(recipe)
        recipe.policy.allows(usersign, 'manage')
    except NoRecipeError:
        create_policy_check(environ, 'recipe', usersign)

    try:
        serialize_type = web.get_serialize_type(environ)[0]
    except TypeError:
        raise HTTP400('Content-type header required')

    try:
        serializer = Serializer(serialize_type, environ)
        serializer.object = recipe
        content = web.read_request_body(environ, length)
        serializer.from_string(content.decode('utf-8'))

        recipe.policy.owner = usersign['name']

        _validate_recipe(environ, recipe)
        store.put(recipe)
    except RecipeFormatError as exc:
        raise HTTP400('unable to put recipe: %s' % exc)
    except TypeError as exc:
        raise HTTP400('malformed input: %s' % exc)
    except NoSerializationError:
        raise HTTP415('Content type %s not supported' % serialize_type)

    start_response("204 No Content",
            [('Location', web.recipe_url(environ, recipe))])

    return []


def _validate_recipe(environ, recipe):
    """
    Unless recipe is valid raise a ``409`` with the reason why.
    """
    try:
        validate_recipe(recipe, environ)
    except InvalidBagError as exc:
        raise HTTP409('Recipe content is invalid: %s' % exc)


def _determine_recipe(environ):
    """
    Interpret URL information to determine the target
    recipe and then get it from the store.
    """
    recipe_name = web.get_route_value(environ, 'recipe_name')
    recipe_name = web.handle_extension(environ, recipe_name)
    recipe = Recipe(recipe_name)

    store = environ['tiddlyweb.store']

    try:
        recipe = store.get(recipe)
    except NoRecipeError as exc:
        raise HTTP404('%s not found, %s' % (recipe.name, exc))

    return recipe
