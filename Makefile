# simple Makefile for some common tasks
.PHONY: clean cleanagain test makebundle uploadbundle bundle dist upload pypi \
		py2app peermore tagv

clean:
	find . -name "*.pyc" |xargs rm || true
	rm -r dist || true
	rm -r build || true
	rm -r tiddlyweb.egg-info || true
	rm *.bundle || true
	rm -r *-bundle* || true

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
	rm *.bundle || true
	rm -r *-bundle* || true

test:
	py.test -x test

makebundle: clean dist
	# work around errors in pip when bundling a tarball by instead
	# bundling the thing at pypy
	#pip bundle tiddlyweb-`date +%F`.bundle dist/tiddlyweb*.tar.gz
	pip bundle tiddlyweb-`python setup.py --version`.bundle tiddlyweb

uploadbundle:
	scp -P 8022 *.bundle cdent@heavy.peermore.com:public_html/tiddlyweb.peermore.com/dist

bundle: clean dist makebundle uploadbundle

dist: test
	python setup.py sdist

upload: clean test cleanagain tagv pypi peermore

pypi:
	python setup.py sdist upload

py2app: clean
	python setup.py py2app

peermore:
	scp -P 8022 dist/tiddlyweb-*.gz cdent@heavy.peermore.com:public_html/tiddlyweb.peermore.com/dist
	scp -P 8022 CHANGES cdent@heavy.peermore.com:public_html/tiddlyweb.peermore.com/dist/CHANGES.tiddlyweb
