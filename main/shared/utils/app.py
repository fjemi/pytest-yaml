#!.venv/bin/python3
# -*- coding: utf-8 -*-


import asyncio
import dataclasses as dc
import inspect
import os
from typing import Any, Callable, Iterable, List

from error_handler.app import main as error_handler
from get_config.app import main as get_config
from get_value.app import main as get_value


MODULE = __file__
CONFIG = get_config(module=MODULE)

LOCALS = locals()


@dc.dataclass
class Data_Class:
  pass


@error_handler()
async def get_function_parameters(function: Callable) -> List[str]:
  return list(inspect.signature(function).parameters)


@error_handler()
async def process_arguments(
  locals: dict | None = None,
  data_class: Data_Class | None = None,
) -> Data_Class:
  conditions = inspect.isclass(data_class)
  if conditions:
    data_class = data_class()

  for key, value in locals.items():
    conditions = [
      value is None,
      hasattr(data_class, key) is False, ]
    if True in conditions:
      continue

    setattr(data_class, key, value, )
    locals[key] = None

  return data_class


@error_handler()
async def set_field_value(
  kind: str,
  data: dict | Data_Class,
  field: str,
  value: Any,
) -> Data_Class | dict:
  if kind == 'dict':
    data[field] = value
  elif kind == 'object':
    setattr(data, field, value)
  return data


@error_handler()
async def get_task_from_event_loop(
  task: Any | None = None
) -> Any:
  condition = inspect.iscoroutine(task)
  if not condition:
    return task

  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)

  try:
    task = loop.run_until_complete(task)
  finally:
    loop.close()
    asyncio.set_event_loop(None)

  return task


def get_range_from_integer(
  n: int | Iterable | None = None,
) -> Iterable | None:
  kind = type(n).__name__.lower()

  if kind == 'range':
    return n
  if kind == 'nonetype':
    return range(1)
  elif kind == 'int':
    return range(n)


@error_handler()
async def process_operations(
  operations: List[str] | None = None,
  data: dict | Data_Class | None = None,
  functions: dict | None = None,
  n: int | Iterable | None = None,
) -> List[Any]:
  operations = CONFIG.schema.Operations(names=operations)
  kind = 'dict' if isinstance(data, dict) else 'object'
  n = get_range_from_integer(n=n)

  for i in n:
    for operation in operations.names:
      operations.function = functions[operation]
      operations.parameters = get_function_parameters(
        function=operations.function, )

      operations.fields = {}
      for parameter in operations.parameters:
        operations.fields[parameter] = get_value(data, parameter, None)

      task = operations.function(**operations.fields)
      operations.result = get_task_from_event_loop(task=task)

      operations.result = operations.result or {}
      for field, value in operations.result.items():
        data = set_field_value(
          data=data,
          field=field,
          value=value,
          kind=kind, )

  return data


@error_handler()
async def get_parent_module(
  parent_filename: str | None = None,
  module: str | None = None,
  resources_folder_name: str | None = None,
) -> str:
  index = module.find(resources_folder_name)
  directory = module[:index]
  if not parent_filename:
    parent_filename = os.path.split(module)[-1]
  return os.path.join(directory, parent_filename)


def example() -> None:
  from invoke_pytest.app import main as invoke_pytest


  invoke_pytest(project_directory=MODULE)


if __name__ == '__main__':
  example()
