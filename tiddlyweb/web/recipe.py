
from tiddlyweb.recipe import Recipe
from tiddlyweb.store import Store, NoRecipeError
from tiddlyweb.serializer import Serializer
from tiddlyweb import control

serializers = {
        'text/x-tiddlywiki': ['wiki', 'text/html'],
        'text/plain': ['text', 'text/plain'],
        }

def list(environ, start_response):
    store = environ['tiddlyweb.store']
    recipes = store.list_recipes()

    start_response("200 OK",
            [('Content-Type', 'text/plain')])

    return [ '%s\n' % recipe.name for recipe in recipes]

# put content negotiation/serializer in the environ via wrapper app
# put store in the environ via wrapper app
# consider decorating or wrapping with a thing that does exception handling
def get(environ, start_response):
    recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
    accept = environ.get('tiddlyweb.accept')
    extension = environ.get('tiddlyweb.extension')
    if extension:
        recipe_name = recipe_name[0 : recipe_name.rfind('.' + extension)]

    recipe = Recipe(recipe_name)

    store = environ['tiddlyweb.store']

    try:
        store.get(recipe)
    except NoRecipeError, e:
        start_response("404 Not Found", [('Content-Type', 'text/plain')])
        output = '%s not found' % recipe.name
        return [output]

    try:
        serialization, mime_type = _recipe_serializer(accept)
        serializer = Serializer(recipe, serialization)
    except KeyError:
        start_response("415 Unsupported", [('Content-Type', 'text/plain')])
        output = '%s type unsupported' % accept
        return [output]

    # setting the cookie for text/plain is harmless
    start_response("200 OK",
            [('Content-Type', mime_type),
             ('Set-Cookie', 'chkHttpReadOnly=false')])
    return [serializer.to_string()]

def _recipe_serializer(accept):
    return serializers[accept]

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
        start_response("404 Not Found", [('Content-Type', 'text/plain')])
        output = '%s not found' % recipe.name
        return [output]

    start_response("200 OK",
            [('Content-Type', 'text/plain')])

    return [ '%s\n' % tiddler.title for tiddler in control.get_tiddlers_from_recipe(recipe)]

