"""
'top-level' functions intended to be used in command-line
scripts and tools.
"""

import sys

from .core        import TwineExitStatus
from .parsers     import MarkdownParser
from .processors  import PythonProcessor

def cli_twine(infile_name : str, outfile_name : str = None) -> TwineExitStatus :
  """
  Process a markdown document and write output to a file

  Parameters:
    infile_name: input filename
    outfile_name: output filename

  Returns:
    an aptional int (actually, a :class:`TwineExitStatus`) that
    can be passed to sys.exit.
  """

  with open(infile_name, encoding="utf8") as infile:
    parser = MarkdownParser(file=infile)
    chunks = parser.parse()

    if outfile_name:
      # pylint: disable=consider-using-with
      get_out = lambda : open(outfile_name, "w", encoding="utf8")
    else:
      sys.stdout.close = lambda : None # type: ignore
      get_out = lambda : sys.stdout

    with get_out() as outfile:
      processor = PythonProcessor(outfile)
      result = processor.twine(chunks)

    return result





