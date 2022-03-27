
"""
test the IdentityProcessor
"""

from io import StringIO
from typing import (
    List,
    cast
)

from hypothesis import given, strategies as st

from custom_hypothesis_strats import doc_chunks, code_chunks

from pytwine.core import Chunk, DocChunk, CodeChunk, merge_docchunks
from pytwine.parsers import MarkdownParser
from pytwine.processors import IdentityProcessor

def test_simple_doc():
  "test a simple document"

  mydoc = """\
```python .important foo=bar
print("aaa")
```
bar
```python
print(2)
```
"""

  parser = MarkdownParser(string=mydoc)
  chunks = parser.parse()
  sink = StringIO()
  processor = IdentityProcessor(sink)
  processor.twine(chunks)

  assert sink.getvalue() == mydoc, "should reverse parser"


# true if all are docs
def all_are_docs(xs : List[Chunk]) -> bool:
  "for all xs, x is a docchunk"

  return all(x.chunkType == "doc" for x in xs)

def merge_runs(chunks : List[Chunk]) -> List[Chunk]:
  "when we find two adjoining doc chunks, merge them"

  if not chunks:
    return []

  if len(chunks) == 1:
    return chunks

  res : List[Chunk] = []

  # contiguous DocChunks
  run : List[Chunk] = []

  i=0
  while i < len(chunks):

    curr = chunks[i]

    if i < len(chunks) - 1:
      nxt  = chunks[i+1]
    else:
      nxt = None

    if not run:
      if curr.chunkType == "doc" and \
       nxt and nxt.chunkType == "doc":
        run = [curr, nxt]
        i += 1
      else:
        res.append(curr)
    else:
      # finished run?
      if curr.chunkType != "doc":
        assert all_are_docs(run)
        combo = merge_docchunks(cast(List[DocChunk], run))
        res.append(combo)
        run = []
        res.append(curr)
      else:
        run.append(curr)

    i += 1

  # if last run to finish; means
  # last el _must_ have been doc.
  if run:
    assert all_are_docs(run)
    combo = merge_docchunks(cast(List[DocChunk], run))
    res.append(combo)
    run = []

  return res

def fixChunk(c : Chunk) -> Chunk:
  "set nums to -1"

  if c.chunkType == "doc":
    return DocChunk(c.contents, -1, -1)
  if c.chunkType == "code":
    c = cast(CodeChunk, c)
    return CodeChunk(c.contents, -1, -1,
                  block_start_line=c.block_start_line,
                  block_end_line=c.block_end_line)
  raise Exception("unexpected chunk type")


def chunksToDoc(chunks):
  "use IdentityProcessor to turn chunks into a string"

  sink = StringIO()
  processor = IdentityProcessor(sink)
  processor.twine(chunks)
  return sink.getvalue()

@given(st.lists( st.one_of(doc_chunks(), code_chunks()) ))
def test_IdentityProcessor_roundtrips_chunks(chunks):
  r"""
  Given an arbitrary list of chunks, we can turn those
  into a string with the IdentityProcessor, then parse
  the resulting string back into chunks.

  The returned chunks should equal the original ones,
  subject to:

  - line-endings all being converted to '\n'
  - adjonining doc chunks being merged
  - if our original chunks didn't have correct chunk.number
    and startLineNums, we'll have to massage the
    final chunks (e.g. setting everything to -1).
  """

  normalized_chunks = merge_runs(chunks)

  doc = chunksToDoc(chunks)
  parser = MarkdownParser(string=doc)
  # set nums to -1
  fixed_new_chunks = [fixChunk(c) for c in parser.parse()]

  assert normalized_chunks == fixed_new_chunks

