
# Simple Makefile for some common tasks. This will get 
# fleshed out with time to make things easier on developer
# and tester types.
.PHONY: test dist upload

clean:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true

cleanagain:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true

test: 
	py.test -x test

dist: test
	python setup.py sdist

upload: clean test cleanagain pypi peermore

pypi:
	python setup.py sdist upload

peermore:
	scp dist/tiddlyweb-*.gz cdent@peermore.com:public_html/peermore.com/tiddlyweb/dist
	scp CHANGES cdent@peermore.com:public_html/peermore.com/tiddlyweb/dist/CHANGES.tiddlyweb
