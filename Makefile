
# Simple Makefile for some common tasks. This will get 
# fleshed out with time to make things easier on developer
# and tester types.
.PHONY: test dist upload

clean:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true
	rm -r build || true
	rm -r tiddlyweb.egg-info || true
	rm *.bundle || true

cleanagain:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true
	rm -r build || true
	rm -r tiddlyweb.egg-info || true
	rm *.bundle || true

test: 
	py.test -x test

makebundle: clean dist
	pip bundle tiddlyweb-`date +%F`.bundle dist/tiddlyweb*.tar.gz

uploadbundle:
	scp -P 8022 *.bundle cdent@heavy.peermore.com:public_html/tiddlyweb.peermore.com/dist

bundle: clean dist makebundle uploadbundle

dist: test
	python setup.py sdist

upload: clean test cleanagain pypi peermore

pypi:
	python setup.py sdist upload

peermore:
	scp -P 8022 dist/tiddlyweb-*.gz cdent@heavy.peermore.com:public_html/tiddlyweb.peermore.com/dist
	scp -P 8022 CHANGES cdent@heavy.peermore.com:public_html/tiddlyweb.peermore.com/dist/CHANGES.tiddlyweb
