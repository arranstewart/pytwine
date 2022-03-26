
.PHONY: test docs perl-test python-test clean docs-clean

SHELL=bash

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
	$(activate_env) && python3 -m pip install -e "$(abs_mkfile_dir)[docs]" && \
			cd $(abs_mkfile_dir)/docs && \
			rm -rf source/_autosummary && \
			make clean html

docs-clean:
	rm -rf $(abs_mkfile_dir)/docs/source/_autosummary $(abs_mkfile_dir)/docs/build

clean: docs-clean
	export GLOBIGNORE=".:.." && \
	files=`ls -d $(abs_mkfile_dir)/* | grep -v -E 'env|git$$'` && \
	junk=`find $$files -type d \( -name '.hypothesis' -o \
	             -name '__pycache__' -o \
	             -name '*.egg-info' -o \
	             -name '.pytest_cache' -o \
	             -name '.mypy_cache' \)` \
	          && \
	rm -rf $$junk


