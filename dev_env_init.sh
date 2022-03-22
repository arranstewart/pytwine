#!/usr/bin/env bash

# takes 1 option arg, directory for python source code.
# (else assumes current dir)

if (( $# > 1 )); then
  printf >2 "bad no. of args, expected optional PYTHON_SRC_DIR\n"
  exit 1
fi

if (( $# < 1 )); then
  src_dir="."
else
  src_dir="$1"
fi

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
python3 -m pip install -e "${src_dir}[test]"

