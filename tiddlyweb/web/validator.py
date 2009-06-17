"""
A collection of routines for validating,
santizing and otherwise messing with incoming
web content.
"""

import html5lib
from html5lib import sanitizer


class InvalidTiddlerError(Exception):
    pass


class InvalidBagError(Exception):
    pass


class InvalidRecipeError(Exception):
    pass


def sanitize_desc(entity, environ):
    """
    Strip any bad HTML which may be present in a description.
    """
    desc = entity.desc
    entity.desc = sanitize_html_fragment(desc)


BAG_VALIDATORS = [
        sanitize_desc,
        ]

TIDDLER_VALIDATORS = []

RECIPE_VALIDATORS = [
        sanitize_desc,
        ]



def validate_tiddler(tiddler, environ=None):
    _validate(tiddler, environ, TIDDLER_VALIDATORS)


def validate_bag(bag, environ=None):
    _validate(bag, environ, BAG_VALIDATORS)


def validate_recipe(recipe, environ=None):
    _validate(recipe, environ, RECIPE_VALIDATORS)


def _validate(entity, environ, validators):
    if environ is None:
        environ={}

    for validator in validators:
        validator(entity, environ)


def sanitize_html_fragment(fragment):
    """
    Santize an html fragment, returning a copy of the fragment,
    cleaned up.
    """
    p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
    output = p.parseFragment(fragment)
    return output.toxml()
