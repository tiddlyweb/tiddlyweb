from tiddlyweb.web.http import HTTP415

def get_serialize_type(environ, serializers):
    accept = environ.get('tiddlyweb.accept')[:]
    ext = environ.get('tiddlyweb.extension')
    serialize_type, mime_type = None, None

    while len(accept) and serialize_type == None:
        type = accept.pop()
        try:
            serialize_type, mime_type = serializers[type]
        except KeyError:
            pass
    if not serialize_type:
        if ext:
            raise HTTP415, '%s type unsupported' % ext
        serialize_type, mime_type = serializers['default']
    return serialize_type, mime_type
