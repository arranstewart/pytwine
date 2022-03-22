
from pytwine.parser import MarkdownParser, Chunk

def raiseChunks(chunks):
  mystr = str(chunks)
  raise Exception("my str = " + mystr)

def test_permissible_codeblock_starts():
  parser = MarkdownParser(string="")

  acceptable_block_starts = [
      "```python",
      "~~~python",
      "~~~.python",
      "~~~   .python",
      "```python   ",
      "```   python",
      "```python .important foo=bar",
      "~~~python .important foo=bar",
    ]

  for sample in acceptable_block_starts:
    assert parser.is_codeblock_start(sample)

class TestEmptyDocs:

  def test_empty_doc(self):
    doc = ""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    assert chunks == []

  def test_empty_codeblock_is_skipped(self):
    doc = """\
```python { }
```
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    assert chunks == []


class TestOneBlockDocs:

  def test_single_line_doc(self):
    doc = "testing testing 1 2 3"
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [Chunk(chunkType='doc',
                              content=doc,
                              number=1,
                              start_line=1)]
    assert chunks == expected_chunks

  def test_empty_codeblock_is_skipped(self):
    doc = """\
testing testing 1 2 3
```python
```
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [Chunk(chunkType='doc',
                              content="testing testing 1 2 3",
                              number=1,
                              start_line=1)]
    assert chunks == expected_chunks

  def test_two_line_doc(self):
    doc = "testing\ntesting 1 2 3"
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [Chunk(chunkType='doc',
                              content=doc,
                              number=1,
                              start_line=1)]
    assert chunks == expected_chunks

  def test_codeblock_only(self):
    doc = """\
```python
print()
```
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [Chunk(chunkType='code',
                              content="print()",
                              number=1,
                              start_line=1)]
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
    expected_chunks = [Chunk(chunkType='code',
                              content='print()\nmystring="""\n~~~\n"""',
                              number=1,
                              start_line=1)]
    assert chunks == expected_chunks



class TestTwoBlockDocs:

  def test_starts_with_codeblock(self):
    doc = """\
```python
print()
```
foo
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [\
        Chunk(chunkType='code',
               content="print()",
               number=1,
               start_line=1),
        Chunk(chunkType='doc',
               content="foo",
               number=1,
               start_line=4)
        ]
    assert chunks == expected_chunks

  def test_skips_whitespace_block(self):
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
        Chunk(chunkType='code',
               content="print()",
               number=1,
               start_line=1),
        Chunk(chunkType='doc',
               content="foo",
               number=1,
               start_line=4)
        ]
    assert chunks == expected_chunks

  def test_ends_in_codeblock(self):
    doc = """\
foo
```python
print()
"""
    parser = MarkdownParser(string=doc)
    chunks = parser.parse()
    expected_chunks = [\
        Chunk(chunkType='doc',
               content="foo",
               number=1,
               start_line=1),
        Chunk(chunkType='code',
               content="print()",
               number=1,
               start_line=2)
        ]
    assert chunks == expected_chunks


class TestThreeBlockDocs:

  def test_middle_codeblock(self):
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
               content="foo",
               number=1,
               start_line=1),
        Chunk(chunkType='code',
               content="print()",
               number=1,
               start_line=2),
        Chunk(chunkType='doc',
               content="bar",
               number=2,
               start_line=5)
        ]
    assert chunks == expected_chunks


  def test_multicode_starts_with_code(self):
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
    #raiseChunks(chunks)
    expected_chunks = [\
        Chunk(chunkType='code',
               content="print()",
               number=1,
               start_line=1),
        Chunk(chunkType='doc',
               content="bar",
               number=1,
               start_line=4),
        Chunk(chunkType='code',
               content="print(2)",
               number=2,
               start_line=5)
        ]
    assert chunks == expected_chunks

def test_code_options():
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
      Chunk(chunkType='code',
             content="print()",
             number=1,
             start_line=1),
      Chunk(chunkType='doc',
             content="bar",
             number=1,
             start_line=4),
      Chunk(chunkType='code',
             content="print(2)",
             number=2,
             start_line=5)
      ]
  assert chunks == expected_chunks

  assert chunks[0].options == "```python .important foo=bar"

