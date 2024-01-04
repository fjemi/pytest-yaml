#!.venv/bin/python3
# -*- coding: utf-8 -*-


# ${ROOT_DIR}/examples/patch_example/app.py


import dataclasses as dc
import sys
from types import ModuleType
from typing import Any


MODULE = __name__
LOCALS = locals()


@dc.dataclass
class Data:
  field: Any | None = None


STRING = 'string'
NUMBER = 1
DICTIONARY = {'key': 'value'}
LIST = [0, 1, 2, 3]
DATA = Data()
TEMP = None


def function_() -> str:
  return 'FUNCTION'


def get_object(name: str | None) -> Any:
  name = str(name)
  return LOCALS.get(name, None)


def get_this_module() -> ModuleType:
  return sys.modules[MODULE]
