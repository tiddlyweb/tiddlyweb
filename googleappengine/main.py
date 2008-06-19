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


from tiddlyweb.web.serve import load_app, StoreSet, EncodeUTF8, UserExtract, Configurator
from tiddlyweb.auth import PermissionsExceptor
from tiddlyweb.web.negotiate import Negotiate
from tiddlyweb.web.http import HTTPExceptor

import wsgiref.handlers

def google_app():
    host = 'tiddlyweb.appspot.com'
    port = 80
    #host = 'localhost'
    #port = 8000
    filename = 'urls.map'
    server_store = 'googledata'
    return load_app(host, port, server_store, filename, [
        Negotiate, UserExtract, StoreSet, Configurator, PermissionsExceptor, HTTPExceptor, EncodeUTF8
        ])

def main():
  wsgiref.handlers.CGIHandler().run(google_app())

if __name__ == '__main__':
  main()

