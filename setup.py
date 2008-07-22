"""
XXX THIS DOESN'T WORK YET! XXX
"""
from distutils.core import setup
setup(name='tiddlyweb',
        version='0.2',
        description='A headless wiki RESTful datastore for TiddlyWiki',
        author='Chris Dent',
        author_email='cdent@peermore.com',
        packages=['tiddlyweb',],
        scripts=['manager',],
        )

