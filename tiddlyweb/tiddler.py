"""
A class and other thingies for a Tiddler.
"""

class Tiddler(object):

    def __init__(self, name=None, author=None, content=None, tags=[]):
        self.name = name
        self.author = author
        self.content = content
        self.tags = tags
