
This branch is experimenting with adding a suite of
[Gabbi](http://gabbi.readthedocs.org/) tests to TiddlyWeb. For now the
work is being done here within the TiddlyWeb source tree, but eventually
it ought to be possible to remove this to its own tree to become a tool
to validate TiddlyWeb API servers (that is, services which present a
TiddlyWeb API but are not the original Python implementation).

It's not there yet. In fact at the moment it intercepts the TiddlyWeb WSGI
app and uses the server-side API to create content. This is simply to flesh
out and explore the concept.

If you want to play with it:

* checkout this branch

    git clone -b gabbi https://github.com/tiddlyweb/tiddlyweb.git

* install gabbi and testrepository (feel free to use a virtualenv)

    pip install -U gabbi testrepository

* run the gabbi tests

    make gabbi

The test loader is at `gabbitests/test_tiddlyweb.py`. The actual tests
are in the YAML files in `gabbitests/gabbits`.

The tests use a fixture in `gabbitests/fixtures.py` to run each YAML file
with its own TiddlyWeb instance (and thus store), created in a temporary
directory in `$TMPDIR`. This will get cleaned up after each test run unless
you set TIDDLYWEB_TEST_PRESERVE in the environment.

The tests are run from the `Makefile` with a command called `testr`. If you
are not familiar with testrepository you'll be forgiven for responding to it
with a "WTF?". It takes a lot of getting used to. The reason it is being used
here is that it makes it easy to run the tests concurrently and if the point
of your test run is to validate something (rather than build something) this
is very useful.

The first "WTF" is likely "Where is the output of my test run?". This
has been saved for you as what's called a subunit stream in a directory
named `.testrepository`. This keeps a history of tests runs which allows
you to make comparisons and do fun things like rerun a previous run but
only those tests which failed.

You probably just want to see the output. To get that you can do:

    testr last --subunit |subunit2pyunit

Other useful commands for the RHS of the pipe include: `subunit-stats`,
`subunit-ls`, `subunit2csv`.

If you want to run just one or some of the tests you can pass a pattern
as an argument to the `testr run` command, for example:

    testr run --parallel base

If you'd like to have a more interactive experience with the output
of the tests then you can skip testr and use some other testrunner
that supports the PyUnit test discovery process. Some examples:

    python -m subunit.run discover -t . gabbitests |subunit2pyunit

    python -m testtools.run discover -t . gabbitests

    python -m unittest discover -t . gabbitests.test_tiddlyweb

The `discover` is required to engage the dymamic `load_tests` protocol.
The `-t .` ensures that necessary libraries (the ones being tested) can
be found.

I've done some extensive experiments to see if I can get this to work
with py.test, using the powerful collection, running, and reporting
hooks in py.test. So far I have not been able to get it to work, I think
because I'm using `TestSuite` level fixtures.
