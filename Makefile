
.PHONY: test docs

test:
	./dev_env_init.sh
	. ./activate && pytest --doctest-modules -v

docs:
	./dev_env_init.sh
	. ./activate && pip install sphinx
	. ./activate && sphinx-apidoc -o docs/source pytwine
	. ./activate && cd docs && make clean html

