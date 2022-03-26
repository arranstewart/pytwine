
r"""
Classes that turn lists of
:class:`Chunk <pytwine.core.Chunk>`\ s back into
documents.
"""

import sys

from typing import List, TextIO, cast, Dict, Any

# ?? use binary??
from io import StringIO

from .core import Chunk, CodeChunk

class AnnotatedCodeChunk(CodeChunk):
  """ just used for casting, so that mypy won't complain
  about attributes we add.
  """

  pass
  #wibble: bool

class Processor:
  r"""
  Base class for things that process a list of
  :class:`Chunk <pytwine.core.Chunk>`\ s back into
  a document.

  Attributes:
      sink: subclasses should have an attribute ``sink``,
        a file-like that gets written to.

  """

  sink: TextIO

  def write(self, s : str):
    """write ``s`` to our ``sink`` with no newline"""

    self.sink.write(s)


class IdentityProcessor(Processor):
  """
  The processor that tries to map every chunk back to itself.
  """

  def __init__(self, sink: TextIO):
    """
    sink: a file-like object to be written to.
    """

    self.sink = sink

  def twine(self, chunks : List[Chunk] ) -> None:
    """WORK IN PROGRESS"""

    for chunk in chunks:

      if chunk.chunkType == "doc":
        self.write(chunk.contents)
      elif chunk.chunkType == "code":
        chunk = cast(AnnotatedCodeChunk, chunk)
        #chunk.wibble = True
        self.write(chunk.block_start_line)
        self.write(chunk.contents)
        self.write(chunk.block_end_line)


class PythonProcessor(Processor):
  """
  Processor that tries to run all code block as Python.
  """

  def __init__(self, sink: TextIO, log: TextIO = sys.stderr):
    """
    sink: a file-like object to be written to.
    """

    self.sink = sink
    self.log = log
    self.globals : Dict[Any,Any] = {}


  ######
  # TODO: make sure we store original filename
  # so can use in error mesgs

  def _runcode(self, chunk : CodeChunk):
    old_stdout = sys.stdout
    try:
      tmp_stdout = StringIO()
      sys.stdout = tmp_stdout
      code_obj = compile(chunk.contents, '<string>', 'exec')
      exec(code_obj, self.globals)
      sys.stdout = old_stdout
    except Exception as ex:
      print("exception occurred :/", ex)
    finally:
      sys.stdout = old_stdout

    return tmp_stdout.getvalue()

  def twine(self, chunks : List[Chunk] ) -> None:
    """WORK IN PROGRESS"""

    for chunk in chunks:

      if chunk.chunkType == "doc":
        self.write(chunk.contents)
      elif chunk.chunkType == "code":
        chunk = cast(AnnotatedCodeChunk, chunk)
        print("Processing chunk", chunk.number, file=self.log)
        result = self._runcode(chunk)
        self.write(result)

        ##chunk.wibble = True
        #self.write(chunk.block_start_line)
        #self.write(chunk.contents)
        #self.write(chunk.block_end_line)


#class Twiner:
#
#  """
#  For processing documents.
#  """
#
#  def __init__(self, source, output = None):
#    self.source = source
#    #name, ext = os.path.splitext(os.path.basename(source))
#    #self.basename = name
#    #self.file_ext = ext
#    self.sink = None
#    self.output = output
#
#    self.parsed = None
#    self.executed = None
#
#  def _setwd(self):
#      self.wd = os.path.dirname(self.source)
#
#      self.reader.parse()
#      self.parsed = self.reader.getparsed()
#
#  ##### !!!
#  def run(self, Processor = None):
#      """Execute code in the document"""
#      if Processor is None:
#          Processor = PwebProcessors.getprocessor(self.kernel)
#
#      proc = Processor(copy.deepcopy(self.parsed),
#                       self.kernel,
#                       self.source,
#                       self.documentationmode,
#                       self.figdir,
#                       self.wd
#                      )
#      proc.run()
#      self.executed = proc.getresults()
#
#  ### !!!
#  def write(self):
#      """Write formatted code to file"""
#      self.setsink()
#
#      self._writeToSink(self.formatted.replace("\r", ""))
#      self._print('Weaved {src} to {dst}\n'.format(src=self.source,
#                                                        dst=self.sink))
#  def twine(self):
#      """Weave the document, equals -> parse, run, format, write"""
#      self.run()
#      self.format()
#      self.write()






