import urllib
import time
from datetime import datetime

from tiddlyweb.web.http import HTTP415

def get_serialize_type(environ):
    accept = environ.get('tiddlyweb.type')[:]
    ext = environ.get('tiddlyweb.extension')
    serializers = environ['tiddlyweb.config']['serializers']
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

def http_date_from_timestamp(timestamp):
    timestamp_datetime = datetime(*(time.strptime(timestamp, '%Y%m%d%H%M')[0:6]))
    return timestamp_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')

def datetime_from_http_date(http_datestring):
    http_datetime = datetime(*(time.strptime(http_datestring, '%a, %d %b %Y %H:%M:%S GMT')[0:6]))
    return http_datetime

def server_base_url(environ):
    """
    Using information in tiddlyweb.config, construct 
    the base URL of the server, sans the trailing /.
    """
    server_host = environ['tiddlyweb.config']['server_host']
    port = str(server_host['port'])
    if port == '80' or port == '443':
        port = ''
    else:
        port = ':%s' % port
    host = '%s://%s%s' % (server_host['scheme'], server_host['host'], port)
    return host

def tiddler_url(environ, tiddler):
    """
    Construct a URL for a tiddler.
    """
    return '%s/bags/%s/tiddlers/%s' % (server_base_url(environ), urllib.quote(tiddler.bag), urllib.quote(tiddler.title))

def recipe_url(environ, recipe):
    """
    Construct a URL for a recipe.
    """
    return '%s/recipes/%s' % (server_base_url(environ), urllib.quote(recipe.name))

def bag_url(environ, bag):
    """
    Construct a URL for a recipe.
    """
    return '%s/bags/%s' % (server_base_url(environ), urllib.quote(bag.name))

