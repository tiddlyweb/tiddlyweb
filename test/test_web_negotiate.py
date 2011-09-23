
"""
Test the content negotiation pieces.

Content negotiation will put something in
the environment that allows us to determine
what kind of store and serializer to use.
"""


from tiddlyweb.web.negotiate import figure_type
from tiddlyweb.config import config

def setup_module(module):
    module.environ = {'tiddlyweb.config': config}
    environ['REQUEST_METHOD'] = 'GET'

def test_accept_header():
    """
    Given an accept header in the environ,
    determine the type we want.
    """
    environ['HTTP_ACCEPT'] = 'text/plain; q=1.0, text/html; q=0.9, text/x-dvi; q=0.8, text/x-c'

    figure_type(environ)

    assert environ['tiddlyweb.type'][0] == 'text/plain'

def test_accept_ill_formed_header():
    """
    Given an accept header in the environ,
    that is poorly formed, use default.
    """
    environ['HTTP_ACCEPT'] = '; q=1.0, text/plain; q=1.0, text/html, text/x-dvi; q=0.8, text/x-c'

    figure_type(environ)

    assert environ['tiddlyweb.type'][0] == 'text/html'

def test_accept_bad_q():
    """
    Given a non-float q, ignore.
    """
    environ['HTTP_ACCEPT'] = 'text/plain; q=hot, text/html, text/postscript; q=0.5'

    figure_type(environ)

    assert environ['tiddlyweb.type'][0] == 'text/html'

def test_accept_extension():
    """
    Ignore non q= style parameters.
    """
    environ['HTTP_ACCEPT'] = 'text/plain; cookies=chip'
    figure_type(environ)
    assert environ['tiddlyweb.type'][0] == 'text/plain'

def test_file_extension():
    """
    Given a \.extension in the path_info,
    determine the type we want.
    """
    environ['PATH_INFO'] = '/bags/bag0/tiddlers/bigbox.html'
    
    figure_type(environ)

    assert environ['tiddlyweb.type'][0] == 'text/html', \
            'tiddlyweb.type should be text/html, found %s' % environ['tiddlyweb.type'][0]

def test_file_wins_over_header():
    """
    Where there is both an extension and
    an accept header, the extension wins.
    """
    environ['HTTP_ACCEPT'] = 'text/plain; q=1.0, text/html, text/x-dvi; q=0.8, text/x-c'
    environ['PATH_INFO'] = '/bags/bag0/tiddlers/bigbox.html'

    figure_type(environ)

    assert environ['tiddlyweb.type'][0] == 'text/html', \
            'tiddlyweb.type should be text/html, found %s' % environ['tiddlyweb.type'][0]

