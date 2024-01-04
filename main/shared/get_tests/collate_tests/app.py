#!.venv/bin/python3
# -*- coding: utf-8 -*-


import dataclasses as dc
import os

import utils.app as utils
from error_handler.app import main as error_handler
from get_config.app import main as get_config
from get_tests.combine_fields.app import main as combine_fields


@dc.dataclass
class Data_Class:
  pass


YAML_EXTENSIONS = ['.yaml', '.yml']


def get_schema_location(
  module: str | None = None,
) -> str:
  module = module or ''
  name = os.path.splitext(module)[0]
  location = os.path.dirname(module)
  location = os.path.dirname(location)

  yaml = ''
  for extension in YAML_EXTENSIONS:
    yaml = os.path.join(location, f'{name}{extension}')
    if os.path.isfile(yaml):
      break
    yaml = ''

  return yaml


MODULE = __file__
SCHEMA = get_schema_location(module=MODULE)
CONFIG = get_config(module=MODULE, schema=SCHEMA)

LOCALS = locals()

TESTS_KEY = 'tests'
EMPTY_VALUES = [None, []]


@error_handler()
async def add_globals_to_test(
  globals: dict | None = None,
  test: dict | None = None,
) -> dict:
  if globals in CONFIG.empty_values:
    return test

  if test in CONFIG.empty_values:
    return {}

  for key in globals:
    child = test.get(key)
    import copy
    parent = globals.get(key)
    parent = copy.deepcopy(parent)
    test[key] = combine_fields(
      parent=parent,
      child=child, )

  return test


@error_handler()
async def get_tree_roots(
  tests: list | None = None,
  globals: dict | None = None,
) -> Data_Class:
  tests = tests or []
  globals = globals or {}
  tree = {}
  roots = []

  n = range(len(tests))

  for i in n:
    index = str(i)
    tree[index] = tests[i]
    roots.append(index)

  return {
    'tree': tree,
    # 'roots': roots,
    'globals': None,
    'tests': None, }


@error_handler()
async def get_child_branches(
  visited: list | None = None,
  branch_key: str | None = None,
  tree: dict | None = None,
  store: dict | None = None,
) -> Data_Class:
  visited = visited or []
  store = store or {}
  tree = tree or {}
  branch_key = branch_key or ''

  visited.append(branch_key)
  parent = tree.get(branch_key, {})
  children = parent.get('tests', {})

  if children in CONFIG.empty_values:
    return {}

  n = reversed(range(len(children)))

  for i in n:
    child_key = f'{branch_key}.{i}'
    store[child_key] = children[i]
    del children[i]

    for field in tree[branch_key]:
      if field in ['tests']:
        continue
      child_value = store[child_key].get(field)
      parent_value = parent[field]
      store[child_key][field] = combine_fields(
        child=child_value,
        parent=parent_value, )

  return store


@error_handler()
async def get_tree_branches(
  visited: list | None = None,
  roots: list | None = None,
  tree: dict | None = None,
) -> Data_Class:
  visited = visited or []
  roots = roots or []
  child_branches = {}
  branches_added = True
  tree = tree or {}

  while branches_added is True:
    branches_added = False
    store = {}

    for key in tree:
      if key in visited:
        continue

      visited.append(key)
      child_branches = get_child_branches(
        visited=visited,
        branch_key=key,
        tree=tree,
        store=store, )

      if child_branches:
        branches_added = True
        roots.append(key)
        break

    tree.update(child_branches)

  return {
    'roots': roots,
    'tree': tree,
    'visited': None, }


@error_handler()
async def prune_tree_branches(
  roots: list | None = None,
  tree: dict | None = None,
) -> Data_Class:
  roots = roots or []
  tree = tree or {}

  for root in roots:
    tree[root] = None
    del tree[root]

  tests = list(tree.values())
  return {
    'tests': tests,
    'tree': None,
    'roots': None, }


@error_handler()
async def main(
  tests: list | None = None,
) -> dict:
  data = {'tests': tests}
  data = utils.process_operations(
    operations=CONFIG.operations,
    functions=LOCALS,
    data=data, )
  return {'tests': data.get('tests', [])}


@error_handler()
async def example() -> None:
  from invoke_pytest.app import main as invoke_pytest


  invoke_pytest(project_directory=MODULE)


if __name__ == '__main__':
  example()
