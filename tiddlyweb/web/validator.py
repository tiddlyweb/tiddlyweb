"""
A collection of routines for validating,
santizing and otherwise messing with incoming
web content.
"""

class InvalidTiddlerError(Exception):
    pass

TIDDLER_VALIDATORS = []

def validate_tiddler(tiddler, environ=None):
    if environ is None:
        environ={}

    for validator in TIDDLER_VALIDATORS:
        validator(tiddler, environ)



