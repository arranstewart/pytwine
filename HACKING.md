
# Hacking on the source code

Recommended setup: create a venv directory, and activate it.

```
$ python3 -m venv env
$ . env/bin/activate
```

Then to install test dependencies and run pure Python tests:

```
$ python3 -m pip install -e ".[test]"
$ pytest pytwine tests
```

(Alternatively, `make test-python` should do all this and a bit more.)

##  Acceptance test prerequisites

The repository contains a number of Perl-based tests which install
and run pytwine in a temporary directory.

(Why Perl? It's a nicer "shell replacement" than either Powershell
or Python, and provides the original implementation of [TAP][tap],
the "Test Anything Protocol".)

[tap]: https://testanything.org/tap-specification.html

To run these tests, you'll need a version of Perl 5 installed, and the CPAN
libraries `Test::Harness` (which provides the `prove` command)
and `Carp::Assert`.

On Windows, if you have Chocolatey installed, you can install these with:

```
choco install strawberryperl
curl -L https://cpanmin.us | perl - --sudo App::cpanminus
cpanm Carp::Assert;
cpanm Test::Harness;
```

On Debian or Ubuntu, you probably have Perl installed already;
but you can install these with:

```
$ sudo apt-get install libcarp-assert-perl
```

Run the acceptance tests with

```
$ prove --verbose --comments t/*.t
```

(Alternatively, `make test-perl` will also run an appropriate
`prove` command, if you've got the prerequisites installed.)

## Getting help on `make` targets

Run

`make help`

## "out-of-source" tests

The Makefile should allow for "out-of-source" tests; you can `cd`
to some other directory, run `make -f /path/to/Makefile test`, and
it should still work. (Probably.)


