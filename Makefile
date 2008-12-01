
# Simple Makefile for some common tasks. This will get 
# fleshed out with time to make things easier on developer
# and tester types.
.PHONY: test dist upload

test: 
	py.test -x test

dist: test
	python setup.py sdist

upload: pypi peermore

pypi: test
	python setup.py sdist upload

peermore: test
	scp CHANGES dist/tiddlyweb-*.gz cdent@peermore.com:public_html/peermore.com/tiddlyweb/dist
