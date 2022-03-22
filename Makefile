
.PHONY: test

test:
	./dev_env_init.sh
	. activate && pytest --doctest-modules -v

