"""
Access to Recipe objects via the web. List recipes,
GET a recipe, PUT a recipe, GET the tiddlers 
produced by a recipe.
"""
from tiddlyweb.recipe import Recipe
from tiddlyweb.bag import Bag
from tiddlyweb.store import Store, NoRecipeError
from tiddlyweb.serializer import Serializer
from tiddlyweb.web.http import HTTP415, HTTP404
from tiddlyweb import control
from tiddlyweb import web

def get(environ, start_response):
    recipe = _determine_recipe(environ)

    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)
    serializer.object = recipe

    # setting the cookie for text/plain is harmless
    start_response("200 OK",
            [('Content-Type', mime_type),
             ('Set-Cookie', 'chkHttpReadOnly=false')])
    return [serializer.to_string()]

def get_tiddlers(environ, start_response):
    """
    XXX needs support for filtering
    """
    recipe = _determine_recipe(environ)

    tiddlers = control.get_tiddlers_from_recipe(recipe)
    tmp_bag = Bag('tmp_bag', tmpbag=True)
    for tiddler in tiddlers:
        tmp_bag.add_tiddler(tiddler)

    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)
    serializer.object = tmp_bag

    start_response("200 OK", [('Content-Type', mime_type)])
    return [serializer.to_string()]


def list(environ, start_response):
    store = environ['tiddlyweb.store']
    recipes = store.list_recipes()

    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)

    start_response("200 OK",
            [('Content-Type', mime_type)])

    return [ serializer.list_recipes(recipes) ]

def put(environ, start_response):
    recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
    recipe_name = web.handle_extension(environ, recipe_name)

    recipe = Recipe(recipe_name)
    store = environ['tiddlyweb.store']
    length = environ['CONTENT_LENGTH']

    content_type = environ['tiddlyweb.type']

    if content_type != 'application/json':
        raise HTTP415, '%s not supported yet' % content_type

    content = environ['wsgi.input'].read(int(length))
    serialize_type, mime_type = web.get_serialize_type(environ)
    serializer = Serializer(serialize_type)
    serializer.object = recipe
    serializer.from_string(content.decode('UTF-8'))

    store.put(recipe)

    start_response("204 No Content",
            [('Location', web.recipe_url(environ, recipe))])

    return []

def _determine_recipe(environ):
    recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
    recipe_name = web.handle_extension(environ, recipe_name)
    recipe = Recipe(recipe_name)

    store = environ['tiddlyweb.store']

    try:
        store.get(recipe)
    except NoRecipeError, e:
        raise HTTP404, '%s not found, %s' % (recipe.name, e)

    return recipe

