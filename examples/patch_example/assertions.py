#!.venv/bin/python3
# -*- coding: utf-8 -*-


# ${ROOT_DIR}/examples/patch_example/assertions.py


from typing import Any, Callable


def equals(
  output: Any | None = None,
  expected: Any | None = None,
) -> dict:
  passed = output == expected
  return {
    'output': output,
    'expected': expected,
    'passed': passed, }


def function_calls(
  output: Callable | None = None,
  expected: Any | None = None,
) -> dict:
  store = []
  n = expected.get('n')
  keys = expected.get('keys')

  if n:
    n = range(n)
    for i in n:
      store.append(output())
  elif keys:
    for key in keys:
      store.append(output(key))

  output = store
  expected = expected.get('results', [])
  passed = output == expected

  return {
    'output': output,
    'expected': expected,
    'passed': passed, }
