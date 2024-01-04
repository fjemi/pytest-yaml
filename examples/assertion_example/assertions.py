#!.venv/bin/python3
# -*- coding: utf-8 -*-


# ${ROOT_DIR}/examples/assertions_example/assertions.py


from typing import Any


def assert_equals(
  output: Any | None = None,
  expected: Any | None = None,
) -> dict:
  passed = output == expected
  return {
    'passed': passed,
    'output': output,
    'expected': expected, }


def assert_exception(
  exception: str | None = None,
  expected: str | None = None,
) -> dict:
  output = type(exception).__name__
  passed = expected == output
  return {
    'passed': passed,
    'output': output,
    'expected': expected, }
