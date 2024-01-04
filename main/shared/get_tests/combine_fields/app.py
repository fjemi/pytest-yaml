#!.venv/bin/python3
# -*- coding: utf-8 -*-


import dataclasses as dc
from typing import Any, List

from error_handler.app import main as error_handler
from get_config.app import main as get_config


MODULE = __file__
CONFIG = get_config(module=MODULE)

LOCALS = locals()


@error_handler()
async def combine_parent_any_and_child_any(
  parent: Any,
  child: Any,
) -> List[Any]:
  return [
    parent,
    child, ]


@error_handler()
async def combine_parent_any_and_child_list(
  parent: Any,
  child: Any,
) -> List[Any]:
  return [parent, *child]


@error_handler()
async def combine_parent_any_and_child_nonetype(
  parent: Any,
  # trunk-ignore(ruff/ARG001)
  child: Any,
) -> List[Any]:
  return [parent]


@error_handler()
async def combine_parent_nonetype_and_child_nonetype(
  # trunk-ignore(ruff/ARG001)
  parent: Any,
  # trunk-ignore(ruff/ARG001)
  child: Any,
) -> List[Any]:
  return []


@error_handler()
async def combine_parent_nonetype_and_child_any(
  # trunk-ignore(ruff/ARG001)
  parent: Any,
  child: Any,
) -> List[Any]:
  return [child]


@error_handler()
async def combine_parent_nonetype_and_child_list(
  # trunk-ignore(ruff/ARG001)
  parent: Any,
  child: Any,
) -> List[Any]:
  return child


@error_handler()
async def combine_parent_nonetype_and_child_dict(
  # trunk-ignore(ruff/ARG001)
  parent: Any,
  child: Any,
) -> List[Any]:
  return [child]


@error_handler()
async def combine_parent_dict_and_child_dict(
  parent: dict,
  child: dict,
) -> list:
  return [
    parent,
    child, ]


@error_handler()
async def combine_parent_dict_and_child_nonetype(
  parent: Any,
  # trunk-ignore(ruff/ARG001)
  child: Any,
) -> List[Any]:
  return [parent]


@error_handler()
async def combine_parent_dict_and_child_list(
  parent: Any,
  child: Any,
) -> List[Any]:
  return [parent, *child]



@error_handler()
async def combine_parent_list_and_child_nonetype(
  parent: Any,
  # trunk-ignore(ruff/ARG001)
  child: Any,
) -> List[Any]:
  return parent


@error_handler()
async def combine_parent_list_and_child_any(
  parent: Any,
  child: Any,
) -> List[Any]:
  parent.append(child)
  return parent


@error_handler()
async def combine_parent_list_and_child_list(
  parent: Any,
  child: Any,
) -> List[Any]:
  return parent + child


@error_handler()
async def combine_parent_list_and_child_dict(
  parent: Any,
  child: Any,
) -> List[Any]:
  parent.append(child)
  return parent


@dc.dataclass
class Data_Class:
  pass


@error_handler()
async def get_kinds(
  parent: Any,
  child: Any,
) -> Data_Class:
  kinds = CONFIG.schema.Kinds()

  for key, value in locals().items():
    kind = type(value).__name__.lower()

    if kind == 'tuple':
      kind = 'list'
    if kind not in CONFIG.field_kinds:
      kind = 'any'

    setattr(kinds, key, kind)

  return kinds


@error_handler()
async def main(
  parent: Any | None = None,
  child: Any | None = None,
) -> List[Any]:
  kinds = get_kinds(
    parent=parent,
    child=child, )
  handler = f'combine_parent_{kinds.parent}_and_child_{kinds.child}'
  handler = LOCALS[handler]
  return handler(
    parent=parent,
    child=child, )


def example() -> None:
  from invoke_pytest.app import main as invoke_pytest


  invoke_pytest(project_directory=MODULE)


if __name__ == '__main__':
  example()
