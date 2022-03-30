
"""
test cli-level functions, found in pytwine.cli
"""

from tempfile import TemporaryDirectory

from pytwine.core       import TwineExitStatus
from pytwine.cli        import cli_twine

def _dump(contents : str, filename : str) -> None:
  """dump string to file"""
  with open(filename, "w", encoding="utf8") as ofp:
    ofp.write(contents)

def _slurp(filename : str) -> str:
  """read string from file"""
  with open(filename, "r", encoding="utf8") as ifp:
    return ifp.read()

def _run_twine(infile_path: str, outfile_path: str) -> TwineExitStatus:
  with open(infile_path, "r", encoding="utf8") as ifp:
    with open(outfile_path, "w", encoding="utf8") as ofp:
      return cli_twine(ifp, ofp)



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
    infile_path   = f"{tmpdirname}/tmp.pmd"
    outfile_path  = f"{tmpdirname}/tmp.md"

    _dump(mydoc, infile_path)
    res = _run_twine(infile_path, outfile_path)
    actual_output = _slurp(outfile_path)
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
    infile_path = f"{tmpdirname}/tmp.pmd"
    outfile_path = f"{tmpdirname}/tmp.md"

    _dump(mydoc, infile_path)
    res = _run_twine(infile_path, outfile_path)
    actual_output = _slurp(outfile_path)
    expected_output = 'aaa\nbar\n2\n'
    expected_output = 'bar\n2\n'

    assert res == TwineExitStatus.BLOCK_COMPILATION_ERROR
    assert actual_output == expected_output





