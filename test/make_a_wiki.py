
import sys
sys.path.append('.')
from tiddlyweb.recipe import Recipe
from tiddlyweb.serializer import Serializer

from fixtures import recipe_list

recipe = Recipe(name='testrecipe')
recipe.set_recipe(recipe_list)
print Serializer(recipe, 'wiki').to_string()

