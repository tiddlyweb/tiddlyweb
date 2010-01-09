
"""
Test the content negotiation pieces.

Content negotiation will put something in
the environment that allows us to determine
what kind of store and serializer to use.
"""


from tiddlyweb.web.negotiate import Negotiate
from tiddlyweb.config import config

def setup_module(module):
    module.neg = Negotiate(lambda x: x)
    module.environ = {'tiddlyweb.config': config}
    environ['REQUEST_METHOD'] = 'GET'

def test_accept_header():
    """
    Given an accept header in the environ,
    determine the type we want.
    """
    environ['HTTP_ACCEPT'] = 'text/plain; q=1.0, text/html, text/x-dvi; q=0.8, text/x-c'

    neg.figure_type(environ)

    assert environ['tiddlyweb.type'][0] == 'text/plain', \
            'tiddlyweb.type should be text/plain, found %s' % environ['tiddlyweb.type'][0]

def test_accept_ill_formed_header():
    """
    Given an accept header in the environ,
    that is poorly formed, properly skip over a bad entry.
    """
    environ['HTTP_ACCEPT'] = '; q=1.0, text/plain; q=1.0, text/html, text/x-dvi; q=0.8, text/x-c'

    neg.figure_type(environ)

    assert environ['tiddlyweb.type'][0] == 'text/plain', \
            'tiddlyweb.type should be text/plain, found %s' % environ['tiddlyweb.type'][0]


def test_file_extension():
    """
    Given a \.extension in the path_info,
    determine the type we want.
    """
    environ['PATH_INFO'] = '/bags/bag0/tiddlers/bigbox.html'
    
    neg.figure_type(environ)

    assert environ['tiddlyweb.type'][0] == 'text/html', \
            'tiddlyweb.type should be text/html, found %s' % environ['tiddlyweb.type'][0]

def test_file_wins_over_header():
    """
    Where there is both an extension and
    an accept header, the extension wins.
    """
    environ['HTTP_ACCEPT'] = 'text/plain; q=1.0, text/html, text/x-dvi; q=0.8, text/x-c'
    environ['PATH_INFO'] = '/bags/bag0/tiddlers/bigbox.html'

    neg.figure_type(environ)

    assert environ['tiddlyweb.type'][0] == 'text/html', \
            'tiddlyweb.type should be text/html, found %s' % environ['tiddlyweb.type'][0]

