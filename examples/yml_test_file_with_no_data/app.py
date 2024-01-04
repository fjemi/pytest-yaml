#!.venv/bin/python3
# -*- coding: utf-8 -*-


MODULE = __file__


def main(
  # trunk-ignore(ruff/ARG001)
  *args,
  # trunk-ignore(ruff/ARG001)
  **kwargs,
) -> str:
  return 'yaml test file with no data'


def example() -> None:
  from invoke_pytest.app import main as invoke_pytest

  invoke_pytest(
    invoke='pytest',
    project_directory=MODULE, )


if __name__ == '__main__':
  example()
