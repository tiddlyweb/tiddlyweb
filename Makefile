
# Simple Makefile for some common tasks. This will get 
# fleshed out with time to make things easier on developer
# and tester types.
.PHONY: test dist upload

test: 
	py.test test

dist:
	python setup.py sdist

upload:
	scp dist/tiddlyweb-*.gz cdent@hot.burningchrome.com:public_html/peermore.com/tiddlyweb/dist
