"""
Routines related to sending a list of tiddlers out
to the web, including sending those tiddlers and
validating cache headers for list of tiddlers.
"""

from tiddlyweb import control
from tiddlyweb.filters import FilterError
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy
from tiddlyweb.serializer import Serializer, NoSerializationError
from tiddlyweb.util import sha
from tiddlyweb.web.util import \
        get_serialize_type, http_date_from_timestamp, datetime_from_http_date
from tiddlyweb.web.http import HTTP400, HTTP304, HTTP415


def send_tiddlers(environ, start_response, bag):
    """
    Output the tiddlers contained in the provided
    bag in a Negotiated representation. Often, but
    not always, a wiki.
    """
    last_modified = None
    etag = None
    download = environ['tiddlyweb.query'].get('download', [None])[0]
    filters = environ['tiddlyweb.filters']

    try:
        tiddlers = control.filter_tiddlers_from_bag(bag, filters)
    except FilterError, exc:
        raise HTTP400('malformed filter: %s' % exc)
    # We need to inherit revbag and searchbag setting from the provided bag.
    # We reuse name and policy information so we can have a richer
    # Etag when we send.
    tmp_bag = Bag(bag.name, tmpbag=True, revbag=bag.revbag,
            searchbag=bag.searchbag)
    tmp_bag.add_tiddlers(tiddlers)
    tmp_bag.desc = bag.desc
    tmp_bag.policy = bag.policy

    last_modified, etag = _validate_tiddler_list(environ, tmp_bag)

    serialize_type, mime_type = get_serialize_type(environ)

    content_header = ('Content-Type', mime_type)
    cache_header = ('Cache-Control', 'no-cache')
    vary_header = ('Vary', 'Accept')
    response = [content_header, cache_header, vary_header]

    if download:
        response.append(('Content-Disposition',
            'attachment; filename="%s"' % download.encode('utf-8')))
    if last_modified:
        response.append(last_modified)
    if etag:
        response.append(etag)

    serializer = Serializer(serialize_type, environ)
    try:
        output = serializer.list_tiddlers(tmp_bag)
    except NoSerializationError, exc:
        raise HTTP415('Content type not supported: %s:%s, %s' %
                (serialize_type, mime_type, exc))

    start_response("200 OK", response)

    if isinstance(output, basestring):
        return [output]
    else:
        return output


def _validate_tiddler_list(environ, bag):
    """
    Calculate the Last modified and ETag for
    the tiddlers in bag. If the ETag matches an
    incoming If-None-Match, then raise a 304 and
    don't send the tiddler content. If the modified
    string in an If-Modified-Since is newer than the
    last-modified on the tiddlers, raise 304.

    If ETag testing is done, no last modified handling
    is done, even if the ETag testing fails.

    If no 304 is raised, then just return last-modified
    and ETag for the caller to use in constructing
    its HTTP response.
    """
    last_modified_number = _last_modified_tiddler(bag)
    last_modified = None
    if last_modified_number:
        last_modified_string = http_date_from_timestamp(last_modified_number)
        last_modified = ('Last-Modified', last_modified_string)

    username = environ.get('tiddlyweb.usersign', {}).get('name', '')

    try:
        serialize_type, mime_type = get_serialize_type(environ)
        mime_type = mime_type.split(';', 1)[0].strip()
    except TypeError:
        mime_type = ''
    etag_string = '"%s:%s;%s"' % (_sha_tiddler_titles(bag),
            last_modified_number, sha('%s:%s' %
                (username, mime_type)).hexdigest())
    etag = ('Etag', etag_string)

    incoming_etag = environ.get('HTTP_IF_NONE_MATCH', None)
    if incoming_etag:
        if incoming_etag == etag_string:
            raise HTTP304(incoming_etag)
    else:
        incoming_modified = environ.get('HTTP_IF_MODIFIED_SINCE', None)
        if incoming_modified and \
                (datetime_from_http_date(incoming_modified) >= \
                datetime_from_http_date(last_modified_string)):
            raise HTTP304('')

    return last_modified, etag


def _sha_tiddler_titles(bag):
    """
    Create a sha digest of the titles of all the
    tiddlers in the bag. Include the recipe or
    bag name for disambiguation.
    """
    digest = sha()
    digest.update(bag.name.encode('utf-8'))
    digest.update(bag.desc.encode('utf-8'))
    for attribute in Policy.attributes:
        try:
            constraint_value = ''.join(getattr(bag.policy, attribute))
        except TypeError:
            constraint_value = getattr(bag.policy, attribute)
        if constraint_value == None:
            constraint_value = ''
        digest.update('%s:%s' % (attribute.encode('utf-8'),
            constraint_value.encode('utf-8')))
    for tiddler in bag.gen_tiddlers():
        container = tiddler.bag
        digest.update(container.encode('utf-8') +
                tiddler.title.encode('utf-8') + str(tiddler.revision))
    return digest.hexdigest()


def _last_modified_tiddler(bag):
    """
    Generate the last modified time for the tiddlers
    in this bag. It is the most recently modified time
    of all the tiddlers.
    """
    try:
        return str(max(int(tiddler.modified)
            for tiddler in bag.gen_tiddlers()))
    except ValueError:
        return ''
