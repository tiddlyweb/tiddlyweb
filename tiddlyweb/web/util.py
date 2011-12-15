"""
General utility routines shared by various web related modules.
"""

import Cookie
import urllib
import time
from datetime import datetime
try:
    from email.utils import parsedate
except ImportError:  # Python < 2.5
    from email.Utils import parsedate

from tiddlyweb.serializer import Serializer
from tiddlyweb.web.http import HTTP415, HTTP400
from tiddlyweb.util import sha


def get_route_value(environ, name):
    """
    Retrieve and decode from UTF-8 data provided in WSGI route.

    If name is not present in the route, allow KeyError to raise.

    If the provided data is not URI escaped UTF-8, raise and HTTP400
    """
    try:
        value = environ['wsgiorg.routing_args'][1][name]
        value = urllib.unquote(value).decode('utf-8')
    except UnicodeDecodeError, exc:
        raise HTTP400('incorrect encoding for %s, UTF-8 required: %s',
                exc)
    return value


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
        try:
            timestamp_datetime = datetime(*(time.strptime(timestamp,
                '%Y%m%d%H%M')[0:6]))
        except ValueError:
            timestamp_datetime = datetime(*(time.strptime(timestamp,
                '%Y%m%d%H%M%S')[0:6]))
    except ValueError:
        timestamp_datetime = datetime.utcnow()
    return timestamp_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')


def datetime_from_http_date(http_datestring):
    """
    Turn an HTTP formatted date into a datetime
    object.
    """
    if ';' in http_datestring:
        http_datestring = http_datestring.split(';', 1)[0].rstrip().lstrip()
    return datetime(*parsedate(http_datestring)[:6])


def make_cookie(name, value, mac_key=None, path=None,
        expires=None, httponly=True, domain=None):
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

    if domain:
        cookie[name]['domain'] = domain

    output = cookie.output(header='').lstrip().rstrip()
    if httponly:
        output += '; httponly'
    return output


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
    escape common character entities, incuding double quotes
    in attribute values

    This assumes values are enclosed in double quotes (key="value").
    """
    try:
        return html_encode(text).replace('"', '&quot;')
    except AttributeError:  # value might be None
        return text


def entity_etag(environ, entity):
    """
    Construct an etag from the JSON rep of an entity.
    """
    try:
        _, mime_type = get_serialize_type(environ)
        mime_type = mime_type.split(';', 1)[0].strip()
    except (AttributeError, TypeError):
        mime_type = ''
    if 'tiddlyweb.etag_serializer' in environ:
        serializer = environ['tiddlyweb.etag_serializer']
    else:
        serializer = Serializer('json', environ)
        environ['tiddlyweb.etag_serializer'] = serializer
    serializer.object = entity
    content = serializer.to_string()
    return '"%s"' % sha(content + mime_type).hexdigest()


def bag_etag(environ, bag):
    """
    Construct an etag for a bag.
    """
    return entity_etag(environ, bag)


def bag_url(environ, bag, full=True):
    """
    Construct a URL for a bag.
    """
    bag_link = 'bags/%s' % encode_name(bag.name)

    if full:
        return '%s/%s' % (server_base_url(environ), bag_link)
    else:
        return '%s/%s' % (_server_prefix(environ), bag_link)


def tiddler_etag(environ, tiddler):
    """
    Construct an etag for a tiddler from the tiddler's attributes,
    but not its text.
    """
    text = tiddler.text
    tiddler.text = ''
    bag_name = tiddler.bag or ''
    tiddler_id = '"%s/%s/%s:' % (encode_name(bag_name),
            encode_name(tiddler.title), tiddler.revision)
    etag = entity_etag(environ, tiddler)
    tiddler.text = text
    etag = etag.replace('"', tiddler_id, 1)
    return etag


def tiddler_url(environ, tiddler, container='bags', full=True):
    """
    Construct a URL for a tiddler. If the tiddler has a _canonical_uri
    field, use that instead.
    """
    if '_canonical_uri' in tiddler.fields:
        return tiddler.fields['_canonical_uri']

    container_name = tiddler.recipe if container == 'recipes' else tiddler.bag
    tiddler_link = '%s/%s/tiddlers/%s' % (container,
            encode_name(container_name), encode_name(tiddler.title))

    if full:
        return '%s/%s' % (server_base_url(environ), tiddler_link)
    else:
        return '%s/%s' % (_server_prefix(environ), tiddler_link)


def recipe_etag(environ, recipe):
    """
    Construct an etag for a recipe.
    """
    return entity_etag(environ, recipe)


def recipe_url(environ, recipe, full=True):
    """
    Construct a URL for a recipe.
    """
    recipe_link = 'recipes/%s' % encode_name(recipe.name)

    if full:
        return '%s/%s' % (server_base_url(environ), recipe_link)
    else:
        return '%s/%s' % (_server_prefix(environ), recipe_link)
