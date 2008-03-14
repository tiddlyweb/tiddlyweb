"""
WSGI Middleware to do pseudo-content negotiation
and put the type in tiddlyweb.accept.
"""

extension_types = {
        'txt': 'text/plain',
        'html': 'text/html',
        'json': 'application/json',
        'wiki': 'text/x-tiddlywiki',
        'default': 'text/plain'
        }

def type(environ, start_response):

    our_type = extension_types['default']
    accept_header = environ.get('HTTP_ACCEPT')
    path_info = environ.get('PATH_INFO')

    if path_info:
        extension = path_info.rsplit('.', 1)
        if len(extension) == 2:
            our_type, ext = _calculate_type_from_extension(extension[-1])
            environ['tiddlyweb.extension'] = ext
    elif accept_header:
        our_type = _parse_accept_header(accept_header)

    environ['tiddlyweb.accept'] = our_type

def _calculate_type_from_extension(extension):
    try:
        return extension_types[extension], extension
    except KeyError:
        return extension_types['default'], None

def _parse_accept_header(header):
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
    return prefs[0]
