"""
A collection of routines for validating, santizing and otherwise messing
with content coming in from the web to be tiddlers, bags or recipes.

The validators can be extended by adding functions to the BAG_VALIDATORS,
RECIPE_VALIDATORS and TIDDLER_VALIDATORS. The functions take an
entity object, and an optional environ dict.
"""


class InvalidTiddlerError(Exception):
    """
    The provided tiddler has not passed a validation routine
    and has been rejected. The caller should stop processing
    and return an error to calling code or user-agent.
    """
    pass


class InvalidBagError(Exception):
    """
    The provided bag has not passed a validation routine
    and has been rejected. The caller should stop processing
    and return an error to calling code or user-agent.
    """
    pass


class InvalidRecipeError(Exception):
    """
    The provided recipe has not passed a validation routine
    and has been rejected. The caller should stop processing
    and return an error to calling code or user-agent.
    """
    pass


def sanitize_desc(entity, environ):
    """
    Strip any bad HTML which may be present in a
    bag or recipe description.
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
    """
    Pass the tiddler to each of the functions in
    TIDDLER_VALIDATORS, in order, either changing
    the content of the tiddler's attributes, or if
    some aspect of the tiddler can not be accepted
    raising InvalidTiddlerError.

    TIDDLER_VALIDATORS is an empty list which should
    be extended by TiddlyWeb administrators.

    validate_tiddler is called from web handlers,
    when the the accept constraint on the bag containing
    the tiddler does not pass.
    """
    _validate(tiddler, environ, TIDDLER_VALIDATORS)


def validate_bag(bag, environ=None):
    """
    Pass the bag to each of the functions in
    BAG_VALIDATORS, in order, either changing
    the content of the bags's attributes, or if
    some aspect of the bag can not be accepted
    raising InvalidBagError.

    BAG_VALIDATORS is an empty list which should
    be extended by TiddlyWeb administrators.

    validate_bag is called whenever a bag is PUT
    via the web.
    """
    _validate(bag, environ, BAG_VALIDATORS)


def validate_recipe(recipe, environ=None):
    """
    Pass the recipe to each of the functions in
    RECIPE_VALIDATORS, in order, either changing
    the content of the recipes's attributes, or if
    some aspect of the recipe can not be accepted
    raising InvalidRecipeError.

    RECIPE_VALIDATORS is an empty list which should
    be extended by TiddlyWeb administrators.

    validate_recipe is called whenever a recipe is PUT
    via the web.
    """
    _validate(recipe, environ, RECIPE_VALIDATORS)


def _validate(entity, environ, validators):
    """
    Validate the provided entity against the list of functions
    in validators.
    """
    if environ is None:
        environ = {}

    for validator in validators:
        validator(entity, environ)


def sanitize_html_fragment(fragment):
    """
    Santize an html fragment, returning a copy of the fragment,
    cleaned up.
    """
    import html5lib
    from html5lib import sanitizer

    parser = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
    output = parser.parseFragment(fragment)
    return output.toxml()
