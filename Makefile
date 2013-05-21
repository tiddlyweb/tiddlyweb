# simple Makefile for some common tasks
.PHONY: clean cleanagain test dist release pypi peermore tagv

clean:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true
	rm -r build || true
	rm -r tiddlyweb.egg-info || true

tagv:
	git tag -a \
		-m v`python -c 'import tiddlyweb; print tiddlyweb.__version__'` \
		v`python -c 'import tiddlyweb; print tiddlyweb.__version__'`
	git push origin master --tags

cleanagain:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true
	rm -r build || true
	rm -r tiddlyweb.egg-info || true

test:
	py.test -x --tb=short test

dist: test
	python setup.py sdist

release: clean test cleanagain tagv pypi peermore

pypi:
	python setup.py sdist upload

peermore:
	scp -P 8022 dist/tiddlyweb-*.gz cdent@heavy.peermore.com:public_html/tiddlyweb.peermore.com/dist
	scp -P 8022 CHANGES cdent@heavy.peermore.com:public_html/tiddlyweb.peermore.com/dist/CHANGES.tiddlyweb
