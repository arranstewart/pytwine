
.PHONY: test docs perl-test python-test

# evaluate this _once_
abs_mkfile_dir :=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

create_env = if [ ! -e activate ]; then $(abs_mkfile_dir)/dev_env_init.sh $(abs_mkfile_dir); fi

activate_env = if [ -z "$$VIRTUAL_ENV" ]; then . ./activate; fi

# use like this:
# $(call create_tmpdir,testtype)
create_tmpdir=mktemp -d --tmpdir pytwine-$(1)-tmp-XXXXXXXXXX

python-test:
	$(create_env)
	$(activate_env) && pytest --doctest-modules -v $(abs_mkfile_dir)

perl-test:
		tmpdir=`$(call create_tmpdir,perltest)` && \
		cd $$tmpdir                             && \
		$(create_env)                           && \
		$(activate_env); set -x; prove --verbose --comments $(abs_mkfile_dir)/t/*.t || res=$$? && \
		rm -rf $$tmpdir && set +x && exit $$res

test: pyton-test perl-test

docs:
	$(create_env)
	$(activate_env) && pip install sphinx \
		&& sphinx-apidoc -o docs/source pytwine \
	 	&& cd docs && make clean html

