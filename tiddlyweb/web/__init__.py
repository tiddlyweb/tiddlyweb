import urllib
import time
from datetime import datetime

from tiddlyweb.web.http import HTTP415

serializers = {
        'text/x-tiddlywiki': ['wiki', 'text/html; charset=UTF-8'],
        'text/html': ['html', 'text/html; charset=UTF-8'],
        'text/plain': ['text', 'text/plain; charset=UTF-8'],
        'application/json': ['json', 'application/json; charset=UTF-8'],
        'default': ['html', 'text/html; charset=UTF-8'],
        }

root_page = """<html>
<head>
<title>TiddlyWeb</title>
</head>
<body>
<ul>
<li><a href="recipes">recipes</a></li>
<li><a href="bags">bags</a></li>
</ul>
<body>
</html>"""

def get_serialize_type(environ):
    accept = environ.get('tiddlyweb.type')[:]
    ext = environ.get('tiddlyweb.extension')
    serialize_type, mime_type = None, None

    if type(accept) == str:
        accept = [accept]

    while len(accept) and serialize_type == None:
        candidate_type = accept.pop(0)
        try:
            serialize_type, mime_type = serializers[candidate_type]
        except KeyError:
            pass
    if not serialize_type:
        if ext:
            raise HTTP415, '%s type unsupported' % ext
        serialize_type, mime_type = serializers['default']
    return serialize_type, mime_type

def handle_extension(environ, resource_name):
    extension = environ.get('tiddlyweb.extension')
    if extension:
        try:
            resource_name = resource_name[0 : resource_name.rindex('.' + extension)]
        except ValueError:
            pass

    return resource_name

def root(environ, start_response):
    """
    Convenience method to provide an entry point at root.
    """

    start_response("200 OK", [('Content-Type', 'text/html; charset=UTF-8')])
    return [root_page]

def tiddler_url(environ, tiddler):
    """
    Construct a URL for a tiddler.
    This relies on HTTP_HOST, which may not be reliable. REVIEW
    """
    scheme = environ['wsgi.url_scheme']
    host = environ.get('HTTP_HOST', '')
    return '%s://%s/bags/%s/tiddlers/%s' % (scheme, host, urllib.quote(tiddler.bag), urllib.quote(tiddler.title))

def recipe_url(environ, recipe):
    """
    Construct a URL for a recipe.
    This relies on HTTP_HOST, which may not be reliable. REVIEW
    """
    scheme = environ['wsgi.url_scheme']
    host = environ.get('HTTP_HOST', '')
    return '%s://%s/recipes/%s' % (scheme, host, urllib.quote(recipe.name))

def bag_url(environ, bag):
    """
    Construct a URL for a recipe.
    This relies on HTTP_HOST, which may not be reliable. REVIEW
    """
    scheme = environ['wsgi.url_scheme']
    host = environ.get('HTTP_HOST', '')
    return '%s://%s/bags/%s' % (scheme, host, urllib.quote(bag.name))

def http_date_from_timestamp(timestamp):
    timestamp_datetime = datetime(*(time.strptime(timestamp, '%Y%m%d%H%M')[0:6]))
    return timestamp_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')
