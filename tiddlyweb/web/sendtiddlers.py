"""
Routines related to sending a list of tiddlers out
to the web, including sending those tiddlers and
validating cache headers for list of tiddlers.

These are important because this is what sends
a TiddlyWiki out.
"""

from sha import sha

from tiddlyweb.serializer import Serializer
from tiddlyweb.web.util import \
        get_serialize_type, http_date_from_timestamp, datetime_from_http_date
from tiddlyweb.web.http import HTTP404, HTTP304


def send_tiddlers(environ, start_response, bag):
    """
    Output the tiddlers contained in the provided
    bag in a Negotiated representation. Often, but
    not always, a wiki.
    """
    last_modified = None
    etag = None
    bags_tiddlers = bag.list_tiddlers()
    download = environ['tiddlyweb.query'].get('download', [None])[0]

    if bags_tiddlers:
        last_modified, etag = _validate_tiddler_list(environ, bags_tiddlers)
    else:
        raise HTTP404('No tiddlers in container')

    serialize_type, mime_type = get_serialize_type(environ)
    serializer = Serializer(serialize_type, environ)

    content_header = ('Content-Type', mime_type)
    cache_header = ('Cache-Control', 'no-cache')
    response = [content_header, cache_header]

    if serialize_type == 'wiki':
        if download:
            response.append(('Content-Disposition',
                'attachment; filename="%s"' % download))
    if last_modified:
        response.append(last_modified)
    if etag:
        response.append(etag)

    output = serializer.list_tiddlers(bag)
    start_response("200 OK", response)
    return [output]


def _validate_tiddler_list(environ, tiddlers):
    last_modified_number = _last_modified_tiddler(tiddlers)
    last_modified_string = http_date_from_timestamp(last_modified_number)
    last_modified = ('Last-Modified', last_modified_string)

    etag_string = '%s:%s' % (_sha_tiddler_titles(tiddlers),
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


def _sha_tiddler_titles(tiddlers):
    digest = sha()
    for tiddler in tiddlers:
        if tiddler.recipe:
            container = tiddler.recipe
        else:
            container = tiddler.bag
        digest.update(container.encode('utf-8') +
                tiddler.title.encode('utf-8'))
    return digest.hexdigest()


def _last_modified_tiddler(tiddlers):
    return str(max([int(tiddler.modified) for tiddler in tiddlers]))
