"""
test to ensure that extra template variables in the recipe
are picked up in control.recipe_template
"""
from tiddlyweb.control import recipe_template

from tiddlyweb.model.recipe import Recipe

environ = {
    'tiddlyweb.recipe_template': {
        'foo': 'bar'
    },
    'tiddlyweb.usersign': {
        'name': 'JohnSmith'
    }
}

def test_get_template_from_recipe_template():
    template = recipe_template(environ)
    assert template['user'] == 'JohnSmith'
    assert template['foo'] == 'bar'

def test_get_recipe():
    recipe = Recipe('templated')
    recipe.set_recipe([
        ('common','select=topic:{{ id:default }}'),
        ('{{ user }}', ''),
        ('system','')
        ])

    stuff = recipe.get_recipe()
    assert stuff[0][1] == 'select=topic:{{ id:default }}'
    assert stuff[1][0] == '{{ user }}'

    filled = recipe.get_recipe(recipe_template(environ))
    assert filled[0][1] == 'select=topic:default'
    assert filled[1][0] == 'JohnSmith'
