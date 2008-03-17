import urllib

from tiddlyweb.web.http import HTTP415

def get_serialize_type(environ, serializers):
    accept = environ.get('tiddlyweb.type')[:]
    ext = environ.get('tiddlyweb.extension')
    serialize_type, mime_type = None, None

    while len(accept) and serialize_type == None:
        type = accept.pop(0)
        try:
            serialize_type, mime_type = serializers[type]
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
        resource_name = resource_name[0 : resource_name.rfind('.' + extension)]

    return resource_name

def root(environ, start_response):
    """
    Convenience method to provide an entry point at root.
    """

    start_response("200 OK", [('Content-Type', 'text/html')])
    return ["""<html>
<head>
<title>TiddlyWeb</title>
</head>
<body>
<ul>
<li><a href="recipes">recipes</a></li>
<li><a href="bags">bags</a></li>
</ul>
<body>
</html>"""]

def tiddler_url(environ, tiddler):
    """
    Construct a URL for a tiddler.
    This relies on HTTP_HOST, which may not be reliable. REVIEW
    """
    scheme = environ['wsgi.url_scheme']
    host = environ.get('HTTP_HOST', '')
    return '%s://%s/bags/%s/tiddlers/%s' % (scheme, host, urllib.quote(tiddler.bag), urllib.quote(tiddler.title))

