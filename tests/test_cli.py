
"""
test cli-level functions, found in pytwine.cli
"""

from tempfile import TemporaryDirectory

from pytwine.core       import TwineExitStatus
from pytwine.cli        import cli_twine

def test_simple_doc():
  """run the cli_twine function on input file
  in a temporary directory
  """

  mydoc = """\
```python .important foo=bar
print("aaa")
```
bar
```python
print(2)
```
"""

  with TemporaryDirectory() as tmpdirname:
    infile = f"{tmpdirname}/tmp.pmd"
    outfile = f"{tmpdirname}/tmp.md"

    with open(infile, "w", encoding="utf8") as ofp:
      ofp.write(mydoc)

    res = cli_twine(infile, outfile)
    with open(outfile, "r", encoding="utf8") as ofp:
      actual_output = ofp.read()

    expected_output = 'aaa\nbar\n2\n'

    assert res == TwineExitStatus.SUCCESS
    assert actual_output == expected_output


def test_bad_doc():
  """run the cli_twine function on input file
  containing un-compileable Python code.

  The bad code block just gets skipped.
  """

  mydoc = """\
```python .important foo=bar
import
print
```
bar
```python
print(2)
```
"""

  with TemporaryDirectory() as tmpdirname:
    infile = f"{tmpdirname}/tmp.pmd"
    outfile = f"{tmpdirname}/tmp.md"

    with open(infile, "w", encoding="utf8") as ofp:
      ofp.write(mydoc)

    res = cli_twine(infile, outfile)
    with open(outfile, "r", encoding="utf8") as ofp:
      actual_output = ofp.read()

    expected_output = 'bar\n2\n'

    assert res == TwineExitStatus.BLOCK_COMPILATION_ERROR
    assert actual_output == expected_output





