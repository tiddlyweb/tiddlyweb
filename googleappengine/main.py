#!/usr/bin/env python

# TiddlyWeb start for GoogleAppEngine.
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


from tiddlyweb.web.serve import load_app, StoreSet, EncodeUTF8, UserExtract, Configurator, config
from tiddlyweb.auth import PermissionsExceptor
from tiddlyweb.web.negotiate import Negotiate
from tiddlyweb.web.http import HTTPExceptor

import wsgiref.handlers
import urllib

class ScriptCleanup(object):

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        environ['PATH_INFO'] = urllib.unquote(environ['PATH_INFO'])
        return self.application(environ, start_response)

def google_app():
    host = 'tiddlyweb.appspot.com'
    port = 80
    filename = 'urls.map'
    config['server_store'] = ['googledata', {}]
    config['extension_types']['atom'] = 'application/atom+xml'
    config['serializers']['application/atom+xml'] = ['atom.atom', 'application/atom+xml; charset=UTF-8']
    config['serializers']['text/html'] = ['atom.htmlatom', 'text/html; charset=UTF-8']
    app = load_app(host, port, filename, [
        Negotiate, UserExtract, StoreSet, Configurator, PermissionsExceptor, HTTPExceptor, EncodeUTF8
        ])
    return ScriptCleanup(app)

def main():
  wsgiref.handlers.CGIHandler().run(google_app())

if __name__ == '__main__':
  main()

