"""
test to ensure that extra template variables in the recipe
are picked up in control._recipe_template
"""
from tiddlyweb.control import _recipe_template

def test_get_template_from_recipe_template():
    environ = {
        'tiddlyweb.recipe_template': {
            'foo': 'bar'
        },
        'tiddlyweb.usersign': {
            'name': 'JohnSmith'
        }
    }
    template = _recipe_template(environ)
    assert template['user'] == 'JohnSmith'
    assert template['foo'] == 'bar'