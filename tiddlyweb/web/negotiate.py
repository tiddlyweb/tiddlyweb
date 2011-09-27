"""
WSGI Middleware to do pseudo-content negotiation and put the type in
tiddlyweb.type. If extensions are provided on a GET URI that match
extension_types, they win over the Accept header.
"""

import logging
import mimeparse


class Negotiate(object):
    """
    Perform a form of content negotiation
    to provide information to the environment
    that will later be used to choose
    serializers.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        figure_type(environ)
        return self.application(environ, start_response)


def figure_type(environ):
    """
    Determine either the content-type (for POST, PUT, DELETE)
    or accept header (for GET) and put that information
    in tiddlyweb.type in the environment.
    """
    if environ['REQUEST_METHOD'].upper() == 'GET':
        _figure_type_for_get(environ)
    else:
        _figure_type_for_other(environ)


def _figure_type_for_other(environ):
    """
    Determine the type for PUT and POST
    requests, based on the content-type
    header.
    """
    content_type = environ.get('CONTENT_TYPE', None)
    if content_type:
        logging.debug('negotiating for content-type %s', content_type)
        content_type = content_type.split(';')[0]
        environ['tiddlyweb.type'] = content_type


def _figure_type_for_get(environ):
    """
    Determine the type for a GET request,
    based on the Accept header and url path
    filename extensions (if there an extension
    wins).
    """
    accept_header = environ.get('HTTP_ACCEPT')
    path_info = environ.get('PATH_INFO')

    extension_types = environ['tiddlyweb.config']['extension_types']

    our_types = []

    if path_info:
        last_segment = path_info.rsplit('/', 1)[-1]
        extension = last_segment.rsplit('.', 1)
        if len(extension) == 2:
            ext = extension[-1]
            environ['tiddlyweb.extension'] = ext
            try:
                our_type = extension_types[ext]
                our_types.append(our_type)
            except KeyError:
                pass

    if accept_header:
        default_type = environ['tiddlyweb.config']['default_serializer']
        matchable_types = environ['tiddlyweb.config']['serializers'].keys()
        matchable_types.append(default_type)
        try:
            our_types.append(mimeparse.best_match(
                matchable_types, accept_header))
        except ValueError:
            our_types.append(default_type)

    logging.debug('negotiating for accept and extensions %s', our_types)

    environ['tiddlyweb.type'] = our_types

    return
