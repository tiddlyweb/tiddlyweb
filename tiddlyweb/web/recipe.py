"""
Access to Recipe objects via the web. List recipes,
GET a recipe, PUT a recipe, GET the tiddlers 
produced by a recipe.
"""

import urllib
import cgi

from tiddlyweb.recipe import Recipe
from tiddlyweb.bag import Bag
from tiddlyweb.store import Store, NoRecipeError, NoBagError, StoreMethodNotImplemented
from tiddlyweb.serializer import Serializer, NoSerializationError
from tiddlyweb.web.http import HTTP400, HTTP415, HTTP404, HTTP403
from tiddlyweb.web.tiddlers import send_tiddlers
from tiddlyweb import control
from tiddlyweb.web import util as web

def delete(environ, start_response):
    """
    Delete a recipe, where what delete means
    depends on the store used.

    XXX: There are no permissions on this method.
    There should be!
    """
    recipe = _determine_recipe(environ)

    try:
        recipe.store.delete(recipe)
    except StoreMethodNotImplemented:
        raise HTTP400, 'Recipe DELETE not supported'

    start_response("204 No Content", [])
    return []

def get(environ, start_response):
    recipe = _determine_recipe(environ)

    try:
        serialize_type, mime_type = web.get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)
        serializer.object = recipe
        content = serializer.to_string()
    except NoSerializationError:
        raise HTTP415, 'Content type %s not supported' % mime_type

    # setting the cookie for text/plain is harmless
    start_response("200 OK",
            [('Content-Type', mime_type)])
    return [content]

def get_tiddlers(environ, start_response):
    filter_string = environ['tiddlyweb.query'].get('filter',[''])[0]
    filter_string = urllib.unquote(filter_string)
    filter_string = unicode(filter_string, 'utf-8')
    usersign = environ['tiddlyweb.usersign']
    store = environ['tiddlyweb.store']
    recipe = _determine_recipe(environ)

    # get the tiddlers from the recipe and uniquify them
    try:
        tiddlers = control.get_tiddlers_from_recipe(recipe)
    except NoBagError, e:
        raise HTTP404, 'recipe %s lists an unknown bag: %s' % (recipe.name, e)
    tmp_bag = Bag('tmp_bag1', tmpbag=True)
    for tiddler in tiddlers:
        tmp_bag.add_tiddler(tiddler)

    # then filter those tiddlers
    tiddlers = control.filter_tiddlers_from_bag(tmp_bag, filter_string)
    tmp_bag = Bag('tmp_bag2', tmpbag=True)

    # Make an optimization so we are not going
    # to the database to load the policies of
    # the same bag over and over.
    policies = {}
    for tiddler in tiddlers:
        bag_name = tiddler.bag
        try:
            policies['bag_name'].allows(usersign, 'read')
        except KeyError:
            bag = Bag(tiddler.bag)
            store.get(bag)
            policy = bag.policy
            policies['bag_name'] = policy
            policies['bag_name'].allows(usersign, 'read')

        tiddler.recipe = recipe.name
        tmp_bag.add_tiddler(tiddler)

    return send_tiddlers(environ, start_response, tmp_bag)

def list(environ, start_response):
    store = environ['tiddlyweb.store']
    recipes = store.list_recipes()

    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type, environ)

    start_response("200 OK",
            [('Content-Type', mime_type)])

    return [ serializer.list_recipes(recipes) ]

def put(environ, start_response):
    recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
    recipe_name = urllib.unquote(recipe_name)
    recipe_name = unicode(recipe_name, 'utf-8')
    recipe_name = web.handle_extension(environ, recipe_name)

    recipe = Recipe(recipe_name)
    store = environ['tiddlyweb.store']
    length = environ['CONTENT_LENGTH']

    try:
        serialize_type, mime_type = web.get_serialize_type(environ)
        serializer = Serializer(serialize_type, environ)
        serializer.object = recipe
        content = environ['wsgi.input'].read(int(length))
        serializer.from_string(content.decode('UTF-8'))

        store.put(recipe)
    except NoSerializationError:
        raise HTTP415, 'Content type %s not supported' % serialize_type

    start_response("204 No Content",
            [('Location', web.recipe_url(environ, recipe))])

    return []

def _determine_recipe(environ):
    recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
    recipe_name = urllib.unquote(recipe_name)
    recipe_name = unicode(recipe_name, 'utf-8')
    recipe_name = web.handle_extension(environ, recipe_name)
    recipe = Recipe(recipe_name)

    store = environ['tiddlyweb.store']

    try:
        store.get(recipe)
    except NoRecipeError, e:
        raise HTTP404, '%s not found, %s' % (recipe.name, e)

    return recipe

