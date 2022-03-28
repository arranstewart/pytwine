#!/usr/bin/env bash

# initialize a virtual env and some minimal
# packages and symlinks

set -euo pipefail

if [ ! -d env ] ; then
  python3 -m venv env
fi

if [ ! -L activate ]; then
  ln -s env/bin/activate ./activate
fi
. ./activate

set -x
python3 -m pip install --upgrade pip wheel pip-tools

