
"""
Functions that get invoked by installed scripts.

Wrappers around functions in :mod:`pytwine.cli`
which add command-line argument parsing.

"""

import sys

from typing import Optional, TextIO, cast
from optparse import OptionParser

import pytwine
from .cli   import cli_twine
from .core  import TwineExitStatus

def _open_or_fallback( file_path : Optional[str], mode: str, fallback: Optional[TextIO] ):
  """
  Arguments:
    file_path: a file path to open, or None to use the fallback.
    mode: mode to open with (e.g. "w" or "r")
    fallback: what to use when file_path is None; when context
      finishes, this *won't* close.
  """

  if file_path is None:
    fallback.close = lambda : None # type: ignore
    return fallback

  # pylint: disable=consider-using-with
  return open(file_path, mode, encoding="utf8")


def pytwine_script() -> None:
  """
  Implement the ``pytwine`` script: parse command line options,
  process a document, exit with an appriorate exit status.

  Option stuff:
    - if no sourcefile given, or "-" given, use stdin
    - if no outfile given, or "-" given, use stdout

  """

  # Command line options
  parser = OptionParser(usage="pytwine [options] [sourcefile [outfile]]",
                        version="pytwine " + pytwine.__version__)
#    parser.add_option("-f", "--format", dest="doctype", default=None,
#                      help="The output format. Available formats: " +
#                             pytwine.PwebFormats.shortformats() +
#                           " Use pytwine -l to list descriptions or see
#                             http://mpastell.com/pytwine/formats.html")

  parser.add_option("-o", "--output", dest="output", default=None,
                    help="Name of the output file. (Overrides any arguments)")
  parser.add_option("-d", "--debug", dest="debug", action="store_true",
                    help="print additional debugging information to standard error")

  (options, args) = parser.parse_args()
  options_dict = vars(options)

  if len(args) > 2:
    parser.print_help()
    sys.exit(TwineExitStatus.BAD_SCRIPT_ARGS)

  infile_path  : Optional[str] = None
  outfile_path : Optional[str] = None

  try:
    infile_path = args.pop(0)
  except IndexError:
    pass

  # empty string and "-" become stdin
  if not infile_path or infile_path == "-":
    infile_path = None

  try:
    outfile_path = args.pop(0)
  except IndexError:
    pass

  if "output" in options_dict and options_dict["output"] is not None:
    outfile_path = options_dict["output"]
  del options_dict["output"]

  # empty string and "-" become stdout
  if not outfile_path or outfile_path == "-":
    outfile_path = None

  #options_dict["debug"] = True

  with _open_or_fallback( infile_path, "r", sys.stdin) as ifp:
    with _open_or_fallback( outfile_path, "w", sys.stdout) as ofp:
      res = cli_twine(ifp, ofp, **options_dict)
      sys.exit(res.value)



