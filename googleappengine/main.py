#!/usr/bin/env python

# TiddlyWeb start for GoogleAppEngine.
#
# Note that TiddlyWeb itself is advancing at a faster rate
# than the adaptation of TiddlyWeb to GoogleAppEngine. This
# code may need adjustments.
#
# Based on example code that came from Google with the following
# header:
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import wsgiref.handlers
import urllib

from tiddlyweb.web.serve import load_app, config
from tiddlyweb.web.wsgi import SimpleLog


class ScriptCleanup(object):

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        environ['PATH_INFO'] = urllib.unquote(environ['PATH_INFO'])
        return self.application(environ, start_response)

app = None


def google_app():
    """
    Only calculate the app once, otherwise we recalculate the
    config settings with every request, which is not happy.
    """
    global app
    if app:
        return app

    host = 'tiddlyweb.appspot.com'
    port = 80
    #host = 'localhost'
    #port = 8000
    filename = config['urls_map']

    filters_in = config['server_request_filters']
    filters_in.insert(0, ScriptCleanup)

    filters_out = config['server_response_filters']
    try:
        filters_out.remove(SimpleLog)
    except ValueError:
        pass # it wasn't in there

    app = load_app(host, port, filename)
    return app


def main():
    wsgiref.handlers.CGIHandler().run(google_app())

if __name__ == '__main__':
    main()
