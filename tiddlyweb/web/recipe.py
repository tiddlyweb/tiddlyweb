
from tiddlyweb.recipe import Recipe
from tiddlyweb.bag import Bag
from tiddlyweb.store import Store, NoRecipeError
from tiddlyweb.serializer import Serializer
from tiddlyweb.web.http import HTTP415, HTTP404
from tiddlyweb import control
from tiddlyweb import web

serializers = {
        'text/x-tiddlywiki': ['wiki', 'text/html; charset=UTF-8'],
        'text/plain': ['text', 'text/plain; charset=UTF-8'],
        'text/html': ['html', 'text/html; charset=UTF-8'],
        'default': ['html', 'text/html; charset=UTF-8'],
        }

def list(environ, start_response):
    store = environ['tiddlyweb.store']
    recipes = store.list_recipes()

    serialize_type, mime_type = web.get_serialize_type(environ, serializers)
    serializer = Serializer(serialize_type)

    start_response("200 OK",
            [('Content-Type', mime_type)])

    return [ serializer.list_recipes(recipes) ]

# put content negotiation/serializer in the environ via wrapper app
# put store in the environ via wrapper app
# consider decorating or wrapping with a thing that does exception handling
def get(environ, start_response):
    recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
    recipe_name = web.handle_extension(environ, recipe_name)

    recipe = Recipe(recipe_name)

    store = environ['tiddlyweb.store']

    try:
        store.get(recipe)
    except NoRecipeError, e:
        raise HTTP404, '%s not found, %s' % (recipe.name, e)

    serialize_type, mime_type = web.get_serialize_type(environ, serializers)
    serializer = Serializer(serialize_type)
    serializer.object = recipe

    # setting the cookie for text/plain is harmless
    start_response("200 OK",
            [('Content-Type', mime_type),
             ('Set-Cookie', 'chkHttpReadOnly=false')])
    return [serializer.to_string()]

def get_tiddlers(environ, start_response):
    """
    XXX dupe with above. FIXME

    Needs content negotation and linking.
    """
    recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
    recipe = Recipe(recipe_name)

    store = environ['tiddlyweb.store']

    try:
        store.get(recipe)
    except NoRecipeError, e:
        raise HTTP404, '%s not found, %s' % (recipe.name, e)

    tiddlers = control.get_tiddlers_from_recipe(recipe)
    tmp_bag = Bag('tmp_bag', tmpbag=True)
    for tiddler in tiddlers:
        tmp_bag.add_tiddler(tiddler)

    serialize_type, mime_type = web.get_serialize_type(environ, serializers)
    serializer = Serializer(serialize_type)
    serializer.object = tmp_bag

    start_response("200 OK", [('Content-Type', mime_type)])
    return [serializer.to_string()]

