#!/usr/bin/env python

"""setup script."""

import os
import sys
from setuptools import setup

setup_py_path = os.path.realpath(__file__)
setup_py_dir  = os.path.dirname(setup_py_path)
pytwine_dir   = os.path.join(setup_py_dir, "pytwine")

def get_version():
  """Get version.

  'source of truth' for the package version is
  the ``pytwine/_version.py`` file.
  """
  sys.path.append( pytwine_dir )
  # pylint: disable=all
  import _version # type: ignore
  return _version.__version__

def read(fname):
  "get contents of file from source dir"
  fpath = os.path.join(setup_py_dir, fname)
  with open(fpath, encoding="utf8") as ifp:
    return ifp.read()

setup_args = dict(
  name='pytwine',
  author='Arran D. Stewart',
  author_email='arran.stewart@uwa.edu.au',
  entry_points={
        'console_scripts': [
              # thin wrapper around pytwine.cli.cli_twine
              'pytwine = pytwine.scripts:pytwine_script'
            ] },
  version = get_version(),
  description='Reports with embedded python computations',
  url='https://github.com/arranstewart/pytwine',
  packages=['pytwine'],
  install_requires = ['markdown'],
  python_requires = '>=3.6',
  extras_require = {'test': [ \
                          'hypothesis',
                          'pytest',
                          'pytest-cov',
                          'pytest-html',
                          'pytest-tap',
                          ],
                      'docs': [ \
                          'sphinx >= 4.0',
                          'myst-parser'
                          ]
                     },
  license='LICENSE',
  long_description = read('README.md'),
  classifiers=[
      'Development Status :: 1 - Planning',
      'Topic :: Text Processing :: Markup',
      'Intended Audience :: Science/Research',
      'Topic :: Scientific/Engineering',
      'Topic :: Software Development :: Documentation',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python :: 3 :: Only'
      ]
)

if __name__ == "__main__":
  setup(**setup_args)

