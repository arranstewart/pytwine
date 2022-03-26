#!/usr/bin/env python3
# pylint: skip-file

import sys
from subprocess import run, DEVNULL 
from pkg_resources import Distribution, PathMetadata

def main(src_dir):
  run(["python3", f"{src_dir}/setup.py", "egg_info"],
      check=True, stdout=DEVNULL)
  dist = Distribution(metadata=PathMetadata('pytwine.egg-info',
                        'pytwine.egg-info'))
  reqs = dist.requires(extras=["test"])
  reqs = [r.name for r in reqs] 
  print(" ".join(reqs))

if __name__ == "__main__":
  args = sys.argv[1:]
  if len(args) != 1:
    raise Exception("expectd 1 arg, path to src dir")
  src_dir = args[0]
  main(src_dir)


