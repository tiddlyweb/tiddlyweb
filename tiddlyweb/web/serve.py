
import os
import selector

def load_app(map, wrappers=None):
    return selector.Selector(mapfile=map)

def start_simple(filename, port):
    os.environ = {}
    from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
    httpd = WSGIServer(('', port), WSGIRequestHandler)
    httpd.set_app(load_app(filename))
    print "Serving HTTP on %s port %s ..." % httpd.socket.getsockname()
    httpd.serve_forever()

