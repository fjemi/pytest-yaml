#!.venv/bin/python3
# -*- coding: utf-8 -*-


# ${ROOT_DIR}/examples/resources_example/resource.py


import dataclasses as dc
from typing import Any


@dc.dataclass
class Data:
  a: int | float
  b: int | float
  result: int | float | None = None


def assert_equals(
  output: Any | None = None,
  expected: Any | None = None,
) -> dict:
  passed = output == expected
  return {
    'output': output,
    'expected': expected,
    'passed': passed, }
