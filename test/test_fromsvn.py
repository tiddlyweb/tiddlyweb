"""
Test retrieving content from the TiddlyWiki Subversion repository.
"""


from tiddlyweb.fromsvn import _strip_extension


def test_strip_extension():

    doc = """returns name without trailing extension"""
    actual = _strip_extension('foo.bar', '.bar')
    expected = 'foo'
    assert actual == expected, doc

    doc = """strips trailing extension only once"""
    actual = _strip_extension('foo.bar.bar', '.bar')
    expected = 'foo.bar'
    assert actual == expected, doc

    doc = """returns original name if extension does not appear at the end"""
    actual = _strip_extension('foo.bar.baz', '.bar')
    expected = 'foo.bar.baz'
    assert actual == expected, doc

    doc = """returns original name if extension is empty"""
    actual = _strip_extension('foo.bar', '')
    expected = 'foo.bar'
    assert actual == expected, doc

    doc = """raises TypeError for None extension"""
    try:
       _strip_extension('foo.bar', None)
       assert False, doc
    except TypeError:
        assert True, doc
