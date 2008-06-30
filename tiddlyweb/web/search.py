"""
Make a query into the store to find some
tiddlers and list them in the interface.
"""

import cgi
from tiddlyweb.web.http import HTTP400
from tiddlyweb.bag import Bag
from tiddlyweb.auth import ForbiddenError, UserRequiredError
from tiddlyweb.web import util as web

def get(environ, start_response):
    try:
        request_info = cgi.parse_qs(environ['QUERY_STRING'])
        search_query = request_info['q'][0]
    except IndexError:
        raise HTTP400, 'query string required'
    except KeyError:
        raise HTTP400, 'query string required'
    
    store = environ['tiddlyweb.store']
    tiddlers = store.search(search_query)

    usersign = environ['tiddlyweb.usersign']

# naively check permissions on the tiddlers
# this means we go to the store multiple times
# to get the policy for the same bag over and over
# XXX we should improve this once it is working
# It's necessary to get the tiddler off the store
# in case we are doing wiki or atom outputs of the
# search.
    tmp_bag = Bag('tmp_bag', tmpbag=True, searchbag=True)
    for tiddler in tiddlers:
        bag = Bag(tiddler.bag)
        store.get(bag)
        try:
            bag.policy.allows(usersign, 'read')
            tmp_bag.add_tiddler(store.get(tiddler))
        except ForbiddenError:
            pass
        except UserRequiredError:
            pass

    return web.send_tiddlers(environ, start_response, tmp_bag)
