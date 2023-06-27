#!/usr/bin/env python3

import dataclasses as dc
import os
from typing import Dict

import yaml


@dc.dataclass
class Body:
  config: dict | None = None
  module_path: str | None = None
  yml_path: str | None = None
  environment_key: str = 'environment'


@dc.dataclass
class Env:
  ...


@dc.dataclass
class Data:
  body: Body | None = None
  response: Env | dict | None = None


def format_arguments(_locals: dict) -> Data:
  body = Body()
  for field in dc.fields(body):
    value = _locals[field.name]
    if not value:
      continue
    setattr(body, field.name, value)

  data = Data(body=body)
  return data


def get_yml_path(
  module_path: str | None = None,
  yml_path: str | None = None,
) -> str:
  if yml_path:
    return yml_path
  return module_path.replace('.py', '.yml')


def get_yml_data(
  yml_path: str,
  key: str,
) -> dict | None:
  yml_data = {}

  # Handle YML file not existing
  if os.path.exists(yml_path) is False:
    return yml_data

  with open(
    file=yml_path,
    mode='r',
    encoding='utf-8',
  ) as file:
    content = file.read()
    data = yaml.safe_load(content)
    # Handle empty YML file
    if data is None:
      return yml_data
    # Handle YML file not having
    # specified environment key
    if key not in data.keys():
      return {}
    return data[key]


def convert_dict_to_dataclass(yml_data: dict) -> Env:
  fields = []
  for key, value in yml_data.items():
    field = (
      key,
      str,
      dc.field(default=value),
    )
    fields.append(field)
  return dc.make_dataclass('Env', fields)()


def get_variables_from_venv(yml_data: dict) -> dict:
  for key in yml_data:
    venv_value = os.getenv(key)
    if venv_value is None:
      continue
    yml_data[key] = venv_value
  return yml_data


def process_config(
  data: Data | dict | str | None = None,
  config: Dict | str | None = None,
) -> Data | dict | str:
  if data is not None:
    return data
  return config['environment']


# ruff: noqa: ARG001
def main(
  module_path: str | None = None,
  config: dict | None = None,
  yml_path: str | None = None,
  environment_key: str = 'environment',
) -> Env:
  data = format_arguments(_locals=locals())
  data.body.yml_path = get_yml_path(
    module_path=data.body.module_path,
    yml_path=data.body.yml_path,
  )
  data.body.yml_data = get_yml_data(
    yml_path=data.body.yml_path,
    key=data.body.environment_key,
  )
  data.body.yml_data = get_variables_from_venv(yml_data=data.body.yml_data)
  data.response = convert_dict_to_dataclass(yml_data=data.body.yml_data)
  return data.response


def example() -> None:
  yml_path = '${WORKDIR}/utils/get_environment/test_resources/app.yml'
  result = main(yml_path=yml_path)
  print(result)


if __name__ == '__main__':
  example()
