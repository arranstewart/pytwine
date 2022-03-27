
"""
test the PythonProcessor class
"""

from io import StringIO

from pytwine.parsers import MarkdownParser
from pytwine.processors import PythonProcessor

def test_simple_doc():
  "simple doc containing a code block"

  mydoc = """\
```python .important foo=bar
print("aaa")
```
bar
```python
print(2)
```
"""

  expected = 'aaa\nbar\n2\n'

  parser = MarkdownParser(string=mydoc)
  chunks = parser.parse()
  sink = StringIO()
  processor = PythonProcessor(sink)
  processor.twine(chunks)

  assert sink.getvalue() == expected, "should process python"

def test_bad_doc():
  """test with an uncompilable code block -
  should be omitted"""

  mydoc = """\
```python .important foo=bar
import
print(
```
bar
```python
print(2)
```
"""

  expected = 'bar\n2\n'

  parser = MarkdownParser(string=mydoc)
  chunks = parser.parse()
  sink = StringIO()
  processor = PythonProcessor(sink)
  processor.twine(chunks)

  assert sink.getvalue() == expected, "should process python"



def test_pwd():
  """
  TODO: fix this test

  document behaviour
  """
  # TODO: fix test_pwd

  mydoc = """\
```python .important foo=bar
import os
print(os.getcwd())
```
bar
```python
print(2)
```
"""

  expected = 'aaa\nbar\n2\n'

  parser = MarkdownParser(string=mydoc)
  chunks = parser.parse()
  sink = StringIO()
  processor = PythonProcessor(sink)
  processor.twine(chunks)

  assert sink.getvalue() == expected, "should process python"


