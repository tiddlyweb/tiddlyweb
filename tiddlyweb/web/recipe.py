
from tiddlyweb.recipe import Recipe
from tiddlyweb.store import Store, NoRecipeError
from tiddlyweb.serializer import Serializer
from tiddlyweb import control

# put content negotiation/serializer in the environ via wrapper app
# put store in the environ via wrapper app
# consider decorating or wrapping with a thing that does exception handling
def get(environ, start_response):
    recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
    recipe = Recipe(recipe_name)

    store = Store('text')

    try:
        store.get(recipe)
    except NoRecipeError, e:
        start_response("404 Not Found", [('Content-Type', 'text/plain')])
        output = '%s not found' % recipe.name
        return [output]

    serializer = Serializer(recipe, 'wiki')
    start_response("200 OK",
            [('Content-Type', 'text/html'),
             ('Set-Cookie', 'chkHttpReadOnly=false')])
    return [serializer.to_string()]

def get_tiddlers(environ, start_response):
    """
    XXX dupe with above. FIXME

    Needs content negotation and linking.
    """
    recipe_name = environ['wsgiorg.routing_args'][1]['recipe_name']
    recipe = Recipe(recipe_name)

    store = Store('text')

    try:
        store.get(recipe)
    except NoRecipeError, e:
        start_response("404 Not Found", [('Content-Type', 'text/plain')])
        output = '%s not found' % recipe.name
        return [output]

    start_response("200 OK",
            [('Content-Type', 'text/plain')])

    return [ '%s\n' % tiddler.title for tiddler in control.get_tiddlers_from_recipe(recipe)]

