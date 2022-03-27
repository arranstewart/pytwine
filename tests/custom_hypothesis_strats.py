"""
custom strategies for use with Hypothesis
"""

from hypothesis import strategies as st
from hypothesis.strategies._internal.utils import cacheable, defines_strategy
from hypothesis.strategies._internal import SearchStrategy

from pytwine.core import DocChunk, CodeChunk

@defines_strategy(force_reusable_values=True)
@cacheable
def doc_chunks(
) -> SearchStrategy[DocChunk]:
  """Returns a strategy that generates random DocChunks.

  'number' and 'startLineNum' are always set to -1.
  """

  mkDocChunk = lambda s : DocChunk(contents=s+'\n', number=-1, startLineNum=-1)
  return st.builds(mkDocChunk, st.text(min_size=1))

def mk_codechunk(s : str) -> CodeChunk:
  "make code chunk where all we vary is contents"

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
  return st.builds(mk_codechunk, st.text())


