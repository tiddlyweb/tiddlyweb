"""
General utility routines shared by various
web related modules.
"""

import Cookie
import urllib
import time
from datetime import datetime

from tiddlyweb.web.http import HTTP415
from tiddlyweb.util import sha


def get_serialize_type(environ):
    """
    Look in the environ to determine which serializer
    we should use for this request.
    """
    config = environ['tiddlyweb.config']
    accept = environ.get('tiddlyweb.type')[:]
    ext = environ.get('tiddlyweb.extension')
    serializers = config['serializers']
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
        # If we are a PUT and we haven't found a serializer, don't
        # state a default as that makes no sense.
        if environ['REQUEST_METHOD'] == 'GET':
            default_serializer = config['default_serializer']
            serialize_type, mime_type = serializers[default_serializer]
    return serialize_type, mime_type


def handle_extension(environ, resource_name):
    """
    Look for an extension on the provided resource_name and
    trim it off to give the "real" resource_name.
    """
    extension = environ.get('tiddlyweb.extension')
    extension_types = environ['tiddlyweb.config']['extension_types']
    if extension and extension in extension_types:
        try:
            resource_name = resource_name[0:resource_name.rindex('.'
                + extension)]
        except ValueError:
            pass
    else:
        try:
            del(environ['tiddlyweb.extension'])
        except KeyError:
            pass

    return resource_name


def http_date_from_timestamp(timestamp):
    """
    Turn a modifier or created tiddler timestamp
    into a proper formatted HTTP date.
    """
    try:
        timestamp_datetime = datetime(*(time.strptime(timestamp,
            '%Y%m%d%H%M')[0:6]))
    except ValueError:
        timestamp_datetime = datetime(*(time.strptime(timestamp,
            '%Y%m%d%H%M%S')[0:6]))
    return timestamp_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')


def datetime_from_http_date(http_datestring):
    """
    Turn an HTTP formatted date into a datetime
    object.
    """
    if ';' in http_datestring:
        http_datestring = http_datestring.split(';', 1)[0].rstrip().lstrip()
    http_datetime = datetime(*(time.strptime(http_datestring,
        '%a, %d %b %Y %H:%M:%S GMT')[0:6]))
    return http_datetime


def make_cookie(name, value, mac_key=None, path=None, expires=None):
    """
    Create a cookie string, optionally with a MAC, path and
    expires value. Expires is in seconds.
    """
    cookie = Cookie.SimpleCookie()

    value = value.encode('utf-8')

    if mac_key:
        secret_string = sha('%s%s' % (value, mac_key)).hexdigest()
        cookie[name] = '%s:%s' % (value, secret_string)
    else:
        cookie[name] = value

    if path:
        cookie[name]['path'] = path

    if expires:
        cookie[name]['max-age'] = expires

    return cookie.output(header='').lstrip().rstrip()


def server_base_url(environ):
    """
    Using information in tiddlyweb.config, construct
    the base URL of the server, sans the trailing /.
    """
    return '%s%s' % (server_host_url(environ), _server_prefix(environ))


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
    return '%s://%s%s' % (server_host['scheme'], server_host['host'], port)


def _server_prefix(environ):
    """
    Get the server_prefix out of tiddlyweb.config.
    """
    config = environ.get('tiddlyweb.config', {})
    return config.get('server_prefix', '')


def encode_name(name):
    """
    Encode a unicode as utf-8 and then url encode that
    string. Use for entity titles in URLs.
    """
    return urllib.quote(name.encode('utf-8'), safe='')


def html_encode(text):
    """
    Encode &, < and > entities in text that will
    be used in/as HTML.
    """
    return (text.replace('&', '&amp;').replace('<', '&lt;').
            replace('>', '&gt;'))


def escape_attribute_value(text):
    """
    escape double quotes in attribute values

    This assumes values are enclosed in double quotes (key="value").
    """
    try:
        return text.replace('"', '&quot;')
    except AttributeError: # value might be None
        return text


def tiddler_url(environ, tiddler):
    """
    Construct a URL for a tiddler.
    """
    if tiddler.recipe:
        tiddler_link = 'recipes/%s/tiddlers/%s' \
                % (encode_name(tiddler.recipe),
                        encode_name(tiddler.title))
    else:
        tiddler_link = 'bags/%s/tiddlers/%s' \
                % (encode_name(tiddler.bag),
                        encode_name(tiddler.title))
    return '%s/%s' % (server_base_url(environ), tiddler_link)


def recipe_url(environ, recipe):
    """
    Construct a URL for a recipe.
    """
    return '%s/recipes/%s' % (server_base_url(environ),
            encode_name(recipe.name))


def bag_url(environ, bag):
    """
    Construct a URL for a bag.
    """
    return '%s/bags/%s' % (server_base_url(environ),
            encode_name(bag.name))
