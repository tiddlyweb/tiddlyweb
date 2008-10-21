
import sys
sys.path.append('.')
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.serializer import Serializer

from fixtures import recipe_list

recipe = Recipe(name='testrecipe')
recipe.set_recipe(recipe_list)
ser = Serializer('wiki')
ser.object = recipe
print ser.to_string()

