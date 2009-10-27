"""
Routines related to sending a list of tiddlers out
to the web, including sending those tiddlers and
validating cache headers for list of tiddlers.
"""

from tiddlyweb import control
from tiddlyweb.filters import FilterError
from tiddlyweb.model.bag import Bag
from tiddlyweb.serializer import Serializer, NoSerializationError
from tiddlyweb.util import sha
from tiddlyweb.web.util import \
        get_serialize_type, http_date_from_timestamp, datetime_from_http_date
from tiddlyweb.web.http import HTTP400, HTTP404, HTTP304, HTTP415


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
    tmp_bag = Bag('tmp_bag', tmpbag=True, revbag=bag.revbag,
            searchbag=bag.searchbag)
    tmp_bag.add_tiddlers(tiddlers)

    # If there are no tiddlers in the bag, validation will
    # raise 404. If incoming Etag is acceptable, will raise 304.
    last_modified, etag = _validate_tiddler_list(environ, tmp_bag)

    serialize_type, mime_type = get_serialize_type(environ)

    content_header = ('Content-Type', mime_type)
    cache_header = ('Cache-Control', 'no-cache')
    response = [content_header, cache_header]

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
    return [output]


def _validate_tiddler_list(environ, bag):
    last_modified_number = _last_modified_tiddler(bag)
    last_modified = None
    if last_modified_number:
        last_modified_string = http_date_from_timestamp(last_modified_number)
        last_modified = ('Last-Modified', last_modified_string)

    etag_string = '"%s:%s"' % (_sha_tiddler_titles(bag),
            last_modified_number)
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
    digest = sha()
    for tiddler in bag.gen_tiddlers():
        if tiddler.recipe:
            container = tiddler.recipe
        else:
            container = tiddler.bag
        digest.update(container.encode('utf-8') +
                tiddler.title.encode('utf-8'))
    return digest.hexdigest()


def _last_modified_tiddler(bag):
    # If there are no tiddlers, raise a 404
    try:
        return str(max(int(tiddler.modified) for tiddler in bag.gen_tiddlers()))
    except ValueError:
        return ''
