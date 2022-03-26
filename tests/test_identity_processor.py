
from hypothesis import given, strategies as st
from hypothesis.strategies._internal.utils import cacheable, defines_strategy
from hypothesis.strategies._internal import SearchStrategy, check_strategy
from io import StringIO

from pytwine.core import Chunk, DocChunk, CodeChunk, merge_docchunks
from pytwine.parsers import MarkdownParser
from pytwine.processors import IdentityProcessor

from hypothesis.strategies._internal.numbers import (
    IntegersStrategy,
    Real,
    floats,
    integers,
)

from typing import (
    Any,
    AnyStr,
    Callable,
    Dict,
    FrozenSet,
    Hashable,
    Iterable,
    List,
    Optional,
    Pattern,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from typing import cast
import re


def test_simple_doc():
  mydoc = """\
```python .important foo=bar
print()
```
bar
```python
print(2)
```
"""

  parser = MarkdownParser(string=mydoc)
  chunks = parser.parse()
  print("got chunks:")
  for c in chunks:
    print("  ", repr(c))
  print("\n\n")

  sink = StringIO()
  processor = IdentityProcessor(sink)
  processor.twine(chunks)

  if sink.getvalue() != mydoc:
    print("assertion will fail")
    print("sink  = ", repr(sink.getvalue()))
    print("mydoc = ", repr(mydoc))


  assert sink.getvalue() == mydoc, "should reverse parser"

@defines_strategy(force_reusable_values=True)
@cacheable
def doc_chunks(
) -> SearchStrategy[DocChunk]:
    """Returns a strategy that generates random DocChunks.

    'number' and 'startLineNum' are always set to -1.
    """

    mkDocChunk = lambda s : DocChunk(contents=s+'\n', number=-1, startLineNum=-1)
    return st.builds(mkDocChunk, st.text(min_size=1))

def mkCodeChunk(s : str) -> CodeChunk:
  s = repr(s)
  python_code = f'print({s})\n'
  return CodeChunk(contents=python_code, number=-1, startLineNum=-1,
                    block_start_line="```python\n",
                    block_end_line="```\n"
            )


@defines_strategy(force_reusable_values=True)
@cacheable
def code_chunks(
) -> SearchStrategy[CodeChunk]:
    """Returns a strategy that generates random CodeChunks.

    'number' and 'startLineNum' are always set to -1.
    """
    return st.builds(mkCodeChunk, st.text())

# true if all are docs
def all_are_docs(xs : List[Chunk]) -> bool:
  for x in xs:
    if x.chunkType != "doc":
      return False
  return True


# when we find two adjoining doc chunks, merge them
def merge_runs(chunks : List[Chunk]) -> List[Chunk]:
  if not chunks:
    return []

  if len(chunks) == 1:
    return chunks

  res : List[Chunk] = []

  # contiguous DocChunks
  run : List[Chunk] = []
  startedRun = False

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
            startedRun = True
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

# set nums to -1
def fixChunk(c : Chunk) -> Chunk:
  if c.chunkType == "doc":
    return DocChunk(c.contents, -1, -1)
  elif c.chunkType == "code":
    c = cast(CodeChunk, c)
    return CodeChunk(c.contents, -1, -1,
                  block_start_line=c.block_start_line,
                  block_end_line=c.block_end_line)
  else:
    raise Exception("unexpected chunk type")


def chunksToDoc(chunks):
  sink = StringIO()
  processor = IdentityProcessor(sink)
  processor.twine(chunks)
  return sink.getvalue()

@given(st.lists( st.one_of(doc_chunks(), code_chunks()) ))
def test_doc_chunkys(chunks):

  normalized_chunks = merge_runs(chunks)

  doc = chunksToDoc(chunks)
  parser = MarkdownParser(string=doc)
  # set nums to -1
  fixed_new_chunks = [fixChunk(c) for c in parser.parse()]

  assert normalized_chunks == fixed_new_chunks

