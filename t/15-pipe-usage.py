#!/usr/bin/env python3
# pylint: disable=protected-access, no-self-use, invalid-name, consider-using-enumerate

"""
check that pytwine interprets input and output
arguments and flags correctly.
"""

from enum import Enum, auto
from subprocess import run, PIPE
from tempfile import TemporaryDirectory
from typing import List

import os
import sys
import pytest

DEBUG = 0

def _running_on_windows() -> bool:
  """check whether on windows"""
  return sys.platform == "win32"

def _dump(outfile_path, contents):
  with open(outfile_path, "w", encoding="utf8") as ofp:
    ofp.write(contents)

def _slurp(infile_path):
  with open(infile_path, "r", encoding="utf8") as ifp:
    return ifp.read()

pjoin = os.path.join

class FileArg(Enum):
  """placeholder for input and output"""
  INFILE  = auto()
  OUTFILE = auto()

####
# funcs that call pytwine script with various
# args, and return output:

def send_input_as_arg(infile_arg : str, stdin_conts: str):
  """ways of specifying stdin - "-" and "/dev/stdin" -
  work. (Except that Windows has no /dev/stdin.)
  """
  cmd = ["pytwine", infile_arg]
  if DEBUG:
    print("running", cmd, file=sys.stderr)
  res = run(cmd, stdout=PIPE, input=stdin_conts,
            check=True, encoding="utf8")
  return res.stdout



def send_input_no_args(stdin_conts: str) -> str:
  """call pytwine with no args - meaning input is stdin
  """
  cmd = ["pytwine"]
  if DEBUG:
    print("running", cmd, file=sys.stderr)
  res = run(cmd, stdout=PIPE, input=stdin_conts,
            check=True, encoding="utf8")
  return res.stdout

def try_output_args(stdin_conts: str, args_to_use : List[str]) -> str:
  """call pytwine with args signifying output
  should go to stdout - return contents of stdout
  """
  cmd = ["pytwine"] + list(args_to_use)
  if DEBUG:
    print("running", cmd, file=sys.stderr)
  res = run(cmd, stdout=PIPE, input=stdin_conts,
            check=True, encoding="utf8")
  return res.stdout



def try_file_args(infile_path : str, input_conts: str,
                  outfile_path : str,
                  args_to_use : List[str]
  ) -> str:
  """call pytwine with args signifying input should come from
  and output should go to named files - return contents of that file.

  Use FileArg.INFILE and FileArg.OUTFILE to stand in for final
  args (got from a temp directory)
  """
  cmd = ["pytwine"] + list(args_to_use)
  with TemporaryDirectory(prefix="pytwine-test-") as tmpdir:
    infile_path   = pjoin(tmpdir, infile_path)
    outfile_path  = pjoin(tmpdir, outfile_path)
    _dump(infile_path, input_conts)

    for i in range(0, len(cmd)):
      if cmd[i] == FileArg.INFILE:
        cmd[i] = infile_path
      elif cmd[i] == FileArg.OUTFILE:
        cmd[i] = outfile_path
    if DEBUG:
      print("running", cmd, file=sys.stderr)
    run(cmd, check=True, encoding="utf8")

    return _slurp(outfile_path)


class TestStdin:
  """test that args equivalent to stdin work"""

  def test_stdinlike_args(self):
    """test that args equivalent to stdin work"""
    args_to_try = ['-']
    if not _running_on_windows():
      args_to_try.append("/dev/stdin")
    for infile_arg in args_to_try:
      stdin_conts   = "foo"
      actual_output = send_input_as_arg(infile_arg, stdin_conts)
      assert actual_output == stdin_conts, f"arg {infile_arg} gives back stdin"

  def test_no_args(self):
    """providing no args should act as pipe"""
    stdin_conts   = "bar"
    actual_output = send_input_no_args(stdin_conts)
    assert actual_output == stdin_conts, "no args gives back stdin"

class TestStdout:
  """test that args equivalent to stdout work"""

  def test_stdout_args(self):
    """test that args equivalent to stdout work"""
    stdin_conts   = "bar"
    arglists_to_try = [
        ("-", "-"),
        ("--output", "-"),
        ("--output", "-", "-")
      ]
    if not _running_on_windows():
      arglists_to_try += [
        ("--output", "/dev/stdout"),
        ("--output", "/dev/stdout", "-")
      ]

    for arglist in arglists_to_try:
      actual_output = try_output_args(stdin_conts, arglist)
      assert actual_output == stdin_conts, "no args gives back stdin"


class TestFiles:
  """test that pytwine works when both infile and outfile specified"""

  def test_named_file_args(self):
    """test that args equivalent to stdout work"""
    infile_name   = "some_infile"
    infile_conts  = "wuz"
    outfile_name  = "some_outfile"

    arglists_to_try = [
        (FileArg.INFILE, FileArg.OUTFILE),
        ('--output', FileArg.OUTFILE, FileArg.INFILE),
      ]

    for arglist in arglists_to_try:
      actual_output = try_file_args(infile_name, infile_conts, outfile_name,
                                    arglist)
      assert actual_output == infile_conts, "output file should equal infile"

MAIN = "__main__"
#MAIN = None
if __name__ == MAIN:
  sys.exit(pytest.main(["--tap-stream", __file__]))


# vim: syntax=python :
