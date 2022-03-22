#!/usr/bin/env bash

# tests whether we can use `pip install` to install from
# a github branch.

# takes one arg, a branch to use (else uses "master" as default)

# if it finds the variable PERSONAL_TOKEN defined, it uses that as a token
# to get to github; else if looks for a file TOKEN in the working dir;
# else it does no authentication.

set -eo pipefail

if (( $# > 1 )); then
  printf 'expected 0 or 1 args (branch name, got %d\n' "$#"
  exit 1
fi

if (( $# == 1 )); then
  branch="$1"
else
  branch='master'
fi

if [ -n "$PERSONAL_TOKEN" ] ; then
  echo "using github personal token"
  token="$PERSONAL_TOKEN"
  declare -a auth_opts=("-H" "Authorization: Bearer $token")
elif [ -f TOKEN ]; then
  echo "using token file"
  token=$(cat TOKEN)
  declare -a auth_opts=("-H" "Authorization: token $token")
fi

repo=https://github.com/arranstewart/pytwine

path=archive/refs/heads/${branch}.zip
url="${repo}/${path}"

tmpdir=$(mktemp -d --tmpdir pytwine-zip-install-tmp-XXXXXXXXXX)

set -x
curl -L --fail "${auth_opts[@]}" "$url" > $tmpdir/pytwine.zip

unzip -t $tmpdir/pytwine.zip

# just to ensure we don't pick up anything in local dir
cd $tmpdir

python3 -m pip install file://$tmpdir/pytwine.zip

pytwine --help

