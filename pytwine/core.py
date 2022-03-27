
"""
Core classes: chunks of document, exit statuses.
"""

from enum import Enum
from typing import NamedTuple, List

class Chunk(NamedTuple):
  """
  A chunk of document – either a code block, or non-code block.

  Best to construct them using one of the subclasses
  :class:`DocChunk` or :class:`CodeChunk`.

  Attributes:
      chunkType:    "doc" or "code"
      contents:     string contents of the chunk
      number:       doc or code chunk position number in the document
                    (i.e. 0 through to number-of-doc-chunks - 1),
                    mutatis mutandis for code chunks.
      startLineNum: line number (starting from 1) the chunk was found at.
  """

  chunkType:    str
  contents:     str
  number:       int
  startLineNum: int

class DocChunk(Chunk):
  """A non-code-block.

  Keyword arguments:
      contents:     string content
      number:       what number docchunk this is in the document
      startLineNum: what line the chunk started on

  >>> d = DocChunk(contents="foo bar", number=3, startLineNum=10)
  >>> d
  DocChunk(chunkType='doc', contents='foo bar', number=3, startLineNum=10)
  """

  def __new__(cls, *args, **kwargs):

    # out of politeness, we remove a "chunkType" arg if it's
    # accidentally been included.
    if "chunkType" in kwargs:
      del kwargs["chunkType"]

    self = super(DocChunk, cls).__new__(cls, "doc", *args, **kwargs)
    return self

def merge_docchunks(chunks: List[DocChunk]) -> DocChunk:
  """
  merge several dochunks into one. error if list is empty.

  number is number of 1st in chunk, startLineNum ditto.
  """

  if not chunks:
    raise ValueError("ack!")

  combined_conts = []
  for chunk in chunks:
    combined_conts.append( chunk.contents )

  return DocChunk(contents=''.join(combined_conts),
                  number=chunks[0].number,
                  startLineNum=chunks[0].startLineNum)

class CodeChunk(Chunk):
  """ A code block :class:`Chunk`.

  Attributes:
    block_start_line: stores the start-of-code-block demarcator
                line.
    block_end_line: stores the end-of-code-block demarcator
                line.
  >>> c = CodeChunk(contents="foo bar", number=3, startLineNum=10, \
block_start_line="``` python", block_end_line="```")
  >>> c
  CodeChunk(chunkType='code', contents='foo bar', number=3, \
startLineNum=10, block_start_line='``` python', block_end_line='```')
  """

  block_start_line: str
  block_end_line:   str

  def __new__(cls, *args, **kwargs):
    if "chunkType" in kwargs:
      del kwargs["chunkType"]

    if "block_start_line" in kwargs:
      block_start_line = kwargs["block_start_line"]
      assert block_start_line is not None, \
          "block_start_line for CodeChunk may not be None"
      del kwargs["block_start_line"]
    else:
      raise ValueError("must specify block_start_line for CodeChunk")

    if "block_end_line" in kwargs:
      block_end_line = kwargs["block_end_line"]
      assert block_end_line is not None, \
          "block_end_line for CodeChunk may not be None"
      del kwargs["block_end_line"]
    else:
      raise ValueError("must specify block_end_line for CodeChunk")

    self = super(CodeChunk, cls).__new__(cls, "code", *args, **kwargs)
    self.block_start_line = block_start_line
    self.block_end_line   = block_end_line
    return self

  def __str__(self):
    orig = super().__str__()
    return orig[0:-1] + \
      ", block_start_line=" + str(self.block_start_line) + \
      ", block_end_line=" + str(self.block_end_line) + ")"

  def __repr__(self):
    orig = super().__repr__()
    return orig[0:-1] + \
      ", block_start_line=" + repr(self.block_start_line) + \
      ", block_end_line=" + repr(self.block_end_line) + ")"

  def __eq__(self, value):
    orig = super().__eq__(value)
    if not orig:
      return False
    try:
      return self.block_start_line == value.block_start_line and \
             self.block_end_line == value.block_end_line
    except AttributeError:
      return False


class TwineExitStatus(Enum):
  """Some exit statuses.

  Given a TwineExitStatus, its .value is either
  `None` or an `int`, and can be passed to sys.exit.
  """

  SUCCESS = None
  "success"

  BAD_SCRIPT_ARGS = 1
  "wrong number, or, bad arguments sypplied to script"

  BLOCK_COMPILATION_ERROR = 2
  "an exception was encountered trying to compile a code block"


