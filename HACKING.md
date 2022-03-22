
# Hacking on the source code

Recommended setup: create a venv directory, and activate it.

```
$ python3 -m venv env
$ . env/bin/activate
```

Then to install test dependencies,

```
$ python3 -m pip install -e ".[test]"
```

## run tests

To run Python-based tests:

```
$ pytest -v --doctest-modules
```

(Or, `make test` will also do all the above.)

Other tests are written using Perl, and can be run
with

```
$ prove --verbose --comments t/*.t
```

# "out-of-source" tests

The Makefile should allow for "out-of-source" tests; you can cd
to some other directory, run `make -f /path/to/Makefile test`, and
it should still work.




