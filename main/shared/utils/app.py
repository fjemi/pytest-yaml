#!.venv/bin/python3
# -*- coding: utf-8 -*-


from __future__ import annotations

import asyncio
import dataclasses as dc
import inspect
from typing import Any, Callable, List

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


@error_handler()
async def process_operations(
  operations: List[str] | None = None,
  data: dict | Data_Class | None = None,
  functions: dict | None = None,
  n: int | None = None,
) -> List[Any]:
  operations = CONFIG.schema.Operations(names=operations)
  n = range(1) if not n else range(n)
  kind = 'dict' if isinstance(data, dict) else 'object'

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

      for field, value in operations.result.items():
        data = set_field_value(
          data=data,
          field=field,
          value=value,
          kind=kind, )

  return data


def example() -> None:
  from invoke_pytest.app import main as invoke_pytest


  invoke_pytest(project_directory=MODULE)


if __name__ == '__main__':
  example()