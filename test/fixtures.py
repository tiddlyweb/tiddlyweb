"""
Data structures required for our testing.
"""

import sys
sys.path.append('.')
from tiddlyweb.bag import Bag

tiddlers = [
        {
            'name': 'TiddlerOne',
            'content': 'tiddler one content',
            'tags': ['tagone', 'tagtwo']
        },
        {
            'name': 'TiddlerTwo',
            'content': 'tiddler two content',
            'tags': []
        },
        {
            'name': 'TiddlerThree',
            'content': 'tiddler three content',
            'tags': ['tagone', 'tagthree']
        }
]

bagone = Bag(name='bagone')
bagone.add_tiddler(tiddlers[0])
bagtwo = Bag(name='bagtwo')
bagtwo.add_tiddler(tiddlers[1])
bagthree = Bag(name='bagthree')
bagthree.add_tiddler(tiddlers[2])
bagfour = Bag(name='bagfour')
bagfour.add_tiddler(tiddlers[0])
bagfour.add_tiddler(tiddlers[1])
bagfour.add_tiddler(tiddlers[2])
