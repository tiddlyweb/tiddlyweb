
from tiddlyweb.recipe import Recipe
from tiddlyweb.store import Store, NoRecipeError
from tiddlyweb.serializer import Serializer

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
    start_response("200 OK", [('Content-Type', 'text/html')])
    return [serializer.to_string()]

def get_tiddlers(environs, start_repsonse):
    pass
