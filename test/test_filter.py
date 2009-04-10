
"""
Test filtering tiddlers by the filter syntax which is not really
described just yet. Use this as the basis for building the basic
tiddler data store. And the rest of the underneath the web code.
"""

import sys
sys.path.append('.')

import copy

from tiddlyweb import filter
from tiddlyweb.filter import FilterError
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag

from fixtures import tiddlers

import py.test

# cook up some bagged tiddlers
tiddlers = copy.deepcopy(tiddlers)
for tiddler in tiddlers:
    tiddler.bag = tiddler.title

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

def test_filter_by_since():
    """
    Get the tiddlers modified since <timespec>.
    """
    tiddler_old = Tiddler('old')
    tiddler_old.modified = '19691009000000'
    tiddler_new = Tiddler('new')
    tiddler_new.modified = '20090401030303'
    found_tiddlers = filter.by_since('20010101010100', [tiddler_old, tiddler_new])
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].title == 'new'

    found_tiddlers = filter.by_since('200101010101', [tiddler_old, tiddler_new])
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].title == 'new'


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

def test_filter_by_bag():
    """
    Given a bag, find the tiddlers that are in that bag.
    """

    found_tiddlers = filter.by_bag('TiddlerThree', tiddlers)
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].bag == 'TiddlerThree'
    
    found_tiddlers = filter.by_bag('NoHit', tiddlers)
    assert len(found_tiddlers) == 0

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

def test_sort_filter_by_bogus():
    """
    Attempt to sort by a field that does not exist. Get an error.
    """
    filter_function = filter.make_sort()
    py.test.raises(FilterError, 'filter_function("+monkey", tiddlers)')

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

def test_string_to_composed_filter_positive_bag():
    filter_string = '[bag[TiddlerThree]]'
    filters = filter.compose_from_string(filter_string)

    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].bag == 'TiddlerThree'
    assert found_tiddlers[0].title == 'TiddlerThree'

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

def test_string_to_composed_filter_negative_bag():
    filter_string = '[!bag[TiddlerThree]]'
    filters = filter.compose_from_string(filter_string)

    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 2
    assert 'TiddlerOne' in [tiddler.title for tiddler in found_tiddlers]
    assert 'TiddlerTwo' in [tiddler.title for tiddler in found_tiddlers]

def test_string_to_composed_filter_removal_bag():
    filter_string = 'TiddlerThree TiddlerTwo [-bag[TiddlerThree]]'
    filters = filter.compose_from_string(filter_string)

    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].title == 'TiddlerTwo'

def test_string_composed_filter_with_remove_by_title():
    """
    Test removal of a built list.
    """

    filter_string = 'TiddlerTwo TiddlerOne -TiddlerTwo'

    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 1, 'one tiddler should be found, got %s' % len(found_tiddlers)
    assert found_tiddlers[0].title == 'TiddlerOne', 'the found tiddler should be TiddlerOne, got %s' % found_tiddlers[0].title

def test_string_composed_filter_with_spaces():
    """
    Test spaces in filter.
    """

    tiddlers = []
    for name in ['one', 'two', 'three']:
        tiddler = Tiddler('tiddler %s' % name)
        tiddler.text = name
        tiddlers.append(tiddler)

    filter_string = '[[tiddler one]]'

    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, tiddlers)
    assert len(found_tiddlers) == 1, 'one tiddler should be found, got %s' % len(found_tiddlers)
    assert found_tiddlers[0].title == 'tiddler one'

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

def test_field_composed_filter():
    """
    Add a field to a tiddler and then make sure we can filter for it.
    """

    tiddler1 = Tiddler('one')
    tiddler1.fields = {'status': 'hot'}
    tiddler2 = Tiddler('two')
    tiddler2.fields = {'status': 'cold'}
    tiddler3 = Tiddler('three')

    filter_string = '[status[hot]]'
    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, [tiddler1, tiddler2, tiddler3])
    assert [tiddler.title for tiddler in found_tiddlers] == ['one']

    filter_string = '[!status[hot]]'
    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, [tiddler1, tiddler2, tiddler3])
    assert [tiddler.title for tiddler in found_tiddlers] == ['two', 'three']

    filter_string = '[status[cold]]'
    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, [tiddler1, tiddler2, tiddler3])
    assert [tiddler.title for tiddler in found_tiddlers] == ['two']

    filter_string = '[barnabas[monkey]]'
    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, [tiddler1, tiddler2, tiddler3])
    assert [tiddler.title for tiddler in found_tiddlers] == []

    filter_string = '[!barnabas[monkey]]'
    filters = filter.compose_from_string(filter_string)
    found_tiddlers = filter.by_composition(filters, [tiddler1, tiddler2, tiddler3])
    assert [tiddler.title for tiddler in found_tiddlers] == ['one', 'two', 'three']
