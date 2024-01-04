#!.venv/bin/python3
# -*- coding: utf-8 -*-


import os
import time
from types import ModuleType
from typing import Callable, List

from error_handler.app import main as error_handler
from get_config.app import main as get_config

# trunk-ignore(ruff/F401)
from get_locations.app import main as get_locations
from get_module.app import main as get_module
from get_tests.app import main as get_tests
from logger.app import main as logger

# trunk-ignore(ruff/F401)
from process_assertions.app import main as process_assertions

# trunk-ignore(ruff/F401)
from process_casts import app as process_casts
from process_casts.app import (
  # trunk-ignore(ruff/F401)
  process_casts_for_arguments,
  # trunk-ignore(ruff/F401)
  process_casts_for_output,
)

# trunk-ignore(ruff/F401)
from process_patches.app import main as process_patches
from run_multiple_threads.app import main as run_multiple_threads

# trunk-ignore(ruff/F401)
from set_environment.app import main as set_environment
from utils import app as utils
from utils.app import Data_Class


MODULE = __file__
CONFIG = get_config(module=MODULE)
LOCALS = locals()


@error_handler()
async def handle_module(
  module: str | list | None = None,
  module_location: str | None = None,
) -> dict:
  if isinstance(module_location, list):
    module_location = module_location[0]

  if isinstance(module, list):
    module = module[0]

  module = get_module(
    location=module,
    name=module_location,
    pool=False, )

  if module is None:
    module = ''

  return {'module': module}


@error_handler()
async def handle_resources(
  module: ModuleType | None = None,
  resources: List[str] | None = None,
) -> dict:
  resources = resources or []
  visited = []

  for location in resources:
    extension = os.path.splitext(location)[1]
    conditions = [
      os.path.exists(location),
      extension in CONFIG.module_extensions,
      location not in visited, ]
    if False in conditions:
      continue

    visited.append(location)

    resource = get_module(
      location=location,
      pool=False, )

    routes = {
      'module': module.__file__,
      'resource': resource.__file__, }
    for key, value in routes.items():
      # trunk-ignore(ruff/PLW2901)
      value = value.replace(f'{os.sep}{os.sep}', os.sep)
      # trunk-ignore(ruff/PLW2901)
      value = value.split(os.sep)
      routes[key] = value

    # Get the tree or dot-delimited path to the resource
    tree = CONFIG.schema.Tree(**routes)

    start = 0
    n = range(len(tree.resource))

    for i in n:
      if not tree.resource[i]:
        continue

      if tree.resource[i] != tree.module[i]:
        start = i
        break
    tree = tree.resource[start:]

    # Add resource to module
    parent = module
    for path in tree[:-1]:
      if hasattr(parent, path) is False:
        setattr(
          parent,
          path,
          Data_Class(), )
      parent = getattr(parent, path)
    name = tree[-1].replace('.py', '')
    setattr(parent, name, resource)

  return {
    'resources': None,
    'module': module, }


@error_handler()
async def get_function_output(
  function: Callable | None = None,
  arguments: dict | None = None,
) -> dict:
  output = None
  exception = None
  arguments = arguments or {}

  try:
    output = function(**arguments)
  except Exception as e:
    exception = e

  output = utils.get_task_from_event_loop(task=output)
  exception = utils.get_task_from_event_loop(task=exception)

  return {
    'exception': exception,
    'output': output, }


@error_handler()
async def get_function(
  function: str | None = None,
  module: ModuleType | None = None,
  module_location: str | None = None,
) -> dict | None:
  function_ = function or ''

  kind = type(module_location).__name__.lower()
  if kind == 'list':
    module_location = module_location[-1]
  elif kind == 'nonetype':
    module_location = ''

  data = [{'function': function_, 'module': module_location}]
  task = logger(data=data, standard_output=True)
  utils.get_task_from_event_loop(task=task)

  function_ = getattr(module, function_, None, )
  return {'function': function_}


@error_handler()
async def handle_id(
  function: Callable | None = None,
  module: ModuleType | None = None,
  description: str | list | None = None,
) -> dict:
  function_ = function
  kind = type(function_).__name__.lower()
  if kind == 'function':
    function_ = function_.__name__
  function_ = function_ or  ''

  kind = type(module).__name__.lower()
  if kind == 'module':
    module = module.__file__
  module = module or ''

  kind = type(description).__name__.lower()
  if kind not in ['list', 'nonetype']:
    description = [description]
  elif kind == 'nonetype':
    description = []

  return {
    'module': module,
    'function': function_,
    'description': description, }


@error_handler()
async def run_test_for_function(
  test: Data_Class | None = None,
) -> Data_Class:
  return utils.process_operations(
    operations=CONFIG.function_operations,
    functions=LOCALS,
    data=test, )


@error_handler()
async def run_test_handler(
  test: Data_Class | None = None,
) -> Data_Class:
  for kind in CONFIG.test_kinds:
    if isinstance(test, dict):
      test = test.get('test', {})
      test = test or {}
    if getattr(test, kind) in CONFIG.empty_values:
      continue

    handler = f'run_test_for_{kind}'
    handler = LOCALS[handler]
    return handler(test=test)


def format_timestamp(timestamp: int | List[int] | None = None) -> dict:
  kind = type(timestamp).__name__.lower()

  if kind == 'int':
    timestamp = [
      timestamp,
      int(time.time()), ]
  elif kind == 'list':
    timestamp.append(int(time.time()))
  elif kind == 'nonetype':
    timestamp = [int(time.time())]

  return {'timestamp': timestamp}


@error_handler()
async def main(
  project_directory: str | None = None,
  exclude_files: str | List[str] | None = None,
  include_files: str | List[str] | None = None,
  exclude_functions: str | List[str] | None = None,
  include_functions: str | List[str] | None = None,
  resources_folder_name: str | None = None,
  resources: str | list | None = None,
  yaml_suffix: str | None = None,
  timestamp: int | None = None,
) -> list:
  timestamp = int(time.time()) if not timestamp else timestamp

  data = utils.process_arguments(
    data_class=CONFIG.schema.Data,
    locals=locals(), )
  data = utils.process_operations(
    operations=CONFIG.main_operations,
    functions=LOCALS,
    data=data, )

  store = []

  n = range(len(data.locations))
  for i in n:
    data.tests = get_tests(**data.locations[i])
    data.tests = data.tests or []
    data.tests = run_multiple_threads(
      target=run_test_handler,
      kwargs=data.tests.get('tests', []), )
    data.tests = data.tests or []
    store.extend(data.tests)

  return store


@error_handler()
async def example() -> None:
  from invoke_pytest.app import main as invoke_pytest


  invoke_pytest(project_directory=MODULE)


if __name__ == '__main__':
  example()
