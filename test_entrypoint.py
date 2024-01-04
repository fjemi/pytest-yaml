#!.venv/bin/python3
# -*- coding: utf-8 -*-


import dataclasses as dc

import pytest
import yaml


MODULE = __file__

LOCALS = locals()
UNNAMED_TEST_COUNT = 0


@dc.dataclass
class Data_Class:
  pass


def get_ids(test: Data_Class) -> str:
  id_ = getattr(test, 'id_short', None)
  if not id_:
    global UNNAMED_TEST_COUNT
    UNNAMED_TEST_COUNT += 1
    id_ = f'test_{UNNAMED_TEST_COUNT}'
  return id_


def verify_assertions(assertions: list | None = None) -> int | None:
  assertions = assertions or []

  for assertion in assertions:
    output = assertion.output
    expected = assertion.expected

    try:
      output = yaml.dump(output)
      expected = yaml.dump(expected)
    finally:
      # trunk-ignore(bandit/B101)
      assert expected == output

  return 1


@pytest.mark.parametrize(
  argnames='test',
  ids=lambda test: get_ids(test=test),
  argvalues=pytest.yaml_tests, )
def test_(test: Data_Class) -> None:
  assertions = getattr(test, 'assertions', [])
  verify_assertions(assertions=assertions)


def example() -> None:
  from invoke_pytest.app import main as invoke_pytest


  invoke_pytest(project_directory=MODULE)


if __name__ == '__main__':
  example()
