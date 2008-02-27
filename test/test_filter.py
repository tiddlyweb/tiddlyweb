
"""
Test filtering tiddlers by the filter syntax which is not really
described just yet. Use this as the basis for building the basic
tiddler data store. And the rest of the underneath the web code.
"""

import sys
sys.path.append('.')
from tiddlyweb import filter

from fixtures import tiddlers

def setup_module(module):
    pass

def test_filter_by_name():
    """
    Given a name and a list of
    tiddlers (or rather ducks that can name)
    return those that match the name.
    """

    found_tiddlers = filter.by_name('TiddlerOne', tiddlers)
    assert len(found_tiddlers) == 1, 'one tiddler in returned list'
    assert found_tiddlers[0] == tiddlers[0], 'found tiddler is TiddlerOne'

    found_tiddlers = filter.by_name('TiddlerFive', tiddlers)
    assert len(found_tiddlers) == 0, 'no tiddlers found matching TiddlerFive'

def test_filter_by_tag():
    """
    Given a tag, find the tiddlers that use that tag.
    """

    found_tiddlers = filter.by_tag('tagone', tiddlers)
    assert len(found_tiddlers) == 2, 'two tiddlers in returned list'

    found_tiddlers = filter.by_tag('tagoe', tiddlers)
    assert len(found_tiddlers) == 0, 'zero tiddlers in returned list'

    found_tiddlers = filter.by_tag('tagthree', tiddlers)
    assert len(found_tiddlers) == 1, 'one tiddlers in returned list'

    assert found_tiddlers[0]['name'] == tiddlers[2]['name'], 'the found tiddler is the right one'

def test_negate_fitler_by_name():
    """
    Return those tiddlers which are not of provided name.
    """

    filter_function = filter.negate(filter.by_name)
    found_tiddlers = filter_function('TiddlerOne', tiddlers)
    assert len(found_tiddlers) == 2, 'two tiddlers in returned list, got %s' % len(found_tiddlers)

def test_compose_filters():
    """
    Compose a list of filters and see that they do the right thing.
    """

# this data structure seems suspect, but we can change it later
    ordered_filters = [
            [filter.by_tag, 'tagone'],
            [filter.by_name, 'TiddlerTwo'],
            ]

    found_tiddlers = filter.by_composition(ordered_filters, tiddlers)
    assert len(found_tiddlers) == 3, 'three tiddlers should be found, got %s' % len(found_tiddlers)

def test_compose_with_negate_filters():
    """
    Compose a list of filters and see that they do the right thing.
    """

# this data structure seems suspect, but we can change it later
    ordered_filters = [
            [filter.negate(filter.by_tag), 'tagtwo'],
            [filter.by_name, 'TiddlerTwo'],
            ]

    found_tiddlers = filter.by_composition(ordered_filters, tiddlers)
    assert len(found_tiddlers) == 2, 'three tiddlers should be found, got %s' % len(found_tiddlers)

def test_string_to_composed_filter_positive_tag():

    filter_string = 'TiddlerOne [tag[tagone]]'
    filters = filter.compose_from_string(filter_string)

    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 2, 'two tiddlers should be found, got %s' % len(found_tiddlers)
    assert 'TiddlerOne' in [tiddler['name'] for tiddler in found_tiddlers], 'should get first tiddler'
    assert 'TiddlerThree' in [tiddler['name'] for tiddler in found_tiddlers], 'should get third tiddler'

def test_string_to_composed_filter_negative_name():
    filter_string = '[tag[tagthree]] !TiddlerOne'
    filters = filter.compose_from_string(filter_string)

    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 2, 'two tiddlers should be found, got %s' % len(found_tiddlers)
    assert 'TiddlerThree' in [tiddler['name'] for tiddler in found_tiddlers], 'should get third tiddler'
    assert 'TiddlerTwo' in [tiddler['name'] for tiddler in found_tiddlers], 'should get second tiddler'

def test_string_to_composed_filter_negative_tag():

    filter_string = 'TiddlerOne [!tag[tagthree]]'
    filters = filter.compose_from_string(filter_string)

    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 2, 'two tiddlers should be found, got %s' % len(found_tiddlers)
    assert 'TiddlerOne' in [tiddler['name'] for tiddler in found_tiddlers], 'should get first tiddler'
    assert 'TiddlerTwo' in [tiddler['name'] for tiddler in found_tiddlers], 'should get third tiddler'

def test_string_composed_filter_with_remove_by_name():
    """
    Test removal of a built list.
    """

    filter_string = 'TiddlerTwo TiddlerOne -TiddlerTwo'

    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 1, 'one tiddler should be found, got %s' % len(found_tiddlers)
    assert found_tiddlers[0]['name'] == 'TiddlerOne', 'the found tiddler should be TiddlerOne, got %s' % found_tiddlers[0]['name']

def test_string_composed_filter_with_remove_by_tag():
    """
    Test complex composed string filter.
    """

    filter_string = '[!tag[mumbly]] [-tag[tagone]]'

    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 1, 'one tiddler should be found, got %s' % len(found_tiddlers)
    assert found_tiddlers[0]['name'] == 'TiddlerTwo', 'the found tiddler should be TiddlerTwo, got %s' % found_tiddlers[0]['name']


