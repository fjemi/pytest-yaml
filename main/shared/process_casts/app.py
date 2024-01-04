#!.venv/bin/python3
# -*- coding: utf-8 -*-


import dataclasses as dc
from types import ModuleType
from typing import Any, List

from error_handler.app import main as error_handler
from get_config.app import main as get_config
from get_object.app import main as get_object
from process_casts.cast_handlers.app import main as cast_handlers
from utils import app as utils


MODULE = __file__
CONFIG = get_config(module=MODULE)
LOCALS = locals()


@dc.dataclass
class Data_Class:
  pass


@error_handler()
async def get_caster(
  module: ModuleType | None = None,
  cast: dict | None = None,
) -> dict:
  caster = cast.get('caster', None)
  if not caster:
    return {'caster': None}

  caster = get_object(parent=module, name=caster)
  return {'caster': caster}


@error_handler()
async def get_object_to_cast(
  object: Any | None = None,
  cast: dict | None = None,
) -> dict | None:
  field = cast.get('field', None)

  conditions = [not field, not object]
  if True in conditions:
    return {
      'field': field,
      'casted_object': object, }

  casted_object = get_object(parent=object, name=field)
  return {
    'field': field,
    'casted_object': casted_object}


@error_handler()
async def get_kinds(
  casted_object: Any | None = None,
  object: Any | None = None,
  caster: Any | None = None,
) -> dict:
  locals_ = locals()
  kinds = CONFIG.schema.Kinds()

  for key, value in locals_.items():
    kind = type(value).__name__.lower()
    kind = 'dataclass' if dc.is_dataclass(value) else kind
    kind = 'list' if kind == 'tuple' else kind

    valid_kinds = f'{key}_kinds'
    valid_kinds = getattr(
      CONFIG,
      valid_kinds,
      [], )
    if kind not in valid_kinds:
      kind = 'any'

    setattr(kinds, key, kind)

  return {'kinds': kinds}


@error_handler()
async def cast_object(
  casted_object: Any | None = None,
  object: Any | None = None,
  caster: Any | None = None,
  unpack: bool | None = None,
  kinds: Data_Class | None = None,
  field: str | None = None,
) -> dict:
  unpack = 'packed' if unpack in CONFIG.empty_values else 'unpacked'
  object_ = object

  handler = f'cast_{kinds.casted_object}_{unpack}_to_{kinds.caster}'
  handler = cast_handlers(handler=handler)
  casted_object = handler(
    object=casted_object,
    caster=caster, )

  conditions = [
    'whole' if field in CONFIG.empty_values else 'part',
    'dict' if isinstance(object_, dict) else 'object', ]
  conditions = '.'.join(conditions)

  if conditions in ['whole.dict', 'whole.object', ]:
    object_ = casted_object
  elif conditions == 'part.dict':
    object_[field] = casted_object
  elif conditions == 'part.object':
    setattr(object_, field, casted_object)

  return {
    'n': None,
    'i': None,
    'field': None,
    'caster': None,
    'unpack': None,
    'kinds': None,
    'casted_object': None,
    'object': object_, }


CAST_OBJECT_FIELDS = ['caster', 'field', 'unpack']


@error_handler()
async def process_casts_for_arguments(
  cast_arguments: List[dict] | None = None,
  arguments: dict | None = None,
  module: ModuleType | None = None,
) -> dict:
  if not cast_arguments:
    return {}
  return main(
    arguments=arguments,
    cast_arguments=cast_arguments,
    module=module,
    object_key='arguments', )


@error_handler()
async def process_casts_for_output(
  cast_output: List[dict] | None = None,
  output: dict | None = None,
  module: ModuleType | None = None,
) -> dict:
  if not cast_output:
    return {}
  return main(
    output=output,
    cast_output=cast_output,
    module=module,
    object_key='output', )


@error_handler()
async def main(
  cast_arguments: List[dict] | None = None,
  arguments: dict | None = None,
  output: Any | None = None,
  cast_output: List[dict] | None = None,
  module: ModuleType | None = None,
  object_key: str | None = None,
) -> dict:
  if not cast_arguments and not cast_output:
    return {}

  data = utils.process_arguments(
    data_class=CONFIG.schema.Data,
    locals=locals(), )
  data.casts_key = f'cast_{data.object_key}'
  data.casts = getattr(data, data.casts_key, [])
  setattr(data, data.casts_key, None)
  locals()[data.casts_key] = None
  data.n = range(len(data.casts))
  data.object = getattr(data, data.object_key, None)
  setattr(data, data.object_key, None)
  locals()[data.object_key] = None

  for i in data.n:
    data.cast = data.casts[i]
    data = utils.process_operations(
      functions=LOCALS,
      data=data,
      operations=CONFIG.operations, )

  return {
    data.casts_key: None,
    data.object_key: data.object, }


def example() -> None:
  from invoke_pytest.app import main as invoke_pytest


  invoke_pytest(project_directory=MODULE)


if __name__ == '__main__':
  example()
