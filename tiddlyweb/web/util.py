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
            raise HTTP415('%s type unsupported' % ext)
        serialize_type, mime_type = serializers['default']
    return serialize_type, mime_type


def handle_extension(environ, resource_name):
    extension = environ.get('tiddlyweb.extension')
    if extension:
        try:
            resource_name = resource_name[0:resource_name.rindex('.' + extension)]
        except ValueError:
            pass

    return resource_name


def filter_query_string(environ):
    filter_string = environ['tiddlyweb.query'].get('filter', [''])[0]
    filter_string = urllib.unquote(filter_string)
    return unicode(filter_string, 'utf-8')


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
    url = '%s%s' % (server_host_url(environ), _server_prefix(environ))
    return url


def server_host_url(environ):
    """
    Generate the scheme and host portion of our server url.
    """
    server_host = environ['tiddlyweb.config']['server_host']
    port = str(server_host['port'])
    if port == '80' or port == '443':
        port = ''
    else:
        port = ':%s' % port
    url = '%s://%s%s' % (server_host['scheme'], server_host['host'], port)
    return url


def _server_prefix(environ):
    config = environ.get('tiddlyweb.config', {})
    return config.get('server_prefix', '')


def tiddler_url(environ, tiddler):
    """
    Construct a URL for a tiddler.
    """
    if tiddler.recipe:
        tiddler_link = 'recipes/%s/tiddlers/%s' \
                % (tiddler.recipe.encode('utf-8'), urllib.quote(tiddler.title.encode('utf-8')))
    else:
        tiddler_link = 'bags/%s/tiddlers/%s' \
                % (tiddler.bag.encode('utf-8'), urllib.quote(tiddler.title.encode('utf-8')))
    return '%s/%s' % (server_base_url(environ), tiddler_link)


def recipe_url(environ, recipe):
    """
    Construct a URL for a recipe.
    """
    return '%s/recipes/%s' % (server_base_url(environ), urllib.quote(recipe.name.encode('utf-8')))


def bag_url(environ, bag):
    """
    Construct a URL for a recipe.
    """
    return '%s/bags/%s' % (server_base_url(environ), urllib.quote(bag.name.encode('utf-8')))
