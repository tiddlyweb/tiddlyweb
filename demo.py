
import os

from tiddlyweb.manage import server

store_name = 'store'
real_store = 'docstore'

def go():
    try: 
        os.symlink(real_store, store_name)
    except OSError:
        print 'symlink failed, continuing'
    try:
        server(['0.0.0.0', '8080'])
    except KeyboardInterrupt:
        print 'shutting down'
    os.unlink(store_name)

if __name__ == '__main__':
    go()
