"""
General utility routines shared by various web related modules.
"""

from datetime import datetime

from email.utils import parsedate

from httpexceptor import HTTP415, HTTP400, HTTP304

from tiddlyweb.model.policy import PermissionsError
from tiddlyweb.model.tiddler import timestring_to_datetime, current_timestring
from tiddlyweb.serializer import Serializer
from tiddlyweb.util import sha

from tiddlyweb.fixups import SimpleCookie, quote, unquote

try:
    unicode
except NameError:
    unicode = str


def check_bag_constraint(environ, bag, constraint):
    """
    Check to see if the provided :py:class:`bag <tiddlyweb.model.bag.Bag>`
    allows the current ``tiddlyweb.usersign`` to perform the action described
    by ``constraint``. Lets NoBagError raise if the bag does not exist.

    This is a web util because user and store come from the WSGI environ.
    """
    try:
        store = environ['tiddlyweb.store']
        usersign = environ['tiddlyweb.usersign']
        bag = store.get(bag)
        bag.policy.allows(usersign, constraint)
    except (PermissionsError) as exc:
        # XXX this throws away traceback info
        msg = 'for bag %s: %s' % (bag.name, exc)
        raise exc.__class__(msg)


def check_incoming_etag(environ, etag_string, cache_control='no-cache',
        last_modified=None, vary='Accept'):
    """
    Raise 304 if the provided ``etag_string`` is the same as that found
    in the ``If-None-Match`` header of the incoming request.

    Return ``incoming_etag`` to indicate if an etag was there but
    did not match.
    """
    incoming_etag = environ.get('HTTP_IF_NONE_MATCH', None)
    if incoming_etag:
        if incoming_etag == etag_string:
            raise HTTP304(incoming_etag, vary=vary,
                    cache_control=cache_control,
                    last_modified=last_modified)
    return incoming_etag


def check_last_modified(environ, last_modified_string, etag='',
        cache_control='no-cache', vary='Accept'):
    """
    Raise ``304`` if an ``If-Modified-Since`` header matches
    ``last_modified_string``.
    """
    incoming_modified = environ.get('HTTP_IF_MODIFIED_SINCE', None)
    if incoming_modified:
        incoming_modified = datetime_from_http_date(incoming_modified)
        if incoming_modified and (incoming_modified >=
                datetime_from_http_date(last_modified_string)):
            raise HTTP304(etag, vary=vary, cache_control=cache_control,
                    last_modified=last_modified_string)


def content_length_and_type(environ):
    """
    For ``PUT`` or ``POST`` request there must be ``Content-Length`` and
    ``Content-Type`` headers. Raise ``400`` if not present in the request.
    """
    try:
        length = environ['CONTENT_LENGTH']
        content_type = environ['tiddlyweb.type']
    except KeyError:
        raise HTTP400(
                'Content-Length and content-type required to PUT or POST')
    return length, content_type


def get_route_value(environ, name):
    """
    Retrieve and decode ``name`` from data provided in WSGI route.

    If ``name`` is not present in the route, allow KeyError to raise.
    """
    value = environ['wsgiorg.routing_args'][1][name]
    value = unquote(value)
    return value.replace('%2F', '/')


def get_serialize_type(environ, collection=False):
    """
    Look in the ``environ`` to determine which :py:class:`serializer
    <tiddlyweb.serializer.Serializer>` should be used for this request.

    If ``collection`` is ``True``, then the presence of an extension
    on the URI which does not match any serializer should lead to a ``415``.
    """
    config = environ['tiddlyweb.config']
    accept = environ.get('tiddlyweb.type', [])[:]
    ext = environ.get('tiddlyweb.extension')
    extension_types = config['extension_types']
    serializers = config['serializers']
    serialize_type, mime_type = None, None

    if collection and ext and ext not in extension_types:
        accept = [None]

    if type(accept) == unicode or type(accept) == str:
        accept = [accept]

    while len(accept) and serialize_type is None:
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
        if environ.get('REQUEST_METHOD') == 'GET':
            default_serializer = config['default_serializer']
            serialize_type, mime_type = serializers[default_serializer]
    return serialize_type, mime_type


def handle_extension(environ, resource_name):
    """
    Look for an extension (as defined in :py:mod:`config <tiddlyweb.config>`)
    on the provided ``resource_name`` and trim it off to give the
    "real" resource name.
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


def html_frame(environ, title=''):
    """
    Return the header and footer from the current HTML
    :py:class:`serialization
    <tiddlyweb.serializations.SerializationInterface>`.
    """
    html = environ.get('tiddlyweb.config', {}).get(
            'serializers', {}).get('text/html')[0]
    html = Serializer(html, environ).serialization
    header = html._header(title)
    footer = html._footer()
    return header, footer


def http_date_from_timestamp(timestamp):
    """
    Turn a modifier or created tiddler ``timestamp``
    into a properly formatted HTTP date. If the timestamp
    is invalid use the current time as the timestamp.
    """
    try:
        timestamp_datetime = timestring_to_datetime(timestamp)
    except ValueError:
        timestamp_datetime = timestring_to_datetime(current_timestring())
    return timestamp_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')


def datetime_from_http_date(http_datestring):
    """
    Turn an HTTP formatted date into a datetime object.
    Return ``None`` if the date string is invalid.
    """
    if ';' in http_datestring:
        http_datestring = http_datestring.split(';', 1)[0].rstrip().lstrip()
    try:
        return datetime(*parsedate(http_datestring)[:6])
    except TypeError:
        return None


def make_cookie(name, value, mac_key=None, path=None,
        expires=None, httponly=True, domain=None):
    """
    Create a cookie string, optionally with a MAC, path and
    expires value. If ``expires`` is provided, its value should be
    in seconds.
    """
    cookie = SimpleCookie()

    # XXX: backwards to 2.x?
    #value = value.encode('utf-8')

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


def read_request_body(environ, length):
    """
    Read the ``wsgi.input`` handle to get the request body.

    Length is a required parameter because it is tested for existence
    earlier in the process.
    """
    try:
        length = int(length)
        input_handle = environ['wsgi.input']
        return input_handle.read(length)
    except (KeyError, ValueError, IOError) as exc:
        raise HTTP400('Error reading request body: %s', exc)


def server_base_url(environ):
    """
    Using information in :py:mod:`tiddlyweb.config`, construct
    the base URL of the server, without the trailing ``/``.
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
    Get the ``server_prefix`` out of :py:mod:`tiddlyweb.config`.
    """
    config = environ.get('tiddlyweb.config', {})
    return config.get('server_prefix', '')


def encode_name(name):
    """
    Encode a unicode value as utf-8 and then URL encode that
    string. Use for entity titles in URLs.
    """
    return quote(name.encode('utf-8'), safe=".!~*'()")


def html_encode(text):
    """
    Encode ``&``, ``<`` and ``>`` entities in ``text`` that will
    be used in or as HTML.
    """
    return (text.replace('&', '&amp;').replace('<', '&lt;').
            replace('>', '&gt;'))


def escape_attribute_value(text):
    """
    Escape common HTML character entities, including double quotes
    in attribute values

    This assumes values are enclosed in double quotes (key="value").
    """
    try:
        return html_encode(text).replace('"', '&quot;')
    except AttributeError:  # value might be None
        return text


def entity_etag(environ, entity):
    """
    Construct an Etag from the digest of the :py:class:`JSON
    <tiddlyweb.serializations.json.Serialization>` reprepresentation
    of an entity.

    The JSON representation provides a reasonably repeatable and
    unique string of data.
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
    Construct an etag for a :py:class:`bag <tiddlyweb.model.bag.Bag>`.
    """
    return entity_etag(environ, bag)


def bag_url(environ, bag, full=True):
    """
    Construct a URL for a :py:class:`bag <tiddlyweb.model.bag.Bag>`.
    """
    bag_link = 'bags/%s' % encode_name(bag.name)

    if full:
        return '%s/%s' % (server_base_url(environ), bag_link)
    else:
        return '%s/%s' % (_server_prefix(environ), bag_link)


def tiddler_etag(environ, tiddler):
    """
    Construct an etag for a :py:class:`tiddler
    <tiddlyweb.model.tiddler.Tiddler>` from the tiddler's attributes,
    but not its text.
    """
    text = tiddler.text
    tiddler.text = ''
    if not tiddler.revision:
        tiddler.revision = 0
    bag_name = tiddler.bag or ''
    tiddler_id = '"%s/%s/%s:' % (encode_name(bag_name),
            encode_name(tiddler.title), encode_name('%s' % tiddler.revision))
    etag = entity_etag(environ, tiddler)
    tiddler.text = text
    etag = etag.replace('"', tiddler_id, 1)
    return etag


def tiddler_url(environ, tiddler, container='bags', full=True):
    """
    Construct a URL for a :py:class:`tiddler
    <tiddlyweb.model.tiddler.Tiddler>`.
    """
    container_name = tiddler.recipe if container == 'recipes' else tiddler.bag
    tiddler_link = '%s/%s/tiddlers/%s' % (container,
            encode_name(container_name), encode_name(tiddler.title))

    if full:
        return '%s/%s' % (server_base_url(environ), tiddler_link)
    else:
        return '%s/%s' % (_server_prefix(environ), tiddler_link)


def recipe_etag(environ, recipe):
    """
    Construct an etag for a :py:class:`recipe <tiddlyweb.model.recipe.Recipe>`.
    """
    return entity_etag(environ, recipe)


def recipe_url(environ, recipe, full=True):
    """
    Construct a URL for a :py:class:`recipe <tiddlyweb.model.recipe.Recipe>`.
    """
    recipe_link = 'recipes/%s' % encode_name(recipe.name)

    if full:
        return '%s/%s' % (server_base_url(environ), recipe_link)
    else:
        return '%s/%s' % (_server_prefix(environ), recipe_link)
