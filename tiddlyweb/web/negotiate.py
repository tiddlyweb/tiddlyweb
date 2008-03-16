"""
WSGI Middleware to do pseudo-content negotiation
and put the type in tiddlyweb.accept.
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
        self.figure_accept(environ)
        return self.application(environ,start_response)

    def figure_accept(self, environ):
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
                        environ['tiddlyweb.accept'] = [our_type]
                        return
                    except KeyError:
                        pass

        if accept_header:
            our_types = self._parse_accept_header(accept_header)

        environ['tiddlyweb.accept'] = our_types

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
