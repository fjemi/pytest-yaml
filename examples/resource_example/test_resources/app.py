#!.venv/bin/python3
# -*- coding: utf-8 -*-


# ${ROOT_DIR}/examples/resources_example/test_resources/app.py


import dataclasses as dc
from typing import Any


@dc.dataclass
class Data:
  a: int | float
  b: int | float
  result: int | float | None = None


def assert_type(
  output: Any | None = None,
  expected: Any | None = None,
) -> dict:
  output = type(output).__name__
  passed = output == expected
  return {
    'output': output,
    'expected': expected,
    'passed': passed, }
