
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
and run pytwine in a temporary directory and emit
results in format expected by [TAP][tap] (the "Test Anything Protocol".)

[tap]: https://testanything.org/tap-specification.html

To run these tests, you'll need a version of Perl 5 installed, and the CPAN
libraries `Test::Harness` (which provides the `prove` command),
`Carp::Assert`. and `File::Which`.

On Windows, if you have Chocolatey installed, you can install these with:

```
choco install strawberryperl
curl -L https://cpanmin.us | perl - --sudo App::cpanminus
cpanm Carp::Assert;
cpanm Test::Harness;
cpanm File::Which;
```

On Debian or Ubuntu, you probably have Perl installed already;
and you can install the extra libraries with:

```
$ sudo apt-get install libcarp-assert-perl libfile-which-perl
```

(On MacOS, I have no idea what the appropriate commands are, but they
probably involve using `brew`.)

Run the acceptance tests with `make test-perl`.

## Getting help on `make` targets

Run

`make help`

## "out-of-source" tests

The Makefile should allow for "out-of-source" tests; you can `cd`
to some other directory, run `make -f /path/to/Makefile test`, and
it should still work. (Probably.)


