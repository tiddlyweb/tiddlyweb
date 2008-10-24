
test:
	py.test test

dist:
	python setup.py sdist

upload:
	scp dist/tiddlyweb-*.gz cdent@hot.burningchrome.com:public_html/peermore.com/tiddlyweb/dist
