# pylint: disable=protected-access, no-self-use

"""
test the pytwine.parsers classes.
"""

from pytwine.parsers import MarkdownParser, Chunk, CodeChunk

#def raiseChunks(chunks):
#  mystr = str(chunks)
#  raise Exception("my str = " + mystr)

def test_permissible_codeblock_starts():
  "check that they work: permissible ways to start a code block"

  parser = MarkdownParser(string="")

  acceptable_block_starts = [
      ("```python", "backtick fence start"),
      ("~~~python", "tilde fence start"),
      ("~~~.python", "python class marker"),
      ("~~~   .python", "leading spaces okay before python"),
      ("```python   ", "trailing spaces ok after python"),
      ("```   python", "leading spaces okay before python"),
      ("```python .important foo=bar", "other attributes okay"),
      ("~~~python .important foo=bar", "tildes and attributes okay"),
      ("~~~~python", "4 tildes okay")
    ]

  for sample, descrip in acceptable_block_starts:
    result : str = parser._is_codeblock_start(sample)
    assert result, "code block starts: " + descrip

def test_codeblock_starts_only_in_col0():
  """
  The parser only recognizes a code-block when it appears
  at the top level - not indented in any way.
  """

  parser = MarkdownParser(string="")

  unrecognized_block_starts = [
      " ```python",
      "\t~~~python",
      "\xa0~~~.python",
      "\u1680~~~   .python",
    ]

  for sample in unrecognized_block_starts:
    assert not parser._is_codeblock_start(sample)

class TestEmptyDocs:
  """tests in which the input document is
  (or is treated as) empty.
  """

  def test_empty_doc(self):
    "an empty document"

    doc = ""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    assert not chunks

  def test_empty_codeblock_is_skipped(self):
    "non-empty document, but with empty codeblock"

    doc = """\
```python { }
```
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    assert not chunks


class TestOneBlockDocs:
  """test documents containing
  (or which are treated as containing) one block.
  """

  def test_single_line_doc(self):
    "simple document with one line"

    doc = "testing testing 1 2 3"
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [Chunk(chunkType='doc',
                              contents=doc,
                              number=1,
                              startLineNum=1)]
    assert chunks == expected_chunks

  def test_empty_codeblock_is_skipped(self):
    "simple document with one line and empty code block"

    doc = """\
testing testing 1 2 3
```python
```
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [Chunk(chunkType='doc',
                              contents="testing testing 1 2 3\n",
                              number=1,
                              startLineNum=1)]
    assert chunks == expected_chunks

  def test_two_line_doc(self):
    "simple document with two lines"

    doc = "testing\ntesting 1 2 3"
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [Chunk(chunkType='doc',
                              contents=doc,
                              number=1,
                              startLineNum=1)]
    assert chunks == expected_chunks

  def test_codeblock_only(self):
    "simple document consisting solely of a code block"

    doc = """\
```python
print()
```
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [CodeChunk(
                              contents="print()\n",
                              number=1,
                              startLineNum=1,
                              block_start_line='```python\n',
                              block_end_line='```\n'
                              )]
    assert chunks == expected_chunks

  def test_4char_fence(self):
    """fences can be three (```) _or_ more backticks"""

    doc = """\
````python
print()
````
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [CodeChunk(
                              contents="print()\n",
                              number=1,
                              startLineNum=1,
                              block_start_line='````python\n',
                              block_end_line='````\n'
                              )]
    assert chunks == expected_chunks

  def test_codeblock_delimeters_must_match(self):
    """
    If a code block starts with ```SOMETHING, it must
    end with backticks as well.

    Trying to end with tildes means the block goes on.
    """

    doc = """\
```python
print()
mystring=\"\"\"
~~~
\"\"\"
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [CodeChunk(
                              contents='print()\nmystring="""\n~~~\n"""\n',
                              number=1,
                              startLineNum=1,
                              block_start_line='```python\n',
                              block_end_line=''
                              )]
    assert chunks == expected_chunks

  def test_codeblock_delimeters_must_matchlen(self):
    """
    If a code block starts with four tildes -- ~~~~SOMETHING, it must
    end with 4 tildes as well.

    Trying to end with fewer tildes means the block goes on.
    """

    doc = """\
~~~~python
print()
mystring=\"\"\"
~~~
\"\"\"
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [CodeChunk(
                              contents='print()\nmystring="""\n~~~\n"""\n',
                              number=1,
                              startLineNum=1,
                              block_start_line='~~~~python\n',
                              block_end_line=''
                              )]
    assert chunks == expected_chunks

class TestTwoBlockDocs:
  """some test documents containing
  (or which are treated as containing) two blocks
  """

  def test_starts_with_codeblock(self):
    "simple case where input doc starts with a code block"

    doc = """\
```python
print()
```
foo
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [\
        CodeChunk(
               contents="print()\n",
               number=1,
               startLineNum=1,
               block_start_line='```python\n',
               block_end_line='```\n'
               ),
        Chunk(chunkType='doc',
               contents="foo\n",
               number=1,
               startLineNum=4)
        ]
    assert chunks == expected_chunks

  def test_skips_whitespace_block(self):
    "code blocks containing only whitespace are skipped."


    doc = """\
```python
print()
```
foo
```python
\t
```
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [\
        CodeChunk(
               contents="print()\n",
               number=1,
               startLineNum=1,
               block_start_line='```python\n',
               block_end_line='```\n'),
        Chunk(chunkType='doc',
               contents="foo\n",
               number=1,
               startLineNum=4)
        ]
    assert chunks == expected_chunks

  def test_ends_in_codeblock(self):
    """a document may simply leave a code block unterminated -
    in that case, it runs to the end of the document.
    """

    doc = """\
foo
```python
print()
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [\
        Chunk(chunkType='doc',
               contents="foo\n",
               number=1,
               startLineNum=1),
        CodeChunk(
               contents="print()\n",
               number=1,
               startLineNum=2,
               block_start_line='```python\n',
               block_end_line='')
        ]
    assert chunks == expected_chunks


class TestThreeBlockDocs:
  """some test documents containing
  (or which are treated as containing) three blocks
  """

  def test_middle_codeblock(self):
    "document has a [doc,code,doc] sequence"

    doc = """\
foo
```python
print()
```
bar
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [\
        Chunk(chunkType='doc',
               contents="foo\n",
               number=1,
               startLineNum=1),
        CodeChunk(
               contents="print()\n",
               number=1,
               startLineNum=2,
               block_start_line='```python\n',
               block_end_line='```\n'),
        Chunk(chunkType='doc',
               contents="bar\n",
               number=2,
               startLineNum=5)
        ]
    assert chunks == expected_chunks


  def test_multicode_starts_with_code(self):
    "document has a [code,doc,code] sequence"

    doc = """\
```python
print()
```
bar
```python
print(2)
```
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [\
        CodeChunk(
               contents="print()\n",
               number=1,
               startLineNum=1,
               block_start_line='```python\n',
               block_end_line='```\n'),
        Chunk(chunkType='doc',
               contents="bar\n",
               number=1,
               startLineNum=4),
        CodeChunk(
               contents="print(2)\n",
               number=2,
               startLineNum=5,
               block_start_line='```python\n',
               block_end_line='```\n'),
        ]
    assert chunks == expected_chunks

def test_code_options():
  """attributes and options in the fence start are
  retained for later processing."""

  doc = """\
```python .important foo=bar
print()
```
bar
```python
print(2)
```
"""
  parser = MarkdownParser(string=doc)
  chunks = parser.parse()
  expected_chunks = [\
      CodeChunk(
             contents="print()\n",
             number=1,
             startLineNum=1,
             block_start_line='```python .important foo=bar\n',
             block_end_line='```\n'),
      Chunk(chunkType='doc',
             contents="bar\n",
             number=1,
             startLineNum=4),
      CodeChunk(
             contents="print(2)\n",
             number=2,
             startLineNum=5,
             block_start_line='```python\n',
             block_end_line='```\n'),
      ]
  assert chunks == expected_chunks

  assert chunks[0].block_start_line == "```python .important foo=bar\n"

