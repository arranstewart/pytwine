
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

To run tests:

```
$ pytest -v --doctest-modules
```

(Or, `make test` will also do all the above.)
