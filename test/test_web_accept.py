
"""
Test the content negotiation pieces.

Content negotiation will put something in
the environment that allows us to determine
what kind of store and serializer to use.
"""

import sys
sys.path.append('.')

from tiddlyweb.web.negotiate import Negotiate

def setup_module(module):
    module.neg = Negotiate(lambda x: x)

def test_accept_header():
    """
    Given an accept header in the environ,
    determine the type we want.
    """
    environ = {}
    environ['HTTP_ACCEPT'] = 'text/plain; q=1.0, text/html, text/x-dvi; q=0.8, text/x-c'

    neg.figure_accept(environ)

    assert environ['tiddlyweb.accept'][0] == 'text/plain', \
            'tiddlyweb.accept should be text/plain, found %s' % environ['tiddlyweb.accept'][0]


def test_file_extension():
    """
    Given a \.extension in the path_info,
    determine the type we want.
    """
    environ = {}
    environ['PATH_INFO'] = '/bags/bag0/tiddlers/bigbox.html'
    
    neg.figure_accept(environ)

    assert environ['tiddlyweb.accept'][0] == 'text/html', \
            'tiddlyweb.accept should be text/html, found %s' % environ['tiddlyweb.accept'][0]

def test_accept_query():
    """
    Give an accept query string, determine
    the type we want. Not really sure we want, so pass.
    """
    pass

def test_file_wins_over_header():
    """
    Where there is both an extension and
    an accept header, the extension wins.
    """
    environ = {}
    environ['HTTP_ACCEPT'] = 'text/plain; q=1.0, text/html, text/x-dvi; q=0.8, text/x-c'
    environ['PATH_INFO'] = '/bags/bag0/tiddlers/bigbox.html'

    neg.figure_accept(environ)

    assert environ['tiddlyweb.accept'][0] == 'text/html', \
            'tiddlyweb.accept should be text/html, found %s' % environ['tiddlyweb.accept'][0]

