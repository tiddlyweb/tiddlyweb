"""
A class and other thingies for a Tiddler.
"""

from datetime import datetime

class Tiddler(object):
    """
    A proper tiddler has the follow attributes:
    title: the name of the tiddler
    modifier: the name of the thing that edited the tiddler
    modified: the last time it was edited
    created: the time it was created
    tags: the list of tags this tiddler has.

    XXX content is not content is text in the tiddlywiki, fix that.

    XXX: therefore the model below is wrong and needs a tuneup
    """

    def __init__(self,
            title=None,
            modifier=None,
            modified=datetime.utcnow(),
            created=datetime.utcnow(),
            tags=[],
            bag=None,
            content=None):
        self.title = title
        self.modifier = modifier
        self.modified = modified
        self.create = created
        self.tags = tags
        self.bag = bag
        self.content = content
        # reference to the store which 'got' us
        # this is can be used in serialization
        self.store = None

    def __repr__(self):
        """
        Include the name of the tiddler in the repr.
        This is nice for debugging.
        """
        return self.title + object.__repr__(self)

