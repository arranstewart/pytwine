#!/usr/bin/env python

import os
import sys
from setuptools import setup

def get_version():
  """Get version."""

  sys.path.append("pytwine")
  import _version # type: ignore
  return _version.__version__

def read(fname):
  "get contents"
  fpath = os.path.join(os.path.dirname(__file__), fname)
  with open(fpath, encoding="utf8") as ifp:
    return ifp.read()

setup(name='pytwine',
      entry_points={
          'console_scripts': [
                # thin wrapper around pytwine.cli.cli_twine
                'pytwine = pytwine.scripts:pytwine_script'
              ] },
      version = get_version(),
      description='Reports with embedded python computations',
      author='Arran D. Stewart',
      author_email='arran.stewart@uwa.edu.au',
      url='https://github.com/arranstewart/pytwine',
      packages=['pytwine'],
      install_requires = ['markdown'],
      python_requires = '>=3.6',
      extras_require = {'test': [ \
                            'pytest',
                            'pytest-cov',
                            'pytest-html',
                            'hypothesis'
                            ],
                        'docs': [ \
                            'sphinx >= 4.0'
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
