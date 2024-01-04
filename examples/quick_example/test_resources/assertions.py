#!.venv/bin/python3
# -*- coding: utf-8 -*-


# ${ROOT_DIR}/examples/quick_example/test_resources/assertions.py


def equals(output, expected) -> dict:
  '''Use `test_resources.assertions.equals` in YAML file to access method'''
  passed = expected == output
  return {
    'passed': passed,
    'output': output,
    'expected': expected, }
