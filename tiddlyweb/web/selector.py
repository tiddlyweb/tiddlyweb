"""selector - WSGI handler delegation. (AKA routing.)"""

"""
This code is a port (to python3) of Luke Arno's selector:

    https://github.com/lukearno/selector/

included here temporarily until a full port is complete.
"""

import re

from itertools import starmap
from wsgiref.util import shift_path_info

import resolver


class MappingFileError(Exception):
    """Raised to signal a syntax error in a mapping file."""


class PathExpressionParserError(Exception):
    """Raised to signal a syntax error in a path expression."""


def method_not_allowed(environ, start_response):
    """Default WSGI 405 app."""
    start_response("405 Method Not Allowed",
                   [('Allow', ', '.join(environ['selector.methods'])),
                    ('Content-Type', 'text/plain')])
    return ["405 Method Not Allowed\n\n"
            "The method specified in the Request-Line is not allowed "
            "for the resource identified by the Request-URI."]


def not_found(environ, start_response):
    """Default WSGI 404 app."""
    start_response("404 Not Found", [('Content-Type', 'text/plain')])
    return ["404 Not Found\n\n"
            "The server has not found anything matching the Request-URI."]


class Selector(object):
    """WSGI middleware for URL paths and HTTP method based delegation."""

    status405 = staticmethod(method_not_allowed)
    status404 = staticmethod(not_found)

    def __init__(self,
                 mappings=None,
                 prefix="",
                 parser=None,
                 wrap=None,
                 mapfile=None,
                 consume_path=True):
        """Initialize selector."""
        self.mappings = []
        self.prefix = prefix
        if parser is None:
            self.parser = SimpleParser()
        else:
            self.parser = parser
        self.wrap = wrap
        if mapfile is not None:
            self.slurp_file(mapfile)
        if mappings is not None:
            self.slurp(mappings)
        self.consume_path = consume_path

    def slurp(self, mappings, prefix=None, parser=None, wrap=None):
        """Slurp in a whole list (or any iterable) of mappings.

        Mappings take the form of

        .. code-block:: python

            (PATH_EXPRESSION, HTTP_METHOD_TO_WSGI_APP_DICT)

        """
        if prefix is not None:
            oldprefix = self.prefix
            self.prefix = prefix
        if parser is not None:
            oldparser = self.parser
            self.parser = parser
        if wrap is not None:
            oldwrap = self.wrap
            self.wrap = wrap
        list(starmap(self.add, mappings))
        if wrap is not None:
            self.wrap = oldwrap
        if parser is not None:
            self.parser = oldparser
        if prefix is not None:
            self.prefix = oldprefix

    def add(self, path, method_dict=None, prefix=None, **http_methods):
        """Add a mapping.

        HTTP methods can be specified in a dict or using key word args,
        but kwargs will override if both are given.
        """
        # Thanks to Sebastien Pierre
        # for suggesting that this accept keyword args.
        if method_dict is None:
            method_dict = {}
        if prefix is None:
            prefix = self.prefix
        method_dict = dict(method_dict)
        method_dict.update(http_methods)
        if self.wrap is not None:
            for meth, cbl in list(method_dict.items()):
                method_dict[meth] = self.wrap(cbl)
        regex = self.parser(prefix + path)
        compiled_regex = re.compile(regex)
        mapping = (compiled_regex, method_dict)
        self.mappings.append(mapping)
        return mapping

    def __call__(self, environ, start_response):
        """Delegate request to the appropriate WSGI app."""
        app, svars, methods, matched = \
            self.select(environ['PATH_INFO'], environ['REQUEST_METHOD'])
        unnamed, named = [], {}
        for k, v in svars.items():
            if k.startswith('__pos'):
                k = k[5:]
            named[k] = v
        environ['selector.vars'] = dict(named)
        for k in list(named.keys()):
            if k.isdigit():
                unnamed.append((k, named.pop(k)))
        unnamed.sort()
        unnamed = [v for k, v in unnamed]
        cur_unnamed, cur_named = environ.get('wsgiorg.routing_args', ([], {}))
        unnamed = cur_unnamed + unnamed
        named.update(cur_named)
        environ['wsgiorg.routing_args'] = unnamed, named
        environ['selector.methods'] = methods
        environ.setdefault('selector.matches', []).append(matched)
        if self.consume_path:
            environ['SCRIPT_NAME'] = environ.get('SCRIPT_NAME', '') + matched
            environ['PATH_INFO'] = environ['PATH_INFO'][len(matched):]
        return app(environ, start_response)

    def select(self, path, method):
        """Figure out which app to delegate to or send 404 or 405.

        """
        for regex, method_dict in self.mappings:
            match = regex.search(path)
            if match:
                methods = list(method_dict.keys())
                if method in method_dict:
                    return (method_dict[method],
                            match.groupdict(),
                            methods,
                            match.group(0))
                elif '_ANY_' in method_dict:
                    return (method_dict['_ANY_'],
                            match.groupdict(),
                            methods,
                            match.group(0))
                else:
                    return self.status405, {}, methods, ''
        return self.status404, {}, [], ''

    def slurp_file(self, filename, prefix=None, parser=None, wrap=None):
        """Read mappings from a simple text file. (See README.md.)"""
        with open(filename, 'rb') as the_file:
            oldprefix = self.prefix
            if prefix is not None:
                self.prefix = prefix
            oldparser = self.parser
            if parser is not None:
                self.parser = parser
            oldwrap = self.wrap
            if parser is not None:
                self.wrap = wrap
            path = methods = None
            lineno = 0
            try:
                try:
                    for line in the_file:
                        line = line.decode()
                        lineno += 1
                        path, methods = self._parse_line(line, path, methods)
                    if path and methods:
                        self.add(path, methods)
                except MappingFileError as mfe:
                    raise MappingFileError("line %s: %s" % (lineno, mfe))
            finally:
                self.wrap = oldwrap
                self.parser = oldparser
                self.prefix = oldprefix

    def _parse_line(self, line, path, methods):
        """Parse one line of a mapping file.

        This method is for the use of selector.slurp_file.
        """
        # Comment or line:
        if not line.strip() or line.strip()[0] == '#':
            pass
        # Directive:
        elif line.strip()[0] == '@':
            parts = line.strip()[1:].split(' ', 1)
            if len(parts) == 2:
                directive, rest = parts
            else:
                directive = parts[0]
                rest = ''
            if directive == 'prefix':
                self.prefix = rest.strip()
            if directive == 'parser':
                self.parser = resolver.resolve(rest.strip())
            if directive == 'wrap':
                self.wrap = resolver.resolve(rest.strip())
        # HTTP Method -> Handler:
        elif line[0] in ' \t':
            if path is None:
                raise MappingFileError(
                    "Specify a path expression first.")
            meth, app = line.strip().split(' ', 1)
            methods[meth.strip()] = resolver.resolve(app)
        # Path Expression:
        else:
            if path and methods:
                self.add(path, methods)
            path = line.strip()
            methods = {}
        return path, methods


class SimpleParser(object):
    """Callable to turn path expressions into regexes with named groups.

    .. code-block:: python

        SimpleParser()("/hello/{name}") == r"^\/hello\/(?P<name>[^\^.]+)$"

    See README.md for details.
    """

    start, end = '{}'
    ostart, oend = '[]'
    _patterns = {'word': r'\w+',
                 'alpha': r'[a-zA-Z]+',
                 'digits': r'\d+',
                 'number': r'\d*.?\d+',
                 'chunk': r'[^/^.]+',
                 'segment': r'[^/]+',
                 'any': r'.+'}
    default_pattern = 'chunk'

    def __init__(self, patterns=None):
        """Initialize with character class mappings."""
        self.patterns = dict(self._patterns)
        if patterns is not None:
            self.patterns.update(patterns)

    def _lookup(self, name):
        """Return the replacement for the name found."""
        if ':' in name:
            name, pattern = name.split(':')
            pattern = self.patterns[pattern]
        else:
            pattern = self.patterns[self.default_pattern]
        if name == '':
            name = '__pos%s' % self._pos
            self._pos += 1
        return '(?P<%s>%s)' % (name, pattern)

    def _lastly(self, regex):
        """Process the result of __call__ right before it returns.

        Adds the ^ and the $ to the beginning and the end, respectively.
        """
        return "^%s$" % regex

    def _openended(self, regex):
        """Process the result of __call__ right before it returns.

        Adds the ^ to the beginning but no $ to the end.
        Called as a special alternative to _lastly.
        """
        return "^%s" % regex

    def _outermost_optionals_split(self, text):
        """Split out optional portions by outermost matching delims."""
        parts = []
        buffer = ""
        starts = ends = 0
        for c in text:
            if c == self.ostart:
                if starts == 0:
                    parts.append(buffer)
                    buffer = ""
                else:
                    buffer += c
                starts += 1
            elif c == self.oend:
                ends += 1
                if starts == ends:
                    parts.append(buffer)
                    buffer = ""
                    starts = ends = 0
                else:
                    buffer += c
            else:
                buffer += c
        if not starts == ends == 0:
            raise PathExpressionParserError(
                "Mismatch of optional portion delimiters."
            )
        parts.append(buffer)
        return parts

    def _parse(self, text):
        """Turn a path expression into regex."""
        if self.ostart in text:
            parts = self._outermost_optionals_split(text)
            parts = list(map(self._parse, parts))
            parts[1::2] = ["(%s)?" % p for p in parts[1::2]]
        else:
            parts = [part.split(self.end)
                     for part in text.split(self.start)]
            parts = [y for x in parts for y in x]
            parts[::2] = list(map(re.escape, parts[::2]))
            parts[1::2] = list(map(self._lookup, parts[1::2]))
        return ''.join(parts)

    def __call__(self, url_pattern):
        """Turn a path expression into a regex."""
        self._pos = 0
        if url_pattern.endswith('|'):
            return self._openended(self._parse(url_pattern[:-1]))
        else:
            return self._lastly(self._parse(url_pattern))


class EnvironDispatcher(object):
    """Dispatch based on list of rules."""

    def __init__(self, rules):
        """Instantiate with a list of (predicate, wsgiapp) rules."""
        self.rules = rules

    def __call__(self, environ, start_response):
        """Call the first app whose predicate is true.

        Each predicate is passes the environ to evaluate.
        """
        for predicate, app in self.rules:
            if predicate(environ):
                return app(environ, start_response)


class MiddlewareComposer(object):
    """Compose middleware based on list of rules."""

    def __init__(self, app, rules):
        """Instantiate with an app and a list of rules."""
        self.app = app
        self.rules = rules

    def __call__(self, environ, start_response):
        """Apply each middleware whose predicate is true.

        Each predicate is passes the environ to evaluate.

        Given this set of rules:

        t = lambda x: True; f = lambda x: False
        [(t, a), (f, b), (t, c), (f, d), (t, e)]

        The app composed would be equivalent to this:

        a(c(e(app)))
        """
        app = self.app
        for predicate, middleware in reversed(self.rules):
            if predicate(environ):
                app = middleware(app)
        return app(environ, start_response)


def expose(obj):
    """Set obj._exposed = True and return obj."""
    obj._exposed = True
    return obj


class Naked(object):
    """Naked object style dispatch base class."""

    _not_found = staticmethod(not_found)
    _expose_all = True
    _exposed = True

    def _is_exposed(self, obj):
        """Determine if obj should be exposed.

        If self._expose_all is True, always return True.
        Otherwise, look at obj._exposed.
        """
        return self._expose_all or getattr(obj, '_exposed', False)

    def __call__(self, environ, start_response):
        """Dispatch to the method named by the next bit of PATH_INFO."""
        # Predict the path shift to get the callable name.
        name = shift_path_info(dict(SCRIPT_NAME=environ['SCRIPT_NAME'],
                                    PATH_INFO=environ['PATH_INFO']))
        # If there is such a callable and it is exposed...
        callable = getattr(self, name or 'index', None)
        if callable is not None and self._is_exposed(callable):
            # ... shift the path and call the callable.
            shift_path_info(environ)
            return callable(environ, start_response)
        else:
            # ... or call self._not_found (
            return self._not_found(environ, start_response)


class ByMethod(object):
    """Base class for dispatching to method named by REQUEST_METHOD."""

    _method_not_allowed = staticmethod(method_not_allowed)

    def __call__(self, environ, start_response):
        """Dispatch based on REQUEST_METHOD."""
        environ['selector.methods'] = \
            [m for m in dir(self) if not m.startswith('_')]
        return getattr(self,
                       environ['REQUEST_METHOD'],
                       self._method_not_allowed)(environ, start_response)


def pliant(func):
    """Decorate an unbound wsgi callable taking args from wsgiorg.routing_args.

    .. code-block:: python

        @pliant
        def app(environ, start_response, arg1, arg2, foo='bar'):
            ...
    """
    def wsgi_func(environ, start_response):
        args, kwargs = environ.get('wsgiorg.routing_args', ([], {}))
        args = list(args)
        args.insert(0, start_response)
        args.insert(0, environ)
        return func(*args, **dict(kwargs))
    return wsgi_func


def opliant(meth):
    """Decorate a bound wsgi callable taking args from wsgiorg.routing_args.

    .. code-block:: python

        class App(object):
            @opliant
            def __call__(self, environ, start_response, arg1, arg2, foo='bar'):
                ...
    """
    def wsgi_meth(self, environ, start_response):
        args, kwargs = environ.get('wsgiorg.routing_args', ([], {}))
        args = list(args)
        args.insert(0, start_response)
        args.insert(0, environ)
        args.insert(0, self)
        return meth(*args, **dict(kwargs))
    return wsgi_meth
