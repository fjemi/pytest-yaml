#!.venv/bin/python3
# -*- coding: utf-8 -*-


import asyncio
import dataclasses as dc
import inspect
import json
import logging
import os
import time
from typing import Any, Callable, List

import yaml
from get_config.app import main as get_config
from get_value.app import main as get_value


MODULE = __file__
CONFIG = get_config(module=MODULE)
LOCALS = locals()

LOGGERS = {}


@dc.dataclass
class Data_Class:
  pass


def get_task_from_event_loop(
  task: Any | None = None
) -> Any:
  conditions = [
    inspect.isawaitable(object=task),
    inspect.iscoroutine(object=task),
    inspect.iscoroutine(object=task), ]
  if True in conditions:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
      task = loop.run_until_complete(task)
    finally:
      loop.close()
      asyncio.set_event_loop(None)

  return task


def set_default(object: Any) -> Any:
  kind = type(object).__name__.lower()

  if kind == 'module':
    return object.__file__

  if kind in ['function', 'callable']:
    return object.__name__

  if isinstance(object, Exception):
    return {
      'exception': object.__class__.__name__,
      'description': str(object), }

  if kind == 'Test':
    if type(object.module).__name__.lower() == 'module':
      object.module = object.module.__file__

    if type(object.function).__name__.lower() == 'function':
      object.function = object.function.__name__

    try:
      return dc.asdict(object)
    except Exception as e:
      _ = e
      return object.__dict__

  return str(object)


async def process_arguments(
  locals: dict | None = None,
) -> Data_Class:
  locals_ = locals or {}
  data = CONFIG.schema.Data()

  for key, value in locals_.items():
    conditions = [
      value is None,
      hasattr(data, key) is False, ]
    if True in conditions:
      continue
    setattr(data, key, value)

  return data


async def format_location(
  level: str | None = None,
  enabled: bool | None = None,
) -> dict:
  if enabled in CONFIG.empty_values:
    return {'status': 'exited'}

  level = 'debug' if not level else level
  directory = CONFIG.environment.LOGS_DIR
  location = f'{level}.log'
  location = os.path.join(
    directory,
    location, )

  return {'location': location}


async def format_data(
  data: Data_Class | dict | None,
) -> dict:
  condition = dc.is_dataclass(data) is True
  if condition:
    try:
      data = dc.asdict(data)
    except Exception as e:
      _ = e
      data = data.__dict__

  return {'data': data}


async def convert_data_to_json(data: Data_Class) -> dict:
  try:
    data = json.dumps(
      data,
      default=set_default, )
  except Exception as e:
    _ = e
    data = f'{data}\n'

  return {'data': data}


async def convert_data_to_yaml(data: Data_Class) -> dict:
  try:
    data = json.dumps(
      data,
      default=set_default, )
    data = yaml.safe_load(data)
    data = yaml.dump(
      data,
      default_flow_style=False, )
  except Exception as e:
    _ = e
    data = str(data)

  return {'data': data}


async def convert_data(
  data: Data_Class | dict | None = None,
  format_: str | None = None,
) -> dict:
  function_ = f'convert_data_to_{format_}'
  function_ = LOCALS[function_]
  return await function_(data=data)


LOGGING_LEVELS = {
  'debug': logging.DEBUG,
  'info': logging.INFO,
  'exception': logging.ERROR, }


async def format_level(
  level: str | None = None,
  enabled: bool | None = None,
) -> dict:
  if enabled in CONFIG.empty_values:
    return {'status': 'exited'}

  level = str(level).lower()
  level = get_value(
    LOGGING_LEVELS,
    level,
    logging.DEBUG, )

  return {'level': level}


async def create_logger(
  location: str | None = None,
  level: int | None = None,
) -> logging.Logger:
  logger = logging.getLogger(location)
  logger.setLevel(level)
  handler = logging.FileHandler(location)
  formatter = logging.Formatter('%(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  return logger


async def log_data(
  location: str | None = None,
  level: int | None = None,
  data: Any | None = None,
  enabled: bool | None = None,
) -> dict:
  if enabled in CONFIG.empty_values:
    return {'status': 'exited'}

  global LOGGERS
  if location not in LOGGERS:
    LOGGERS[location] = await create_logger(
      location=location,
      level=level, )
  logger = LOGGERS[location]
  logger.info(data)

  return {'status': 'success'}


TRUE_VALUES = ['1', 'true', 1, 'True', True]


async def output_to_terminal(
  data: Data_Class | dict,
  standard_output: bool | None = None,
) -> dict:
  debug = CONFIG.environment.DEBUG.lower()
  standard_output = str(standard_output).lower()
  status = 'exited'

  conditions = [
    debug not in CONFIG.empty_values,
    standard_output not in CONFIG.empty_values, ]
  if True in conditions:
    status = 'success'
    print(data)

  return {'status': status}


def get_function_parameters(function: Callable) -> List[str]:
  return list(inspect.signature(function).parameters)


async def main(
  data: Any | None = None,
  format_: str = 'yaml',
  level: str | None = None,
  location: str | None = None,
  timestamp: int | None = None,
  standard_output: bool = False,
  enabled: bool = True,
) -> dict:
  timestamp = int(time.time()) if not timestamp else timestamp
  data = await process_arguments(locals=locals())

  # data = utils.process_operations(
  #   data=data,
  #   functions=LOCALS,
  #   operations=CONFIG.operations, )
  # Cannot use `utils.process_operations` because
  # of circular references

  for operation in CONFIG.operations:
    function_ = LOCALS[operation]
    parameters = get_function_parameters(function=function_)
    fields = {}
    for parameter in parameters:
      fields[parameter] = getattr(data, parameter, None)
    result = await function_(**fields)
    for key, value in result.items():
      setattr(data, key, value)

  return {'status': data.status}


def example() -> None:
  from invoke_pytest.app import main as invoke_pytest


  invoke_pytest(project_directory=MODULE)


if __name__ == '__main__':
  example()
