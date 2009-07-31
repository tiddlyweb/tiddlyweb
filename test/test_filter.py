
"""
Test filtering tiddlers by the filter syntax which is not really
described just yet. Use this as the basis for building the basic
tiddler data store. And the rest of the underneath the web code.
"""


import copy

from tiddlyweb.filters import FilterError, parse_for_filters, recursive_filter
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

    found_tiddlers = list(filter('select=title:TiddlerOne', tiddlers))
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0] == tiddlers[0]


    found_tiddlers = list(filter('select=title:TiddlerFive', tiddlers))
    assert len(found_tiddlers) == 0



def test_filter_by_since():
    """
    Get the tiddlers modified since <timespec>.
    """
    tiddler_old = Tiddler('old')
    tiddler_old.modified = '19691009000000'
    tiddler_new = Tiddler('new')
    tiddler_new.modified = '20090401030303'
    found_tiddlers = list(filter('select=modified:>20010101010100', [tiddler_old, tiddler_new]))
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].title == 'new'

    found_tiddlers = list(filter('select=modified:>200101010101', [tiddler_old, tiddler_new]))
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].title == 'new'

    found_tiddlers = list(filter('select=modified:<200101010101', [tiddler_old, tiddler_new]))
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].title == 'old'


def test_filter_by_tag():
    """
    Given a tag, find the tiddlers that use that tag.
    """

    found_tiddlers = list(filter('select=tag:tagone', tiddlers))
    assert len(found_tiddlers) == 2, 'two tiddlers in returned list'

    found_tiddlers = list(filter('select=tag:tagoe', tiddlers))
    assert len(found_tiddlers) == 0, 'zero tiddlers in returned list'

    found_tiddlers = list(filter('select=tag:tagthree', tiddlers))
    assert len(found_tiddlers) == 1, 'one tiddlers in returned list'

    assert found_tiddlers[0].title == tiddlers[2].title, 'the found tiddler is the right one'

def test_filter_by_bag():
    """
    Given a bag, find the tiddlers that are in that bag.
    """

    found_tiddlers = list(filter('select=bag:TiddlerThree', tiddlers))
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].bag == 'TiddlerThree'
    
    found_tiddlers = list(filter('select=bag:NoHit', tiddlers))
    assert len(found_tiddlers) == 0

def test_negate_fitler_by_title():
    """
    Return those tiddlers which are not of provided title.
    """

    found_tiddlers = list(filter('select=title:!TiddlerOne', tiddlers))
    assert len(found_tiddlers) == 2, 'two tiddlers in returned list, got %s' % len(found_tiddlers)

def test_sort_filter_by_title():
    """
    Get some tiddlers by a filter, and then sort them.
    """
    found_tiddlers = filter('sort=title', tiddlers)
    assert [tiddler.title for tiddler in found_tiddlers] == ['TiddlerOne', 'TiddlerThree', 'TiddlerTwo']

def test_sort_filter_by_bogus():
    """
    Attempt to sort by a field that does not exist. Get an error.
    """
    #py.test.raises(FilterError, 'filter("sort=monkey", tiddlers)')

def test_count_filter():
    """
    Get some tiddlers by a filter, and then sort them.
    """
    found_tiddlers = filter('limit=2', tiddlers)
    assert [tiddler.title for tiddler in found_tiddlers] == ['TiddlerOne', 'TiddlerTwo']

def test_compose_filters():
    """
    Compose a list of filters and see that they do the right thing.
    """

    found_tiddlers = list(filter('select=tag:tagone;select=title:TiddlerThree', tiddlers))
    assert len(found_tiddlers) == 1

def test_compose_with_negate_filters():
    """
    Compose a list of filters and see that they do the right thing.
    """
# this is only one because of the title check
    found_tiddlers = list(filter('select=tag:!tagtwo;select=title:TiddlerTwo', tiddlers))
    assert len(found_tiddlers) == 1

def test_empty_composed_filters():
    found_tiddlers = filter('', tiddlers)
    assert list(found_tiddlers) == tiddlers, 'empty filter returns all tiddlers'

def test_string_to_composed_filter_positive_tag():
    found_tiddlers = list(filter('select=tag:tagone', tiddlers))
    assert len(found_tiddlers) == 2
    assert 'TiddlerOne' in [tiddler.title for tiddler in found_tiddlers]
    assert 'TiddlerThree' in [tiddler.title for tiddler in found_tiddlers]

def test_string_to_composed_filter_positive_bag():
    found_tiddlers = list(filter('select=bag:TiddlerThree', tiddlers))
    assert len(found_tiddlers) == 1
    assert found_tiddlers[0].bag == 'TiddlerThree'
    assert found_tiddlers[0].title == 'TiddlerThree'

def test_string_to_composed_filter_negative_title():
    found_tiddlers = list(filter('select=title:!TiddlerOne', tiddlers))
    assert len(found_tiddlers) == 2
    assert 'TiddlerThree' in [tiddler.title for tiddler in found_tiddlers], 'should get third tiddler'
    assert 'TiddlerTwo' in [tiddler.title for tiddler in found_tiddlers], 'should get second tiddler'

def test_string_to_composed_filter_negative_tag():
    found_tiddlers = list(filter('select=tag:!tagthree', tiddlers))
    assert len(found_tiddlers) == 2, 'two tiddlers should be found, got %s' % len(found_tiddlers)
    assert 'TiddlerOne' in [tiddler.title for tiddler in found_tiddlers], 'should get first tiddler'
    assert 'TiddlerTwo' in [tiddler.title for tiddler in found_tiddlers], 'should get third tiddler'

def test_string_to_composed_filter_negative_bag():
    found_tiddlers = list(filter('select=bag:!TiddlerThree', tiddlers))
    assert len(found_tiddlers) == 2
    assert 'TiddlerOne' in [tiddler.title for tiddler in found_tiddlers]
    assert 'TiddlerTwo' in [tiddler.title for tiddler in found_tiddlers]

def test_string_composed_filter_with_spaces():
    """
    Test spaces in filter.
    """

    tiddlers = []
    for name in ['one', 'two', 'three']:
        tiddler = Tiddler('tiddler %s' % name)
        tiddler.text = name
        tiddlers.append(tiddler)

    found_tiddlers = list(filter('select=title:tiddler one', tiddlers))
    assert len(found_tiddlers) == 1, 'one tiddler should be found, got %s' % len(found_tiddlers)
    assert found_tiddlers[0].title == 'tiddler one'

def test_string_composed_filter_with_sort():
    """
    Test sort composed string filter.
    """

    found_tiddlers = filter('sort=-title', tiddlers)
    assert [tiddler.title for tiddler in found_tiddlers] == ['TiddlerTwo', 'TiddlerThree', 'TiddlerOne']

def test_string_composed_filter_with_count():
    """
    Test count composed string filter.
    """

    found_tiddlers = filter('sort=-title;limit=2', tiddlers)
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

    found_tiddlers = filter('select=status:hot', [tiddler1, tiddler2, tiddler3])
    assert [tiddler.title for tiddler in found_tiddlers] == ['one']

    found_tiddlers = filter('select=status:!hot', [tiddler1, tiddler2, tiddler3])
    assert [tiddler.title for tiddler in found_tiddlers] == ['two', 'three']

    found_tiddlers = filter('select=status:cold', [tiddler1, tiddler2, tiddler3])
    assert [tiddler.title for tiddler in found_tiddlers] == ['two']

    found_tiddlers = filter('select=barnabas:monkey', [tiddler1, tiddler2, tiddler3])
    assert [tiddler.title for tiddler in found_tiddlers] == []

    found_tiddlers = filter('select=barnabas:!monkey', [tiddler1, tiddler2, tiddler3])
    assert [tiddler.title for tiddler in found_tiddlers] == ['one', 'two', 'three']

def filter(filter_string, tiddlers):
    return recursive_filter(parse_for_filters(filter_string)[0], tiddlers)
