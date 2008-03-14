
"""
Test the content negotiation pieces.

Content negotiation will put something in
the environment that allows us to determine
what kind of store and serializer to use.
"""

import sys
sys.path.append('.')

from tiddlyweb.web import negotiate

def setup_module(module):
    pass

def test_accept_header():
    """
    Given an accept header in the environ,
    determine the type we want.
    """
    environ = {}
    environ['HTTP_ACCEPT'] = 'text/plain; q=1.0, text/html, text/x-dvi; q=0.8, text/x-c'

    negotiate.type(environ, lambda x: x)

    assert environ['tiddlyweb.accept'] == 'text/plain', \
            'tiddlyweb.accept should be text/plain, found %s' % environ['tiddlyweb.accept']


def test_file_extension():
    """
    Given a \.extension in the path_info,
    determine the type we want.
    """
    environ = {}
    environ['PATH_INFO'] = '/bags/bag0/tiddlers/bigbox.html'
    
    negotiate.type(environ, lambda x: x)

    assert environ['tiddlyweb.accept'] == 'text/html', \
            'tiddlyweb.accept should be text/html, found %s' % environ['tiddlyweb.accept']

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

    negotiate.type(environ, lambda x: x)

    assert environ['tiddlyweb.accept'] == 'text/html', \
            'tiddlyweb.accept should be text/html, found %s' % environ['tiddlyweb.accept']



