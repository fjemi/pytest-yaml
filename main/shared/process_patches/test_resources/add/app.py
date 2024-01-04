#!.venv/bin/python3
# -*- coding: utf-8 -*-


import dataclasses as dc


MODULE = __file__

LOCALS = locals()


@dc.dataclass
class Data:
  a: int = 0
  b: int = 0


def add_numbers(locals_: dict) -> int:
  return locals_['a'] + locals_['b']


def add_dataclass(locals_: dict) -> int:
  data = locals_['data']
  return data.a + data.b


MAIN = {
  'dataclass': add_dataclass,
  'int': add_numbers,
}


def main(
  data: Data | dict | None = None,
  a: int | float | None = None,
  b: int | float | None = None,
) -> int:
  case_ = 'dataclass' if data else 'numbers'
  function_ = f'add_{case_}'
  function_ = LOCALS[function_]
  data = function_(locals_=locals())
  return data


def example() -> None:
  import utils.app as utils
  from invoke_pytest.app import main as invoke_pytest


  parent_module = utils.get_parent_module(
    module=MODULE,
    resource_folder_name='test_resources', )
  invoke_pytest(project_directory=parent_module)


if __name__ == '__main__':
  example()
