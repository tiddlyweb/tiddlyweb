
"""
Test tiddler, a simple data container for a tiddler.
"""

import datetime

from tiddlyweb.model.tiddler import (Tiddler, current_timestring,
        tags_list_to_string, string_to_tags_list, timestring_to_datetime)

test_tiddler_text = "Race car drivers\ngo really very fast."


def setup_module(module):
    pass


def test_tiddler_create():
    tiddler = Tiddler('hello')

    assert type(tiddler) == Tiddler, ('Tiddler returns a Tiddler, %s, %s'
            % (type(tiddler), Tiddler))
    assert 'hello<tiddlyweb.model.tiddler.Tiddler object' in '%s' % tiddler


def test_tiddler_full_create():
    """
    Confirm we can populate a tiddler at create time.
    """

    tiddler = Tiddler('test tiddler')
    tiddler.modifier = 'test@example.com'
    tiddler.text = test_tiddler_text
    tiddler.tags = ['foo', 'bar']
    tiddler.bag = u'bagone'

    assert type(tiddler) == Tiddler, \
            'Tiddler returns a Tiddler'
    assert tiddler.title == 'test tiddler', \
            'tiddler title should be test tiddler, got %s' \
            % tiddler.title
    assert tiddler.modifier == 'test@example.com', \
            'tiddler modifier should test@example.com, got %s' \
            % tiddler.modifier
    assert tiddler.text == test_tiddler_text, \
            'tiddler content is correct'
    assert tiddler.tags == ['foo', 'bar'], \
            'tiddler tags are correct'
    assert tiddler.bag == 'bagone', \
            'tiddler has a bag of bagone'
    assert tiddler.revision is None, \
            'tiddler revision is None'
    assert tiddler.creator == 'test@example.com'


def test_tiddler_revision_create():
    """
    Confirm that when we set revision in a new Tiddler,
    we are able to retrieve that attribute.
    """

    tiddler = Tiddler('test tiddler r')
    tiddler.text = 'revision test'
    tiddler.revision = 5

    assert type(tiddler) == Tiddler, \
            'Tiddler returns a Tiddler'
    assert tiddler.revision == 5, \
            'revision is set as expected, to 5'


def test_current_timestring():
    """
    Confirm timestring has desired format and is at least in
    the ballpark of now.
    """

    current_time = datetime.datetime.utcnow()
    year = current_time.year
    month = current_time.month
    timestring = current_timestring()

    assert len(timestring) == 14
    assert timestring.startswith('%d%02d' % (year, month))


def test_tags_list_to_string():
    """
    Confirm that tags format as TiddlyWiki likes them.
    """
    tags = ['alpha', 'beta', 'Gamma Fire', 'troll']

    output = tags_list_to_string(tags)

    assert output == 'alpha beta [[Gamma Fire]] troll'

    assert sorted(string_to_tags_list(output)) == sorted(tags)


def test_timestring_to_datetime():
    """
    Confirm a timestring becomes the expected datetime object.
    """
    timestring = '20130711154400'
    date_object = timestring_to_datetime(timestring)

    assert date_object.year == 2013
    assert date_object.month == 7
    assert date_object.day == 11
    assert date_object.hour == 15
    assert date_object.minute == 44
    assert date_object.second == 00
