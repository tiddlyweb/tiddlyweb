"""
Collection classes.
"""

from tiddlyweb.util import sha

class Collection(object):

    def __init__(self):
        self._digest = sha()
        self.modified = 0
        self._container = []

    def __contains__(self, item):
        return item in self._container

    def add(self, thing):
        self._update_digest(thing)
        self._container.append(thing)
        try:
            modified = thing.modified
            if modified > self.modified:
                self.modified = modified
        except AttributeError:
            pass

    def _update_digest(self, thing):
        self._digest.update(thing)

    def hexdigest(self):
        return self._digest.hexdigest()

    def out(self):
        for thing in self._container:
            yield thing

class Tiddlers(Collection):

    def _update_digest(self, tiddler):
        if tiddler.recipe:
            container = tiddler.recipe
        elif tiddler.bag:
            container = tiddler.bag
        else:
            container = ''
        self._digest.update(container.encode('utf-8'))
        self._digest.update(tiddler.title.encode('utf-8'))
