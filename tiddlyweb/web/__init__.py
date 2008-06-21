"""
Convenience routines for presenting the root of
the web server. There are probably better places
for this.
"""

root_page = """<html>
<head>
<title>TiddlyWeb</title>
</head>
<body>
<ul>
<li><a href="recipes">recipes</a></li>
<li><a href="bags">bags</a></li>
</ul>
<body>
</html>"""

def root(environ, start_response):
    """
    Convenience method to provide an entry point at root.
    """

    start_response("200 OK", [('Content-Type', 'text/html; charset=UTF-8')])
    return [root_page]


