
"""
'top-level' functions intended to be used in command-line
scripts and tools.
"""


import sys

from io import StringIO

from .parsers import MarkdownParser
from .processors import PythonProcessor


def twine(infile_name, outfile_name = None) -> None :
  """
  Process a markdown document and write output to a file
  :param file: ``string`` input filename
  """

  print("does nothing, yet. filen = ", infile_name, file=sys.stderr)

  assert infile_name != '', 'No input file specified'
  assert infile_name is not None, 'No input file specified'


  with open(infile_name, encoding="utf8") as infile:
    parser = MarkdownParser(file=infile)

    if outfile_name:
      # pylint: disable=consider-using-with
      get_out = lambda : open(outfile_name, encoding="utf8")
    else:
      get_out = lambda : sys.stdout

    with get_out() as outfile:

      print("hi", file=outfile)

    #chunks = parser.parse()
    #sink = StringIO()
    #processor = PythonProcessor(sink)
    #processor.twine(chunks)


    #return sink.getvalue()



