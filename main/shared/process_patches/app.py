#!.venv/bin/python3
# -*- coding: utf-8 -*-


import dataclasses as dc
import time
from types import ModuleType
from typing import Any, Callable, List

from error_handler.app import main as error_handler
from get_config.app import main as get_config
from utils import app as utils


MODULE = __file__
CONFIG = get_config(module=MODULE)
LOCALS = locals()

SIDE_EFFECTS = {}


@dc.dataclass
class Data_Class:
  pass


@error_handler()
async def get_patch_for_value(
  value: Any | None = None,
  # trunk-ignore(ruff/ARG001)
  timestamp: int | None = None,
) -> Any:
  def patch(
    patch_value: Any | None = None,
  ) -> Any:
    return patch_value

  return patch(patch_value=value)


@error_handler()
async def get_patch_for_callable(
  value: Any | None = None,
  # trunk-ignore(ruff/ARG001)
  timestamp: int | None = None,
) -> Callable:
  def callable_patch(
    # trunk-ignore(ruff/ARG001)
    *args,
    # trunk-ignore(ruff/ARG001)
    **kwargs,
  ) -> Any:
    # callable patch
    return value

  return callable_patch


@error_handler()
async def get_patch_for_side_effect_list(
  value: list,
  timestamp: int,
) -> Callable:
  global SIDE_EFFECTS

  data_class = CONFIG.schema.Side_Effect_List
  SIDE_EFFECTS[timestamp] = data_class(
    value=value,
    count=0, )

  def side_effect_list_patch(
    # trunk-ignore(ruff/ARG001)
    *args,
    # trunk-ignore(ruff/ARG001)
    **kwargs,
  ) -> Any:
    n = len(SIDE_EFFECTS[timestamp].value)
    if SIDE_EFFECTS[timestamp].count == n:
      SIDE_EFFECTS[timestamp].count = 0
    SIDE_EFFECTS[timestamp].count += 1
    return SIDE_EFFECTS[timestamp].value[SIDE_EFFECTS[timestamp].count - 1]

  return side_effect_list_patch


@error_handler()
async def get_patch_for_side_effect_dict(
  value: Any,
  # trunk-ignore(ruff/ARG001)
  timestamp: int,
) -> Callable:

  def side_effect_dict_patch(key) -> Any:
    values = value
    return values[key]

  return side_effect_dict_patch


@error_handler()
async def get_patch(
  method: str | None = None,
  timestamp: int | None = None,
  value: Any | None = None,
) -> Any:
  handler = f'get_patch_for_{method}'
  handler = LOCALS[handler]
  patch = handler(
    value=value,
    timestamp=timestamp, )
  return {'patch': patch}


@error_handler()
async def get_parent_from_dict(
  parent: dict | None,
  name: str,
) -> Any:
  if name in parent:
    return parent[name]

  parent[name] = Data_Class()
  return parent[name]


@error_handler()
async def get_parent_from_object(
  parent: object,
  name: str,
) -> Any:
  if hasattr(parent, name) is False:
    setattr(parent, name, Data_Class(), )

  return getattr(parent, name)


@error_handler()
async def get_parent(
  module: ModuleType | None = None,
  name: str | None = None,
) -> Data_Class:
  data_class = CONFIG.schema.Parents
  parents = data_class(
    names=[''],
    values=[module],
    types=['object'], )

  condition = name in CONFIG.empty_values
  if not condition:
    names = name.split('.')
  elif condition:
    names = []

  for name in names:
    handler = f'get_parent_from_{parents.types[-1]}'
    handler = LOCALS[handler]

    value = handler(
      parent=parents.values[-1],
      name=name, )
    type_ = 'dict' if isinstance(value, dict) else 'object'

    parents.names.append(name)
    parents.values.append(value)
    parents.types.append(type_)

  return {'parents': parents}


@error_handler()
async def patch_object_in_dict(
  parents: Any | None = None,
  patch: Any | None = None,
) -> Data_Class:
  n = len(parents.values)

  if n != 1:
    value = {parents.names[-1]: patch}
    parents.values[-2].update(value)
  elif n == 1:
    parents.values[-1] = patch

  return {
    'parents': parents,
    'patch': None, }


@error_handler()
async def patch_object_in_object(
  parents: Any | None = None,
  patch: Any | None = None,
) -> Data_Class:
  n = len(parents.values)

  if n != 1:
    setattr(
      parents.values[-2],
      parents.names[-1],
      patch, )
  elif n == 1:
    parents.values[-1] = patch

  return {
    'parents': parents,
    'patch': None, }


@error_handler()
async def patch_object_in_nonetype(
  # trunk-ignore(ruff/ARG001)
  parents: Any | None = None,
  # trunk-ignore(ruff/ARG001)
  patch: Any | None = None,
) -> Data_Class:
  return {
    'parents': None,
    'patch': None, }


@error_handler()
async def patch_object(
  parents: Any | None = None,
  patch: Any | None = None,
) -> dict:
  parent = 'nonetype'
  if hasattr(parents, 'types'):
    parent = parents.types[-2]

  handler = f'patch_object_in_{parent}'
  handler = LOCALS[handler]
  return handler(
    parents=parents,
    patch=patch, )


@error_handler()
async def main(
  patches: List[dict] | None = None,
  module: ModuleType | None = None,
) -> dict:
  patches = patches or []
  n = range(len(patches))

  for i in n:
    timestamp = int(time.time())
    patches[i].update({
      'module': module,
      'timestamp': timestamp, })
    patches[i] = utils.process_arguments(
      data_class=CONFIG.schema.Data,
      locals=patches[i], )
    patches[i] = utils.process_operations(
      operations=CONFIG.operations,
      functions=LOCALS,
      data=patches[i], )
    module = patches[i].module

  return {
    'module': module,
    'patches': None, }


@error_handler()
async def example() -> None:
  from invoke_pytest.app import main as invoke_pytest


  invoke_pytest(project_directory=MODULE)


if __name__ == '__main__':
  example()
