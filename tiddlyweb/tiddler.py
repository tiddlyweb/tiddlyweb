"""
A class and other thingies for a Tiddler.
"""

class Tiddler(object):

    def __init__(self, name=None, author=None, content=None, tags=[]):
        self.name = name
        self.author = author
        self.content = content
        self.tags = tags

    def __repr__(self):
        """
        Include the name of the tiddler in the repr.
        This is nice for debugging.
        """
        return self.name + object.__repr__(self)

