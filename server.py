
from tiddlyweb.web import serve

def start():
    serve.start_simple('./urls.map', 8080)

if __name__ == '__main__':
    start()
