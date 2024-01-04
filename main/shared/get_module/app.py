#!.venv/bin/python3
# -*- coding: utf-8 -*-


import dataclasses as dc
import importlib
import importlib.util  # as importlib_util
import os
from types import ModuleType

from error_handler.app import (
  main as error_handler,
)
from get_config.app import main as get_config
from utils import app as utils


MODULE = __file__
CONFIG = get_config(module=MODULE)
LOCALS = locals()

POOL = {}


@dc.dataclass
class Data_Class:
  pass


@error_handler()
async def format_module_name(
  name: str | None = None,
  location: str | None = None,
) -> dict:
  if name not in CONFIG.empty_values:
    return {'name': name.replace('.py', '')}

  if location in CONFIG.empty_values:
    return {'name': 'app'}

  name = location.replace('.py', '')
  name = name.split(os.sep)
  return {'name': '.'.join(name)}


@error_handler()
async def get_module_from_pool(
  location: str,
  pool: bool
) -> dict:
  module = None

  if pool:
    module = POOL.get(location, None)

  return {'module': module}




@error_handler()
async def get_module_from_location(
  location: str | None = None,
  name: str | None = None,
  module: ModuleType | None = None,
) -> dict:
  kind = type(module).__name__.lower()
  condition = kind == 'module'
  if condition:
    return {'module': module}

  location = str(location)
  if os.path.exists(location) is False:
    return {}

  spec = importlib.util.spec_from_file_location(
    name=name,
    location=location, )
  module = importlib.util.module_from_spec(spec)

  try:
    spec.loader.exec_module(module)
  finally:
    return {'module': module}


@error_handler()
async def add_module_to_pool(
  module: ModuleType,
  location: str,
  pool: bool,
) -> dict:
  conditions = [
    pool in CONFIG.empty_values,
    module in CONFIG.empty_values, ]
  if True not  in conditions:
    global POOL
    POOL[location] = module
  return {}


@error_handler()
async def main(
  location: str | None = None,
  name: str | None = None,
  pool: bool = True,
) -> ModuleType | None:
  data = utils.process_arguments(
    data_class=CONFIG.schema.Data,
    locals=locals(), )
  data = utils.process_operations(
    functions=LOCALS,
    operations=CONFIG.operations,
    data=data, )
  return data.module


@error_handler()
def example() -> None:
  from invoke_pytest.app import main as invoke_pytest


  invoke_pytest(project_directory=MODULE)


if __name__ == '__main__':
  example()
