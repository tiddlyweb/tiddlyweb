
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

def test_filter_by_title():
    """
    Given a title and a list of
    tiddlers (or rather ducks that can title)
    return those that match the title.
    """

    found_tiddlers = filter.by_title('TiddlerOne', tiddlers)
    assert len(found_tiddlers) == 1, 'one tiddler in returned list'
    assert found_tiddlers[0] == tiddlers[0], 'found tiddler is TiddlerOne'

    found_tiddlers = filter.by_title('TiddlerFive', tiddlers)
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

    assert found_tiddlers[0].title == tiddlers[2].title, 'the found tiddler is the right one'

def test_negate_fitler_by_title():
    """
    Return those tiddlers which are not of provided title.
    """

    filter_function = filter.negate(filter.by_title)
    found_tiddlers = filter_function('TiddlerOne', tiddlers)
    assert len(found_tiddlers) == 2, 'two tiddlers in returned list, got %s' % len(found_tiddlers)

def test_sort_filter_by_title():
    """
    Get some tiddlers by a filter, and then sort them.
    """
    filter_function = filter.make_sort()
    found_tiddlers = filter_function('+title', tiddlers)
    assert [tiddler.title for tiddler in found_tiddlers] == ['TiddlerOne', 'TiddlerThree', 'TiddlerTwo']

def test_count_filter():
    """
    Get some tiddlers by a filter, and then sort them.
    """
    filter_function = filter.make_count()
    found_tiddlers = filter_function('2', tiddlers)
    assert [tiddler.title for tiddler in found_tiddlers] == ['TiddlerOne', 'TiddlerTwo']

def test_compose_filters():
    """
    Compose a list of filters and see that they do the right thing.
    """

# this data structure seems suspect, but we can change it later
    ordered_filters = [
            [filter.by_tag, 'tagone'],
            [filter.by_title, 'TiddlerTwo'],
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
            [filter.by_title, 'TiddlerTwo'],
            ]

    found_tiddlers = filter.by_composition(ordered_filters, tiddlers)
    assert len(found_tiddlers) == 2, 'three tiddlers should be found, got %s' % len(found_tiddlers)

def test_empty_composed_filters():

    filter_string = ''
    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, tiddlers)

    assert found_tiddlers == tiddlers, 'empty filter returns all tiddlers'

def test_string_to_composed_filter_positive_tag():

    filter_string = 'TiddlerOne [tag[tagone]]'
    filters = filter.compose_from_string(filter_string)

    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 2, 'two tiddlers should be found, got %s' % len(found_tiddlers)
    assert 'TiddlerOne' in [tiddler.title for tiddler in found_tiddlers], 'should get first tiddler'
    assert 'TiddlerThree' in [tiddler.title for tiddler in found_tiddlers], 'should get third tiddler'

def test_string_to_composed_filter_negative_title():
    filter_string = '[tag[tagthree]] !TiddlerOne'
    filters = filter.compose_from_string(filter_string)

    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 2, 'two tiddlers should be found, got %s' % len(found_tiddlers)
    assert 'TiddlerThree' in [tiddler.title for tiddler in found_tiddlers], 'should get third tiddler'
    assert 'TiddlerTwo' in [tiddler.title for tiddler in found_tiddlers], 'should get second tiddler'

def test_string_to_composed_filter_negative_tag():

    filter_string = 'TiddlerOne [!tag[tagthree]]'
    filters = filter.compose_from_string(filter_string)

    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 2, 'two tiddlers should be found, got %s' % len(found_tiddlers)
    assert 'TiddlerOne' in [tiddler.title for tiddler in found_tiddlers], 'should get first tiddler'
    assert 'TiddlerTwo' in [tiddler.title for tiddler in found_tiddlers], 'should get third tiddler'

def test_string_composed_filter_with_remove_by_title():
    """
    Test removal of a built list.
    """

    filter_string = 'TiddlerTwo TiddlerOne -TiddlerTwo'

    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 1, 'one tiddler should be found, got %s' % len(found_tiddlers)
    assert found_tiddlers[0].title == 'TiddlerOne', 'the found tiddler should be TiddlerOne, got %s' % found_tiddlers[0].title

def test_string_composed_filter_with_remove_by_tag():
    """
    Test complex composed string filter.
    """

    filter_string = '[!tag[mumbly]] [-tag[tagone]]'

    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 1, 'one tiddler should be found, got %s' % len(found_tiddlers)
    assert found_tiddlers[0].title == 'TiddlerTwo', 'the found tiddler should be TiddlerTwo, got %s' % found_tiddlers[0].title

def test_string_composed_filter_with_sort():
    """
    Test sort composed string filter.
    """

    filter_string = '[sort[-title]]'

    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert [tiddler.title for tiddler in found_tiddlers] == ['TiddlerTwo', 'TiddlerThree', 'TiddlerOne']

def test_string_composed_filter_with_count():
    """
    Test count composed string filter.
    """

    filter_string = '[sort[-title]] [count[2]]'

    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert [tiddler.title for tiddler in found_tiddlers] == ['TiddlerTwo', 'TiddlerThree']
