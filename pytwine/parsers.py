
"""
parse documents into chunks.
"""

import re

from typing import List, TextIO, cast, Optional

from .core import Chunk, CodeChunk, DocChunk

def _read_filepath(source: str) -> str:
  """
  Read file contents
  """

  with open(source, 'r', encoding='utf-8') as infile:
    contents = infile.read()
  return contents

def _read_file(infile: TextIO) -> str:
  """
  Read file contents
  """
  return infile.read()


class Parser:
  """
  Reads and parses twineable documents into a list of
  :class:`Chunk <pytwine.core.Chunk>`\\ s.

  Has a concept of a **code block marker**, i.e. something like
  markdown's backtick fenced code blocks::

    ```

  or tilde fenced code blocks::

    ~~~


  Code blocks are considered to start on the line where
  the code block marker begins, and end on the line of their
  end marker.

  Empty blocks, and code blocks containing only whitespace,
  are skipped.

  Code blocks can have pandoc-style **options**. e.g. for a Markdown
  document, the options would be given like so::

    ```python .important startLine=101 animal="spotted lynx"

  where dot gives a class and the ``=`` gives attributes.

  The Parser doesn't parse or process options at all, but just stores
  the whole unparsed start-of-block line in the
  ``block_start_line`` attribute
  of the :class:`CodeChunk <pytwine.core.CodeChunk>`;
  it's up to Processor classes to parse and potentially
  make use of the options.

  Only subclass so far is :class:`MarkdownParser`.

  Subclasses should override :meth:`_is_codeblock_start` and
  :meth:`_is_codeblock_end` (see the code for details).

  **sample usage:**

  sample usage using :class:`MarkdownParser` subclass:

  >>> parser = MarkdownParser(string="some stuff")
  >>> chunks = parser.parse()
  >>> chunks
  [DocChunk(chunkType='doc', contents='some stuff', number=1, startLineNum=1)]
  """

  # as doc is processed, state will alternate between
  # "doc" (i.e. in markdown bits)
  # and "code" (i.e. in code blocks)

  def __init__(self, file :TextIO =None, string :str =None):
    """
    Keyword arguments:
        file: path to a file to be processed
        string: a string to be processed

    One of either ``file`` or ``string`` must be given.

    """

    self.source = file

    # Get input from string or
    if self.source is not None:
      self.source = cast(TextIO, self.source)
      self.rawtext = _read_file(self.source)
    elif string is not None:
      self.rawtext = string
    else:
      raise KeyError("string or file must be specified")
    self.state = "doc"  # Initial state of document

    # stores start of code block, so that (a) we know
    # about block_start_line, and (b) we can match end.
    self.block_start_line : Optional[str] = None
    self.block_end_line   : Optional[str] = None


  def _is_codeblock_start(self, line : str):
    """ returns a boolean-ish result when a line matches start-of-code-block """
    raise NotImplementedError('_is_codeblock_start not implemented')

  def _is_codeblock_end(self, line : str):
    """ returns a boolean-ish result when a line matches end-of-code-block

    Should only be called when we're in a block / i.e. when self.block_start_line is not None.
    """
    raise NotImplementedError('_is_codeblock_end not implemented')

  def parse(self) -> List[Chunk] :
    r"""
    Parse the source and return a list of
    :class:`Chunk <pytwine.core.Chunk>`\ s.
    """

    lines : List[str] = self.rawtext.splitlines(keepends=True)

    # we accumulate a chunk of lines in currentChunk
    # (then join them back together once the chunk is done)
    currentChunk  : List[str]   = []
    chunks        : List[Chunk] = []

    # keep track of how many code and non-code chunks
    # we've seen
    codeN : int = 1
    docN  : int = 1

    # stores start of code block, so that (a) we know
    # about block_start_line, and (b) we can match end.
    self.block_start_line = None
    self.block_end_line   = None

    lineNo : int = 0
    chunk_start_line : int = 1

    # set to True when we hit a code-block start line or end line
    # (```) -- we exclude that line from the block and take
    # only the contents.
    onBlockBorder : bool = False

    def add_chunk(chunkType) -> bool:
      """
      helper func: add current chunk to chunks.
      don't add empty chunks or whitespace-only code
      chunks.

      returns: whether a chunk was added
      """
      assert chunkType in ["doc", "code"]

      contents = "".join(currentChunk)
      if chunkType == "doc":
        number = docN
        clazz : type = DocChunk
      elif chunkType == "code":
        number = codeN
        clazz = CodeChunk

      # Don't parse empty chunks, or whitespace-only code chunks
      if (chunkType == "code" and contents.strip() != "") or \
         (chunkType == "doc" and contents != ""):
        keywords = dict(chunkType=chunkType,
                        contents=contents,
                        number=number,
                        startLineNum=chunk_start_line)
        if chunkType == "code":
          keywords["block_start_line"] = self.block_start_line
          keywords["block_end_line"]   = self.block_end_line

        chunks.append( clazz(**keywords) )
        return True
      return False

    # we want lineNos from 1, not 0
    bumpFst = lambda x : (x[0] + 1, x[1])

    for lineNo, line in map(bumpFst, enumerate(lines)):

      if self.state != "code" and self._is_codeblock_start(line):
        self.state = "code"
        self.block_start_line = line

        # we've finished a doc chunk, append it
        if add_chunk("doc"):
          docN += 1
        currentChunk = []
        chunk_start_line = lineNo
        onBlockBorder = True
      elif self.state == "code" and self._is_codeblock_end(line):
        self.state = "doc"
        # we've finished a code chunk, append it
        self.block_end_line = line
        if add_chunk("code"):
          codeN += 1
        self.block_end_line = None
        currentChunk = []
        chunk_start_line = lineNo + 1
        onBlockBorder = True

      # add line to chunk (but not lines that are boundaries
      # of code blocks)
      if not onBlockBorder:
        currentChunk.append(line)
      onBlockBorder = False

    # end of for line in lines
    # Handle the last chunk
    if self.state == "code":
      self.block_end_line = ""
      add_chunk("code")
    elif self.state == "doc":
      add_chunk("doc")

    return chunks


class MarkdownParser(Parser):
  """
  Parse markdown files into chunks.

  Looks for markdown-style fenced code blocks that
  have "``python``" or "``.python``" as their first attribute; e.g.::

    ``` .python someproperty=foo

  See <https://spec.commonmark.org/0.30/#fenced-code-blocks>

  The closing "fence" must match the opening "fence": i.e., if we start a code
  block with backticks, then tildes won't end it.

  (And we can therefore include code like::

    mystring=\"""
    ~~~
    \"""

  safely inside it.)

  Fenced code blocks are only parsed when they appear at the root level –
  they aren't recognized if nested inside lists or block-quotes, for
  example. (But there's nothing to stop your Python code block from
  outputting indented content which will be inside a list or block
  quote.)

  """

  def __init__(self, file=None, string=None):
    Parser.__init__(self, file, string)

    # see tests/test_parser.py/test_tildes_can_start_block
    # two groups: the fence start (e.g. ``` or ```` or ~~~~)
    #   and the stuff that comes after "python"
    self.codeblock_begin = r"^([`~]{3,})\s*(?:|\.|)python(?:;|,|)\s*(.*?)(?:\}|\s*)$"

  def _is_codeblock_start(self, line):
    """ returns a boolean-ish result when a line matches
    ``codeblock_begin`` pattern
    """
    return re.match(self.codeblock_begin, line)

  def _is_codeblock_end(self, line):
    """ returns a boolean-ish result when a line is
    a codeblock end.

    Should only be called when we're in a code block
    (i.e. when self.block_start_line is not None)
    """
    assert self.block_start_line is not None

    # find out how the block started (three backticks? four tildes):
    # that's how it must end.
    regex_result = re.match(self.codeblock_begin, self.block_start_line)
    fence_chars, _ = regex_result.groups()

    return line.strip() == fence_chars


