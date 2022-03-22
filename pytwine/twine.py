
import re

from typing import List, NamedTuple, Any #, Set, Dict, Tuple, Optional

class Chunk(NamedTuple):
  "A chunk of document -- either a code block, or non-code-block."

  chunkType:  str
  content:    str
  number:     int
  start_line: int

class DocChunk(Chunk):
  def __new__(cls, **kwargs):
    if "chunkType" in kwargs:
      del kwargs["chunkType"]
    self = super(DocChunk, cls).__new__(cls, chunkType="doc", **kwargs)
    return self

# "options" won't get printed or used in ==
class CodeChunk(Chunk):
  """ A Chunk with a self.options attribute added.
  (doesn't get included for str(), repr() or == purposes.)
  """

  def __new__(cls, **kwargs):
    if "chunkType" in kwargs:
      del kwargs["chunkType"]
    if "options" in kwargs:
      options = kwargs["options"]
      del kwargs["options"]
    else:
      options = None
    self = super(CodeChunk, cls).__new__(cls, chunkType="code", **kwargs)
    self.options = options
    return self



def read_file(source: str) -> str:
    """
    Read file contents
    """

    with open(source, 'r', encoding='utf-8') as infile:
        contents = infile.read()
    return contents

class Parser:
  """Reads and parses twineable documents into a list of
  Chunks.

  Code blocks are considered to start on the line where
  the block marker (e.g. ```) begins, and end on the line of their
  end marker.

  Empty blocks, and code blocks containing only whitespace,
  are skipped.

  Code blocks can have pandoc-style _options_
  (e.g. ```python .important startLine=101 animal="spotted lynx"```)
  where dot gives a class and the = gives attributes;
  but the Parser _doesn't parse these_. It just stores
  the whole unparsed start-of-block line; other classes can parse the options.

  Only subclass so far is MarkdownParser.

  Subclasses should override is_codeblock_start and is_codeblock_end.

  sample usage (MarkdownParser subclass):

  >>> parser = MarkdownParser(string="some stuff")
  >>> chunks = parser.parse()
  >>> chunks
  [DocChunk(chunkType='doc', content='some stuff', number=1, start_line=1)]
  """

  # as doc is processed, state will alternate between
  # "doc" (i.e. in markdown bits)
  # and "code" (i.e. in code blocks)

  def __init__(self, file=None, string=None):
    """
    Keyword arguments:
    file: path to a file to be processed
    string: a sring to be processed.

    At least one of file or string must be given.

    """

    self.source = file

    # Get input from string or
    if file is not None:
      self.rawtext = read_file(self.source)
    elif string is not None:
      self.rawtext = string
    else:
      raise KeyError("string or file must be specified")
    self.state = "doc"  # Initial state of document

  def is_codeblock_start(self, line):
    """ returns a boolean-ish result when a line matches start-of-code-block """
    raise NotImplementedError('is_codeblock_start not implemented')

  def is_codeblock_end(self, line):
    """ returns a boolean-ish result when a line matches end-of-code-block

    Should only be called when we're in a block / i.e. when self.options is not None.
    """
    raise NotImplementedError('is_codeblock_end not implemented')

  def parse(self) -> List[Chunk] :
    lines : List[str] = self.rawtext.splitlines()

    # we accumulate a chunk of lines in currentChunk
    # (then join them back together once the chunk is done)
    currentChunk  : List[str]   = []
    chunks        : List[Chunk] = []

    # keep track of how many code and non-code chunks
    # we've seen
    codeN : int = 1
    docN  : int = 1

    # stores start of code block, so that (a) we know
    # about options, and (b) we can match end.
    self.options = None
    lineNo : int = 0
    chunk_start_line : int = 1

    # set to True when we hit a code-block start line or end line
    # (```) -- we exclude that line from the block and take
    # only the contents.
    onBlockBorder : bool = False

    def addChunk(chunkType) -> bool:
      """
      helper: add current chunk to chunks.
      don't add empty chunks or whitespace-only code
      chunks.

      returns: whether a chunk was added
      """
      assert chunkType in ["doc", "code"]

      content = "\n".join(currentChunk)
      if chunkType == "doc":
        number = docN
        clazz : type = DocChunk
      elif chunkType == "code":
        number = codeN
        clazz = CodeChunk

      # Don't parse empty chunks, or whitespace-only code chunks
      if (chunkType == "code" and content.strip()) or \
         (chunkType == "doc" and content):
        keywords = dict(chunkType=chunkType,
                        content=content,
                        number=number,
                        start_line=chunk_start_line)
        if chunkType == "code":
          keywords["options"] = self.options

        chunks.append( clazz(**keywords) )
        return True
      return False

    # we want lineNos from 1, not 0
    bumpFst = lambda x : (x[0] + 1, x[1])

    for lineNo, line in map(bumpFst, enumerate(lines)):

      if self.state != "code" and self.is_codeblock_start(line):
        self.state = "code"
        self.options = line
        #import sys
        #print(found_codeblock_start, file=sys.stderr)

        # we've finished a doc chunk, append it
        if addChunk("doc"):
          docN += 1
        currentChunk = []
        chunk_start_line = lineNo
        onBlockBorder = True
      elif self.state == "code" and self.is_codeblock_end(line):
        self.state = "doc"
        # we've finished a code chunk, append it
        if addChunk("code"):
          codeN += 1
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
      addChunk("code")
    elif self.state == "doc":
      addChunk("doc")

    return chunks


class MarkdownParser(Parser):
  """
  Look for code blocks that look like "```.python " or
  "~~~python " or similar.

  Closing triple must match opening.

  i.e., if we start a code block with ```python, then
  ~~~ doesn't end it.

  (And we can therefore include code like:

mystring=\"\"\"
~~~
\"\"\"

  safely inside it.)

  """

  def __init__(self, file=None, string=None):
      Parser.__init__(self, file, string)

      # see tests/test_parser.py/test_tildes_can_start_block
      self.codeblock_begin = r"^[`~]{3,}\s*(?:|\.|)python(?:;|,|)\s*(.*?)(?:\}|\s*)$"
      self.codeblock_end = r"^(`|~){3,}\s*$"

  def is_codeblock_start(self, line):
    """ returns a boolean-ish result when a line matches
    `codeblock_begin` pattern
    """
    return re.match(self.codeblock_begin, line)

  def is_codeblock_end(self, line):
    """ returns a boolean-ish result when a line matches
    `codeblock_end` pattern.

    Should only be called when we're in a code block
    (i.e. when self.options is not None)
    """
    assert self.options is not None

    blockStart = self.options[:3]

    return line.strip() == blockStart




class Twiner:

  """
  For processing documents.
  """

  def __init__(self, source, output = None):
    self.source = source
    #name, ext = os.path.splitext(os.path.basename(source))
    #self.basename = name
    #self.file_ext = ext
    self.sink = None
    self.output = output

    self.parsed = None
    self.executed = None

  def _setwd(self):
      self.wd = os.path.dirname(self.source)

      self.reader.parse()
      self.parsed = self.reader.getparsed()

  ##### !!!
  def run(self, Processor = None):
      """Execute code in the document"""
      if Processor is None:
          Processor = PwebProcessors.getprocessor(self.kernel)

      proc = Processor(copy.deepcopy(self.parsed),
                       self.kernel,
                       self.source,
                       self.documentationmode,
                       self.figdir,
                       self.wd
                      )
      proc.run()
      self.executed = proc.getresults()

  ### !!!
  def write(self):
      """Write formatted code to file"""
      self.setsink()

      self._writeToSink(self.formatted.replace("\r", ""))
      self._print('Weaved {src} to {dst}\n'.format(src=self.source,
                                                        dst=self.sink))
  def twine(self):
      """Weave the document, equals -> parse, run, format, write"""
      self.run()
      self.format()
      self.write()



