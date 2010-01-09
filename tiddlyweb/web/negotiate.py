"""
WSGI Middleware to do pseudo-content negotiation
and put the type in tiddlyweb.type.
"""
import logging


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
        self.figure_type(environ)
        return self.application(environ, start_response)

    def figure_type(self, environ):
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
        extension = path_info.rsplit('.', 1)
        if len(extension) == 2:
            ext = extension[-1]
            environ['tiddlyweb.extension'] = ext
            try:
                our_type = extension_types[ext]
                our_types.append(our_type)
            except KeyError:
                pass

    if accept_header:
        our_types.extend(_parse_accept_header(accept_header))

    logging.debug('negotiating for accept and extensions %s', our_types)

    environ['tiddlyweb.type'] = our_types

    return


def _parse_accept_header(header):
    """
    Parse the accept header to get the highest
    priority type. Copied from Perl's REST::Application
    Thanks Matthew O'Connor.
    """
    default_weight = 1
    prefs = []

    accept_types = header.strip().rstrip().split(',')
    order = 0
    for accept_type in accept_types:
        weight = None
        splits = accept_type.strip().rstrip().split(';')

        if splits[0]:
            name = splits[0]
        else:
            continue

        if len(splits) == 2:
            weight = splits[1]
            weight = weight.strip(' q=')
            weight = float(weight)

        prefs.append({'name': name, 'order': order})
        order += 1
        if weight:
            prefs[-1]['score'] = weight
        else:
            prefs[-1]['score'] = default_weight
            default_weight -= 0.001

    def sorter(cmp_a, cmp_b):
        return cmp(cmp_b['score'], cmp_a['score']) \
                or \
                cmp(cmp_a['order'], cmp_b['order'])

    prefs.sort(cmp=sorter)
    prefs = [pref['name'] for pref in prefs]
    prefs.append('*/*')
    return prefs
