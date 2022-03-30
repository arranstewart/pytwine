"""
'top-level' functions intended to be used in command-line
scripts and tools.
"""

import sys

from typing import TextIO, Union


from .core        import TwineExitStatus
from .parsers     import MarkdownParser
from .processors  import PythonProcessor

def cli_twine(ifp : TextIO, ofp : TextIO, debug : bool =False) -> TwineExitStatus :
  """
  Process a markdown document and write output to a file

  Parameters:
    infile_name: input file-like
    outfile_name: output file-like

  Returns:
    a :class:`TwineExitStatus` with a .value that
    can be passed to sys.exit.
  """

  if debug:
    print("running cli w infile:", ifp, "outfile:", ofp, file=sys.stderr)

  parser = MarkdownParser(file=ifp)
  chunks = parser.parse()

  processor = PythonProcessor(ofp)
  return processor.twine(chunks)



