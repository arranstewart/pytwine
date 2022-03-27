
r"""
Classes that turn lists of
:class:`Chunk <pytwine.core.Chunk>`\ s back into
documents.
"""

import sys
import textwrap as tw
import traceback

from typing import List, TextIO, cast, Dict, Any

# ?? use binary??
from io import StringIO

from .core import Chunk, CodeChunk, TwineExitStatus

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
      _sink: subclasses should have an attribute ``_sink``,
        a file-like that gets written to.

  """

  _sink: TextIO

  def _write(self, s : str):
    """write ``s`` to our ``_sink`` with no newline"""

    self._sink.write(s)


class IdentityProcessor(Processor):
  """
  The processor that tries to map every chunk back to itself.
  """

  def __init__(self, sink: TextIO):
    """
    Arguments:
      sink: a file-like object to be written to.
    """

    self._sink = sink

  def twine(self, chunks : List[Chunk] ) -> None:
    """THE TWINE FUNC - WORK IN PROGRESS"""

    for chunk in chunks:

      if chunk.chunkType == "doc":
        self._write(chunk.contents)
      elif chunk.chunkType == "code":
        chunk = cast(AnnotatedCodeChunk, chunk)
        #chunk.wibble = True
        self._write(chunk.block_start_line)
        self._write(chunk.contents)
        self._write(chunk.block_end_line)


def _get_traceback_text(exc_type, value, tb) -> str:
  """return the text that would be printed by
  traceback.print_exception.
  """

  sio = StringIO()
  traceback.print_exception(exc_type, value, tb, file=sio)
  return sio.getvalue()


class PythonProcessor(Processor):
  """
  Processor that tries to run all code blocks as Python.

  Uncompileable code blocks just get omitted from the output.

  TODO: put an error into the output
  """
  # TODO: put an error into the output

  def __init__(self, sink: TextIO, log: TextIO = sys.stderr):
    """
    Arguments:
      sink: a file-like object to be written to.
    """

    self._sink = sink
    self.log = log
    self.globals : Dict[Any,Any] = {}
    self.exceptions_encountered : List[Exception] = []


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
    except SyntaxError as ex:
      (exc_type, value, tb) = sys.exc_info()
      self.exceptions_encountered.append(ex)
      indentation = " " * 4
      block_excerpt = tw.indent("\n".join(chunk.contents.splitlines()[:3]),
                                indentation)
      tb_text = _get_traceback_text(exc_type, value, tb)

      print(f"compilation exception while processing code block no. {chunk.number},",
            f"beginning at line {chunk.startLineNum} of input file:\n",
            "\n" + block_excerpt,
            "\n\n    ...\n",
            file=self.log)
      hbar = '-' * 40
      print(tw.indent(hbar + "\n" + tb_text, indentation),
            file=self.log)

    except KeyError as ex:
      print("exception occurred :/", ex)
    finally:
      sys.stdout = old_stdout

    return tmp_stdout.getvalue()

  def twine(self, chunks : List[Chunk] ) -> TwineExitStatus:
    """WORK IN PROGRESS - process chunks and write to sink.

    in case of errors, returns a :class:`TwineExitStatus`;
    its .value attribute is either int or None, and
    can be passed to sys.exit as a status code.

    Effects:
      - output is written to the ``sink`` arrgument
        passed to the constructor.

    """

    for chunk in chunks:

      if chunk.chunkType == "doc":
        self._write(chunk.contents)
      elif chunk.chunkType == "code":
        chunk = cast(AnnotatedCodeChunk, chunk)
        print("Processing chunk", chunk.number, file=self.log)
        result = self._runcode(chunk)
        self._write(result)

    if self.exceptions_encountered:
      num_exceptions = len(self.exceptions_encountered)
      print("Encountered", num_exceptions,
            "exceptions while processing input file",
            file=self.log)
      return TwineExitStatus.BLOCK_COMPILATION_ERROR

    return TwineExitStatus.SUCCESS

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






