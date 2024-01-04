#!.venv/bin/python3
# -*- coding: utf-8 -*-


from typing import List

import pytest
import yaml
from error_handler.app import main as error_handler
from get_config.app import main as get_config
from logger.app import main as logger

from main.app import main as plugin


MODULE = __file__
CONFIG = get_config(module=MODULE)

LOCALS = locals()


@error_handler()
async def run_plugin(
  project_directory: str | None = None,
  exclude_files: str | List[str] | None = None,
  resources_folder_name: str | None = None,
  yaml_suffix: str | None = None,
) -> int:
  data = plugin(
    exclude_files=exclude_files,
    project_directory=project_directory,
    yaml_suffix=yaml_suffix,
    resources_folder_name=resources_folder_name, )
  await logger(
    data=data,
    standard_output=True, )
  return 1


@error_handler()
async def run_pytest(
  project_directory: str | None = None,
  exclude_files: str | None = None,
  resources_folder_name: str | None = None,
  yaml_suffix: str | None = None,
) -> int:
  args = f'''
    - -s
    - -vvv
    - -ra
    - --tb=short
    - --resources-folder-name={resources_folder_name}
    - --exclude-files={exclude_files}
    - --project-directory={project_directory}
    - --yaml_suffix={yaml_suffix}
  '''
  args = yaml.safe_load(args)
  pytest.main(args)
  return 1


@error_handler()
async def main(
  invoke: str | None = None,
  # plugin arguments
  project_directory: str | None = None,
  exclude_files: str | None = None,
  resources_folder_name: str | None = None,
  yaml_suffix: str | None = None,
) -> int:
  project_directory = project_directory or '.'
  yaml_suffix = yaml_suffix or '_test'
  exclude_files = exclude_files or 'ignore'
  resources_folder_name = resources_folder_name or 'test_resources'
  invoke = invoke or 'plugin'

  handler = f'run_{invoke}'
  handler = LOCALS[handler]
  return handler(
    exclude_files=exclude_files,
    project_directory=project_directory,
    yaml_suffix=yaml_suffix,
    resources_folder_name=resources_folder_name, )


if __name__ == '__main__':
  main(
    invoke='pytest',
    project_directory='.', )
