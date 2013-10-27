"""
Routines related to sending a list of :py:class:`tiddlers
<tiddlyweb.model.tiddler.Tiddler>` out to the web, including optionally
:py:mod:`filtering <tiddlyweb.filters>` those tiddlers and
validating cache-oriented request headers.
"""

import logging
import inspect

from httpexceptor import HTTP400, HTTP415

from tiddlyweb.filters import FilterError, recursive_filter
from tiddlyweb.model.collections import Tiddlers
from tiddlyweb.serializer import Serializer, NoSerializationError
from tiddlyweb.util import sha
from tiddlyweb.web.util import (get_serialize_type, http_date_from_timestamp,
        check_last_modified, check_incoming_etag, encode_name)

from tiddlyweb.fixups import basestring


LOGGER = logging.getLogger(__name__)


def send_tiddlers(environ, start_response, tiddlers=None):
    """
    Output the :py:class:`tiddlers <tiddlyweb.model.tiddler.Tiddler>`
    contained in the provided :py:class:`Tiddlers collection
    <tiddlyweb.model.collections.Tiddlers>` in a :py:mod:`Negotiated
    <tiddlyweb.web.negotiate>` representation.
    """
    download = environ['tiddlyweb.query'].get('download', [None])[0]
    filters = environ['tiddlyweb.filters']
    store = environ['tiddlyweb.store']

    if tiddlers.store is None and not filters:
        LOGGER.warn('Incoming tiddlers no store set %s', inspect.stack()[1])

    if filters:
        candidate_tiddlers = _filter_tiddlers(filters, store, tiddlers)
    else:
        candidate_tiddlers = tiddlers

    last_modified, etag = _validate_tiddler_list(environ, candidate_tiddlers)

    serialize_type, mime_type = get_serialize_type(environ, collection=True)

    response = [('Content-Type', mime_type),
            ('Cache-Control', 'no-cache'),
            ('Vary', 'Accept')]

    if download:
        response.append(('Content-Disposition',
            'attachment; filename="%s"' % encode_name(download)))

    if last_modified:
        response.append(last_modified)

    if etag:
        response.append(etag)

    try:
        serializer = Serializer(serialize_type, environ)
        output = serializer.list_tiddlers(candidate_tiddlers)
    except NoSerializationError as exc:
        raise HTTP415('Content type not supported: %s:%s, %s' %
                (serialize_type, mime_type, exc))
    except FilterError as exc:  # serializations may filter tildders
        raise HTTP400('malformed filter or tiddler during filtering: %s' % exc)

    start_response("200 OK", response)

    if isinstance(output, basestring):
        return [output]
    else:
        return output


def _filter_tiddlers(filters, store, tiddlers):
    """
    Filter the tiddlers by filters provided by the environment.
    """
    candidate_tiddlers = Tiddlers(store=store)
    try:
        candidate_tiddlers.title = tiddlers.title
        candidate_tiddlers.link = tiddlers.link
        candidate_tiddlers.is_search = tiddlers.is_search
        candidate_tiddlers.is_revisions = tiddlers.is_revisions
        candidate_tiddlers.bag = tiddlers.bag
        candidate_tiddlers.recipe = tiddlers.recipe
    except AttributeError:
        pass
    try:
        for tiddler in recursive_filter(filters, tiddlers):
            candidate_tiddlers.add(tiddler)
    except FilterError as exc:
        raise HTTP400('malformed filter: %s' % exc)
    return candidate_tiddlers


def _validate_tiddler_list(environ, tiddlers):
    """
    Do Etag and Last modified checks on the
    collection of tiddlers.

    If ETag testing is done, no last modified handling
    is done, even if the ETag testing fails.

    If no 304 is raised, then just return last-modified
    and ETag for the caller to use in constructing
    its HTTP response.
    """
    last_modified_string = http_date_from_timestamp(tiddlers.modified)
    last_modified = ('Last-Modified', last_modified_string)

    username = environ.get('tiddlyweb.usersign', {}).get('name', '')

    try:
        _, mime_type = get_serialize_type(environ)
        mime_type = mime_type.split(';', 1)[0].strip()
    except TypeError:
        mime_type = ''
    etag_string = '"%s:%s"' % (tiddlers.hexdigest(),
            sha('%s:%s' % (username, mime_type)).hexdigest())
    etag = ('Etag', etag_string)

    incoming_etag = check_incoming_etag(environ, etag_string,
            last_modified=last_modified_string)
    if not incoming_etag:  # only check last modified when no etag
        check_last_modified(environ, last_modified_string,
                etag=etag_string)

    return last_modified, etag
