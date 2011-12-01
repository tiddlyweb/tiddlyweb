"""
Tests for parts of control.py not otherwise covered by
tests.
"""

import py.test

from tiddlyweb.config import config
from tiddlyweb.store import Store, NoBagError
from tiddlyweb.control import determine_bag_for_tiddler
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler

def test_determine_bag_for_tiddler():
    recipe = Recipe('example')
    recipe.set_recipe([
        ('bagone', ''),
        ('bagtwo', 'select=title:monkey')])

    tiddler = Tiddler('happy')

    bag = determine_bag_for_tiddler(recipe, tiddler)
    assert bag.name == 'bagone'

    tiddler = Tiddler('monkey')
    bag = determine_bag_for_tiddler(recipe, tiddler)
    assert bag.name == 'bagtwo'

    recipe.set_recipe([
        ('bagone', 'select=tag:foo'),
        ('bagtwo', 'select=title:monkeys')])

    py.test.raises(NoBagError, 'determine_bag_for_tiddler(recipe, tiddler)')
