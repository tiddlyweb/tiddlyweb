"""
A collection of routines for validating, santizing and otherwise messing
with content coming in from the web to be :py:class:`tiddlers
<tiddlyweb.model.tiddler.Tidder>`, :py:class:`bags
<tiddlyweb.model.bag.Bag>` or :py:class:`recipes
<tiddlyweb.model.recipe.Recipe>`.

The validators can be extended by adding functions to the ``BAG_VALIDATORS``,
``RECIPE_VALIDATORS`` and ``TIDDLER_VALIDATORS``. The functions take an
entity object, and an optional WSGI ``environ`` dict.
"""


class InvalidTiddlerError(Exception):
    """
    The provided :py:class:`tiddler <tiddlyweb.model.tiddler.Tiddler>`
    has not passed a validation routine and has been rejected.
    The caller should stop processing and return an error to calling
    code or user-agent.
    """
    pass


class InvalidBagError(Exception):
    """
    The provided :py:class:`bag <tiddlyweb.model.bag.Bag>` has not passed
    a validation routine and has been rejected. The caller should stop
    processing and return an error to calling code or user-agent.
    """
    pass


class InvalidRecipeError(Exception):
    """
    The provided :py:class:`recipe <tiddlyweb.model.recipe.Recipe>` has
    not passed a validation routine and has been rejected. The caller
    should stop processing and return an error to calling code or
    user-agent.
    """
    pass


def sanitize_desc(entity, environ):
    """
    Strip any dangerous HTML which may be present in a :py:class:`bag
    <tiddlyweb.model.bag.Bag>` or :py:class:`recipe
    <tiddlyweb.model.recipe.Recipe>` description.
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
    Pass the :py:class:`tiddler <tiddlyweb.model.tiddler.Tiddler>`
    to each of the functions in ``TIDDLER_VALIDATORS``, in order,
    either changing the content of the tiddler's attributes, or if
    some aspect of the tiddler can not be accepted raising
    :py:class:`InvalidTiddlerError`.

    ``TIDDLER_VALIDATORS`` is an empty list which may be extended
    by plugins.

    ``validate_tiddler`` is called from :py:mod:`web handlers
    <tiddlyweb.web.handler>`, when the ``accept`` constraint on
    the :py:class:`policy <tiddlyweb.model.policy.Policy>` of the
    :py:class:`bag <tiddlyweb.model.bag.Bag>` containing the
    tiddler does not pass.
    """
    _validate(tiddler, environ, TIDDLER_VALIDATORS)


def validate_bag(bag, environ=None):
    """
    Pass the :py:class:`bag <tiddlyweb.model.bag.Bag>` to each of
    the functions in ``BAG_VALIDATORS``, in order, either changing
    the content of the bags's attributes, or if some aspect of the
    bag can not be accepted raising :py:class:`InvalidBagError`.

    ``BAG_VALIDATORS`` may be extended by plugins.

    ``validate_bag`` is called whenever a bag is ``PUT`` via HTTP.
    """
    _validate(bag, environ, BAG_VALIDATORS)


def validate_recipe(recipe, environ=None):
    """
    Pass the :py:class:`recipe <tiddlyweb.model.recipe.Recipe>` to
    each of the functions in ``RECIPE_VALIDATORS``, in order, either
    changing the content of the recipes's attributes, or if some aspect
    of the recipe can not be accepted raising :py:class:`InvalidRecipeError`.

    ``RECIPE_VALIDATORS`` may be extended by plugins.

    ``validate_recipe`` is called whenever a recipe is ``PUT`` via HTTP.
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
    Santize an HTML ``fragment``, returning a copy of the fragment
    that has been cleaned up.
    """
    if fragment:
        import html5lib
        from html5lib.sanitizer import HTMLSanitizer
        from html5lib.serializer.htmlserializer import HTMLSerializer

        parser = html5lib.HTMLParser(tokenizer=HTMLSanitizer)
        parsed = parser.parseFragment(fragment)
        walker = html5lib.treewalkers.getTreeWalker('etree')
        stream = walker(parsed)
        serializer = HTMLSerializer(quote_attr_values=True,
                omit_optional_tags=False)
        output = serializer.render(stream)
        return output
    else:
        return fragment
