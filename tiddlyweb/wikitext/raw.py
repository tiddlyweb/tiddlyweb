"""
A default simple wikitext renderer which does not render the wikitext
but instead wraps it in ``pre`` tags.
"""
from tiddlyweb.web.util import html_encode


def render(tiddler, environ):
    """
    Wrap HTML encoded wikitext with ``pre`` tags.
    """
    return '<pre>\n' + html_encode(tiddler.text) + '</pre>\n'
