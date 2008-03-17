"""
WSGI Middleware to do pseudo-content negotiation
and put the type in tiddlyweb.type.
"""

extension_types = {
        'txt': 'text/plain',
        'html': 'text/html',
        'json': 'application/json',
        'wiki': 'text/x-tiddlywiki',
        }

class Negotiate(object):

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        self.figure_type(environ)
        return self.application(environ,start_response)

    def figure_type(self, environ):
        """
        Determine either the content-type (for POST, PUT, DELETE)
        or accept header (for GET) and put that information
        in tiddlyweb.type in the environment.
        """
        if environ['REQUEST_METHOD'].upper() == 'GET':
            self._figure_type_for_get(environ)
        else:
            self._figure_type_for_other(environ)

    def _figure_type_for_other(self, environ):
        environ['tiddlyweb.type'] = environ.get('CONTENT_TYPE')

    def _figure_type_for_get(self, environ):
        accept_header = environ.get('HTTP_ACCEPT')
        path_info = environ.get('PATH_INFO')

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
            our_types.extend(self._parse_accept_header(accept_header))

        environ['tiddlyweb.type'] = our_types

        return 

    def _parse_accept_header(self, header):
# copied from REST::Application
# thanks matthew!
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

        def sorter(x, y):
            return cmp(y['score'], x['score']) \
                    or \
                    cmp(x['order'], y['order'])

        prefs.sort(cmp=sorter)
        prefs = [pref['name'] for pref in prefs]
        prefs.append('*/*')
        return prefs
