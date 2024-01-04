#!.venv/bin/python3
# -*- coding: utf-8 -*-


import copy
import dataclasses as dc
import os
from typing import Any, List

import yaml as py_yaml
from error_handler.app import main as error_handler
from get_config.app import main as get_config

# trunk-ignore(ruff/F401)
from get_tests.collate_tests.app import main as collate_tests
from get_tests.combine_fields.app import main as combine_fields

# trunk-ignore(ruff/F401)
from get_tests.format_tests.app import main as format_tests
from utils import app as utils


MODULE = __file__
CONFIG = get_config(module=MODULE)
LOCALS = locals()


@error_handler()
async def merge_global_and_test_configs(
  tests: list | None = None,
  globals: dict | None = None,
  module: str | None = None,
  module_location: str | None = None,
  yaml: str | None = None,
  resources: List[str] | str | None = None,
) -> dict:
  resources = resources or []

  globals_ = globals or {}
  global_resources = globals_.get('resources') or []
  resources = resources + global_resources
  globals_.update({
    'module': module,
    'module_location': module_location,
    'yaml': yaml,
    'resources': resources, })

  tests = tests or []
  n  = range(len(tests))

  for i in n:
    fields = list(globals_.keys())

    for field in fields:
      child = tests[i].get(field, None)
      parent = globals_.get(field, None)
      parent = copy.deepcopy(parent)
      tests[i][field] = combine_fields(
        parent=parent,
        child=child, )

  return {
    'tests': tests,
    'globals': None, }


@dc.dataclass
class Data_Class:
  pass


YAML_FIELDS = {
  'globals':{},
  'tests': [], }


@error_handler(default_value={})
async def parse_content(
  content: Any | None = None,
) -> dict:
  if content in CONFIG.empty_values:
    content = {}

  store = {}
  for field, default in YAML_FIELDS.items():
    value = content.get(field)
    store[field] = value if value else default

  return store


@error_handler()
async def get_content(yaml: str | list | None = None) -> dict:
  if isinstance(yaml, list):
    yaml = yaml[0]

  yaml = str(yaml)
  condition = os.path.isfile(yaml) is False
  if condition:
    content = {}

  if not condition:
    with open(
      file=yaml,
      encoding='utf-8',
      mode='r',
    ) as file:
      stream = file.read()
      stream = os.path.expandvars(stream)
      content = py_yaml.safe_load(stream=stream)
      content = content if content else {}

  return {'content': content}


@error_handler()
async def main(
  yaml: str | None = None,
  module: str | None = None,
  module_location: str | None = None,
  resources: List[str] | None = None,
) -> dict:
  data = utils.process_arguments(
    locals=locals(),
    data_class=CONFIG.schema.Data, )
  data = utils.process_operations(
    operations=CONFIG.operations,
    functions=LOCALS,
    data=data, )
  return {'tests': data.tests}


def example() -> None:
  from invoke_pytest.app import main as invoke_pytest


  invoke_pytest(project_directory=MODULE)


if __name__ == '__main__':
  example()
