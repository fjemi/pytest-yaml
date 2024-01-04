<!-- markdownlint-disable MD024 -->
<h1>YAML Testing Framework</h1>

A pytest plugin that provides a simple, low code framework for unit testing in Python.

Features:
- Tests defined in YAML for flexibility and accessibility
- Supports functional programming to help build scalable and responsive applications
- Allows modules, functions, and other objects to be easily patched
- Casting function arguments and output
- Allows user to define custom methods for verifying the output of functions
- Runs to tests in multiple threads to prevent conflicts between tests
- Collates multiple, individual tests using minimal configurations or data


<details>
<summary><h2>Setup</h2></summary><br>

<h3>Install</h3>

<h4>From GitHub using</h4>

<h5>pipenv</h5>

```console
pipenv install git+https://github.com/fjemi/pytest-yaml#egg=pytest-yaml
```
<h5>pip</h5>

```console
pip install git+https://github.com/fjemi/pytest-yaml
```

<!-- #### From PyPi
```bash
pip install pytest-yaml
``` -->

<h3>Add Entrypoint for Tests</h3>

Create the file `/examples/test_entrypoint.py`, which is used to:
- invoke pytest
- allow the plugin to collect and execute tests defined in YAML files
- pass collected tests as arguments to a parameterized test function within test_entrypoint.py.


```python
# /examples/test_entrypoint.py


import dataclasses as dc

import pytest
import yaml


MODULE = __file__

LOCALS = locals()
UNNAMED_TEST_COUNT = 0


@dc.dataclass
class Data_Class:
  pass


def get_ids(test: Data_Class) -> str:
  id_ = getattr(test, 'id_short', None)
  if not id_:
    global UNNAMED_TEST_COUNT
    UNNAMED_TEST_COUNT += 1
    id_ = f'test_{UNNAMED_TEST_COUNT}'
  return id_


def verify_assertions(assertions: list | None = None) -> int | None:
  assertions = assertions or []

  for assertion in assertions:
    output = assertion.output
    expected = assertion.expected

    try:
      output = yaml.dump(output)
      expected = yaml.dump(expected)
    finally:
      assert expected == output

  return 1


@pytest.mark.parametrize(
  argnames='test',
  ids=lambda test: get_ids(test=test),
  argvalues=pytest.yaml_tests, )
def test_(test: Data_Class) -> None:
  assertions = getattr(test, 'assertions', [])
  verify_assertions(assertions=assertions)
```

<h3>Configure Plugin</h3>

The plugin can be configured within the pytest settings of a configuration file, such as a `pytest.ini`, or in the console when invoking pytest. The configurations are

- `project-directory` - Location of the a module, YAML file, or directory of modules. Absolute path of a module or directory containing modules to tests. Use `.` to reference the root directory or `.location` to reference a `location` in relation to the root directory.
- `exclude-files` - A list of patterns. Modules that have loations that match one of the patterns are excluded from testsing.
- `resources` - A list containing the locations of globals resource modules to use during tests.
- `resources_folder_name` - Name of folders in the same directory as the module to test.
  - These folders contain modules and other files to use during the tests.
  - Modules in folders are automatically picked up by the app and functions and variables defined in the modules are accessible in the YAML files using the dot-delimited route to the function/variable.
- `yaml_suffix` - Suffix of YAML files containing tests. For example, the test file for the module `app.py` would be `app_test.yml` or `app_test.yaml` when the `yaml_suffix` is set to `_test`

<h4>Configure in pytest.ini</h4>

```ini
; pytest.ini

[pytest]
project-directory = .  #  `.` is default
exclude_files =  # empty list is default
  matching
  patterns
  to
  exclude
resources =  # empty list is default
  resource_location_a
  resource_location_b
resources_folder_name = test_resources  # `test_resources` is default
yaml_suffix = _test  # `_test` is default
```

<h4>Configure console command</h4>

```console
pytest \
--project-directory=.app.py \
--exclude_files matching patterns to exclude \
--resources resource_location_a resource_location_b \
--resource-folder-name test_resources \
--yaml-suffix _test
```
</details>


<details>
<summary><h2>YAML Test Files</h2></summary><br>

Tests are defined in YAML files with the top level keys picked up by the plugin being:
- `globals` - Configurations to be used locally for each test in the YAML files
- `tests` - Configurations used for multiple of individual tests.

```yaml
globals: {}  # Default is null or empty dict


tests: []  # Default is null or empty list
```

<h3>Expanding and Collating Tests</h3>

Using the plugin we can define configurations for tests at various levels (globals, tests, nested tests), expand those configurations to lower configurations, and collate individual tests. This allows us to resuse configurations and reduce the duplication of content across a YAML file. This is similar to [anchors](https://yaml.org/spec/1.2.2/#anchors-and-aliases) in YAML, which we can take advantage, along with the other features availabe in YAML.

<h4>Example</h4>

This is an abstract example of the expanding/collating configurations done by the plugin, where the configurations for tests are comprised of:
- `config_a` - a list
- `config_b` - an object
- `config_c` - a string
- `config_d` - null

In this example, we set these configurations at various levels, globally, tests, and nested tests; and the expanded/collated results are three individual tests containing various values for each configuration.

```yaml
# Defined/Condensed

globals:
  # Append items to list
  config_a:
  - A
  # Update or add dictionary key/value pairs
  config_b:
    b: B
  # Replace string
  config_c: C


tests:
- config_a:
  - B
- config_b:
    c: C
  tests:
  - config_a:
    - C
    config_c: C0
  - config_d: D
    tests:
    - config_a:
      - B
      config_b:
        b: B0
```

```yaml
# Expanded/Collated

tests:
# Test 1
- config_a:
  - A
  - B  # Appended item
  config_b:
    b: B
  config_c: C
  config_d: null  # Standard test config not defined
# Test 2
- config_a:
  - A
  - C  # Appended item
  config_b:
    b: B
    c: C  # Added key/value
  config_c: C0  # Replace string
  config_d: null
# Test 3
- config_a:
  - A
  config_b:
    b: B0  # Updated key/value pair
    c: C
  config_c: C
  config_d: D  # Standard test config defined
```


<h3>Schema</h3>

Details for configurations or fields of an actual test are defined below. These fields can be defined globally or at different test levels.

```yaml
# Test configurations

fields:
- function:
    description: The name of the function test
    type: string
    action: replace
- environment:
    description: Environment variables used by functions in a module
    type: object
    action: Update key/value pairs
- description:
    description: Describes the module, function, tests, etc ...
    type: string | array[string]
    action: Append items to list
- resources:
    description: Other modules to use during tests
    type: string | array[string]
    action: Append items to list
- patches:
    description: Objects in a module to patch for tests
    type: object | array[object]
    action: Append items to list
- cast_arguments:
    description: Convert function arguments to other data types
    type: object | array[object]
    action: Append items to list
- cast_output:
    description: Converts the output of functions to other data types
    type: object | array[object]
    action: Append items to list
- assertions:
    description: Verifies the output of functions
    type: object | array[object]
    action: Append items to list
- tests:
    description: Nested configurations that get collated into individual tests
    types: object | array[object]
    action: Append items to list
```

</details>


<details>
<summary><h2>Quick Example</h2></summary><br>

In this example we create the following files:
- `/examples/quick_example/add.py` - Contains the function `add`, wich returns the result from adding two numbers `a` and `b`. This is the function we will test.
- `/examples/quick_example/add_test.yml` - YAML file where two test, **Add two integers** and **Add two floats**, are defined.
- `/examples/quick_example/test_resources/assertions.py` - Contains the method `equals` that will be used to verify the output of the `add` function.
- `/examples/test_entrypoint.py` - The file that acts as an entrypoint for discovering and running tests

```python
# /examples/quick_example/add.py

def add(
  a: int | float,
  b: int | float,
) -> int | float:
  return a + b

```

```python
# /examples/quick_example/test_resources/assertions.py

def equals(output, expected) -> dict:
  '''Use `test_resources.assertions.equals` in YAML file to access method'''
  passed = expected == output
  return {
    'passed': passed,
    'output': output,
    'expected': expected,
  }

```

```yaml
# /examples/quick_example/add_test.yml

tests:
- function: add
  description: Returns the result of adding two numbers
  tests:
  - description: Add two integers
    arguments:
      a: 1
      b: 2
    assertions:
    - method: test_resources.assertions.equals
      expected: 3
  - description: Add two floats
    arguments:
      a: 1.5
      b: 2.5
    assertions:
    # This test will fail as the result is 4, not 5.
    - method: test_resources.assertions.equals
      expected: 5
```

Execute the command below to call the plugin.

```console
pytest --project-directory=/examples/quick_example --resources-folder-name=test_resources  -s -vvv
```

Here we see the results from calling the plugin. Two tests were collected with one passing and the other failing.

![Alt text](./examples/quick_example/static/quick_example_results.png?raw=true "Quick Example Results")

</details>


<details>
<summary><h2>Resources</h2></summary><br>

Resources are modules and other files that are used during tests. Resources can be defined when configuring the plugin (see above) or globally within in a YAML test file (global but local to the YAML file) as such:

```yaml
globals:
  resources:
  - /resource_location/module_a.py
  - /resource_location/module_b.py
```

<h4>Configuration Fields</h4>

- `resources_folder_name` - The name of folders containing resources to use during tests. Folders placed in the same directory as the module being tested are picked up automatically by the plugin. The modules in theses folders are imported into the module to test, and the objects with resource modules can be accessed in the YAML test file through the dot delimited  route to the object: `[resources_folder_name].[module_name].[object_name]`.
- `resources` - The location of a module or a list of module locations to use as resources. These resources are defined globally and can be used within any YAML test file.

**Note**: Since resource modules are imported into the module to test, there is a risk that attributes of the modules to test can be overwritten. To avoid this it is important to pick unique names for resource folders or structure your project in a way to avoid naming conflicts.

<h3>Example</h3>

For this example we create the following files:
- `/examples/resources_example/app.py` - The module to test
- `/examples/resources_example/test_resources/app.py` - A source module in the resource folder associated with the module to test
- `/examples/resources_example/app_test.yml` - The YAML test file associated with the module to test
- `/examples/test_entrypoint.py`


```python
# /examples/resources_example/test_resources/app.py

import dataclasses as dc
from typing import Any


@dc.dataclass
class Data:
  a: int | float
  b: int | float
  result: int | float | None = None


def assert_type(
  output: Any | None = None,
  expected: Any | None = None,
) -> dict:
  output = type(output).__name__
  passed = output == expected
  return {
    'output': output,
    'expected': expected,
    'passed': passed, }
```

```python
# /examples/resources_example/app.py

import dataclasses as dc


@dc.dataclass
class Data_Class:
  pass


def add(data: Data_Class) -> Data_Class:
  data.result = data.a + data.b
  return data

```

```python
# /examples/resources_example/resource.py

import dataclasses as dc
from typing import Any


@dc.dataclass
class Data:
  a: int | float
  b: int | float
  result: int | float | None = None


def assert_equals(
  output: Any | None = None,
  expected: Any | None = None,
) -> dict:
  passed = output == expected
  return {
    'output': output,
    'expected': expected,
    'passed': passed, }

```

```yaml
# /examples/resources_example/app_test.yml

globals:
  # Define global resources for use throughout
  # the YAML file
  resources:
  - /examples/resource_example/resource.py


tests:
- function: add
  description: Return the result of adding two numbers from a dataclass
  tests:
  - cast_arguments:
    # Dot-delimited route to object from the resource folder
    - caster: test_resources.app.Data
      field: data
    arguments:
      data:
        a: 0
        b: 0
    assertions:
    # Dot-delimited route to object from the resource folder
    - method: test_resources.app.assert_type
      expected: Data
    # Dot-delimited route to object in relation to the location of app to test
    # /examples/resource_example/resource.py
    # /examples/resource_example/app.py
    # We can access objects from this module by resource.[object_name]
    - method: resource.assert_equals
      field: result
      expected: 0
  - cast_arguments:
    - caster: resource.Data
      field: data
    arguments:
      data:
        a: 1
        b: 1
    assertions:
    # Dot-delimited route to object from the resource folder
    - method: test_resources.app.assert_type
      expected: Data
    # Dot-delimited route to object in relation to the location of app to test
    - method: resource.assert_equals
      field: result
      expected: 2

```

Execute the command below to call the plugin.

```console
pytest --project-directory=/examples/resource_example --resources-folder-name=test_resources -s -vvv
```

Here we see the results; two tests collected and both pass as expected.

![Alt text](./examples/resource_example/static/resource_example_results.png?raw=true "Resource Example Results")

</details>


<details>
<summary><h2>Assertions</h2></summary><br>

<h3>Methods</h3>

Assertions are defined by the user as functions or methods that can be reused between tests.

The parameters for the methods can be any combination of:
- `expected`: The expected output of a function
- `output`: The output of a function
- `exception`: Any exception that occurs when calling a function. The exception is formatted as a dictionary with `name` and `description` as keys. If an exception is raised the output is usually null.

The the method must return a dictionary containing any combination of:
- `passed`: A boolean indicating whether or not the test passed or failed
- `output`: The formatted or unformatted output from the tested function
- `expected`: The formatted or unformatted expected output from the tested function

The returned dictionary is processed within the entrypoint file when running tests. in the file we assert that the values of the `output` and `expected` are equal. If so, the test passes, otherwise it fails.

<h3>Schema</h3>

Asssertions are defined in YAML test files under the key `assertions`, and a single assertion has the following fields:

- `method` - Dot-delimited route to the function or method used to verify the output of a function. If the method cannot be found the assertion will fail. Default is `null`.
- `expected` - The expected output of the function. Default is `null`.
- `field` - Sets the output to a dot-delimited route to an atrribute or key within the output. Default is `null`.
- `cast_output` - Casts the output or field within the output. Default is an empty list.

And single test can have multiple assertions

```yaml
tests:
  ...
  assertions:
  - method: null
    expected: null
    field: null
    cast_output: []
```

<h3>Example</h3>

For this example we create the following files:
- `/examples/assertion_example/app.py` - The module containing the functions to test
- `/examples/assertion_example/assertions.py` - Contains assertion methods to use for tests
- `/examples/assertion_example/app_test.yml` - YAML file where tests are defined
- `/examples/test_entrypoint.py`

```python
# .examples/assertions_example/assertions.py

from typing import Any


def assert_equals(
  output: Any | None = None,
  expected: Any | None = None,
) -> dict:
  passed = output == expected
  return {
    'passed': passed,
    'output': output,
    'expected': expected, }


def assert_exception(
  exception: dict | None = None,
  expected: str | None = None,
  # output: Any | None = None,
) -> dict:
  output = exception
  passed = expected == output
  return {
    'passed': passed,
    'output': output,
    'expected': expected, }
```

```python
# .examples/assertions_example/app.py

def subtract(
  a: int | float,
  b: int | float,
) -> int | float:
  return a - b


def add(
  a: int | float,
  b: int | float,
) -> dict:
  result = a + b
  return {'result': result}
```

```yaml
# .examples/assertions_example/app_test.yml

globals:
  resources:
  # Use absolute path for resources
  - /examples/assertions_example/assertions.py


tests:
- function: subtract
  description: Returns the result from subtracting two numbers
  tests:
  - description: Subtract two numbers
    arguments:
      a: 0
      b: 0
    assertions:
    # Method accessible in relation to absolute
    # path of the module to test
    - method: assertions.assert_equals
      expected: 0
  - description: Substract a number and a string
    arguments:
      a: '0'
      b: 0
    assertions:
    - method: assertions.assert_exception
      expected: TypeError
    # Output is always null if an error occurs
    - method: assertions.assert_equals
      expected: null
  - description: Assertion method doesn't exist
    arguments:
      a: 1
      b: 1
    assertions:
    # Fails since method does not exist
    - method: assertions.method_does_no_exist
      expected: null
- function: add
  description: Returns a dictionary containing the result of adding two numbers
  tests:
  - arguments:
      a: 0
      b: 0
    assertions:
    - method: assertions.assert_equals
      expected:
        result: 0
    - method: assertions.assert_equals
      # Setting the `field` key allows us verify specific
      # attributes/keys of the output
      field: result
      # Casting the output to a string
      cast_output:
      - caster: __builtins__.str
      expected: '0'
```

Execute the command below to call the plugin.

```console
pytest --project-directory=/examples/assertion_example --resources-folder-name=test_resources -s -vvv
```

Here we see the results. Three tests were collected with two passing and one failing.

![Alt text](./examples/assertion_example/static/assertion_example_results.png?raw=true "Assertion Example Results")

</details>


<details>
<summary><h2>Cast Arguments and Output</h2></summary><br>

Arguments can be converted to other data type before passing the arguments to the function we wish to test. Similarly, the output from functions can be converted prior to processing assertions. Also, we can perform any number of conversions on the arguments or output.

<h3>Schema</h3>

Casts are defined in YAML files as a list of objects under the keys `cast_arguments` and `cast_output`, or at the assertion level under the `cast_output` key. The following fields make up a cast object:
- `caster`: A function or object to cast the value (arguments/output) to.
- `field`: Dot-delimited route to a field, attribute, or key of the value. When set the sepecified field of the object is cast.
- `unpack`: A boolean indicating whether to unpack a dictionary, list, or tuple into the `caster`.

At the test level we can perform multiple casts of arguments or output, and we can perform multiple casts of the output at the assertion level.

```yaml
tests:  # Test level
  cast_arguments:
  - caster: null
    field: null
    unpack: null
  cast_output:
  - caster: null
    field: null
    unpack: null
  ...
  assertions:  # Assertion level
  - cast_output:
    - caster: null
      field: null
      unpack: null
    ...
```

<h3>Example</h3>

For this example we create the following files:
- `/examples/casts_example/app.py` - The module containing the functions to test`
- `/examples/casts_example/test_resources/app.py` - The module containing resources to use during the test
- `/examples/casts_example/assertions.py` - Contains assertion methods to use for tests
- `/examples/casts_example/app_test.yml` - YAML file where tests are defined
- `/examples/test_entrypoint.py`

```python
# /examples/casts_example/app.py

import dataclasses as dc


@dc.dataclass
class Data:
  a: int | float
  b: int | float
  result: int | float | None = None


def add(data: Data) -> Data:
  print(data)
  data.result = data.a + data.b
  return data

```

```python
# /examples/casts_example/test_resources/app.py

import dataclasses as dc


@dc.dataclass
class Test_Data:
  a: int | float = 0
  b: int | float = 0
  result: int | float = 0
```

```python
# /examples/casts_example/assertions.py

from typing import Any


def assert_equals(
  output: Any | None = None,
  expected: Any | None = None,
) -> dict:
  passed = output == expected
  return {
    'passed': passed,
    'output': output,
    'expected': expected, }


def assert_type(
  output: Any | None = None,
  expected: str | None = None,
) -> dict:
  output = type(output).__name__
  passed = expected == output
  return {
    'passed': passed,
    'output': output,
    'expected': expected, }
```

```yaml
# /examples/casts_example/app_test.yml

globals:
  resources:
  - /examples/casts_example/assertions.py


tests:
- function: add
  description: Returns the result of adding two numbers
  tests:
  - description: Cast argument as a dataclass defined in module
    cast_arguments:
    - caster: Data
      field: data
    arguments:
      data:
        a: 1
        b: 1
    assertions:
    - method: assertions.assert_type
      expected: Data
    - method: assertions.assert_equals
      # Get the value of a field within the output
      field: result
      expected: 2
  - description: Cast argument as a dataclass defined in resource module
    cast_arguments:
    - caster: test_resources.app.Test_Data
      field: data
    arguments:
      data:
        a: 2
        b: 2
    assertions:
    - method: assertions.assert_type
      expected: Test_Data
    - method: assertions.assert_equals
      field: result
      expected: 4
    - method: assertions.assert_equals
      # Cast preformed at the assertion level
      cast_output:
      - caster: __builtins__.str
      expected: Test_Data(a=2, b=2, result=4)
  - description: Cast arguments as a dataclass and cast output to a dictionary
    cast_arguments:
    - caster: Data
      field: data
      unpack: true
    arguments:
      data:
        a: 3
        b: 3
    # Cast output at the test level
    cast_output:
    - caster: dc.asdict
    assertions:
    - method: assertions.assert_type
      expected: dict
    - method: assertions.assert_equals
      expected:
        a: 3
        b: 3
        result: 6
```

![Alt text](./examples/casts_example/static/casts_example_results.png?raw=true "Casts Example Results")

</details>


<details>
<summary><h2>Patches</h2></summary><br>

We can patch objects in the module to test before running tests, and since tests are run in individual threads we can different patches for the same object without interference between tests.

<h3>Methods</h3>

There are four patch methods:

- **value** - A value to return when the patched object is used.
- **return_value** - A value to return when the patched object is called as function.
- **side_effect_list** - A list of values to call based off of the number of times the object is called. Returns the item at index `n - 1` of the list for the `nth` call of the object. Reverts to index 0 when number of calls exceeds the length of the list.
- **side_effect_dict** - A dictionary of key, values for to patch an object with. When the patched object is called with a key, the key's associated value is returned

<h3>Schema</h3>

Patches are defined at a list of objects in YAML test files under the key `patches`, and a single patch object has the following fields:

- `method` - One of the four patch methods defined above.
- `value` - The value the patched object should return when called or used.
- `name` - The dot-delimited route to the object we wish to patch, in the module to test.


```yaml
tests:
  - patches: null  # null is default
    ...
  - patches:
    - method: null  # null is default
      value: null  # null is default
      name: null  # null is default
    ...
```

<h3>Example</h3>

For this example we create the following files:
- `/examples/patch_example/app.py` - The modules to test that contains objects we will patch.
- `/examples/patch_example/app_test.yml` - The YAML test file associated with the module to test.
- `/examples/patch_example/assertions.py` - Resource module containing assertions we will use to verify the results of the patches.


```python
# /examples/patch_example/app.py

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
```

```yaml
# /examples/patch_example/app_test.yml

globals:
  resources:
  - /examples/patch_example/assertions.py


tests:
- function: get_object
  description: Returns an object within the function's parent module
  tests:
  - description: Return original objects
    tests:
    - arguments:
        name: STRING
      assertions:
      - method: assertions.equals
        expected: string
    - arguments:
        name: NUMBER
      assertions:
      - method: assertions.equals
        expected: 1
    - arguments:
        name: DICTIONARY
      assertions:
      - method: assertions.equals
        expected:
          key: value
    - arguments:
        name: function_
      assertions:
      - method: assertions.equals
        field: __name__
        expected: function_
      - method: assertions.function_calls
        expected:
          n: 1
          results:
          - FUNCTION
  - description: Return patched objects
    tests:
    - description: Patch string with another string
      patches:
      - method: value
        value: patched_string
        name: STRING
      arguments:
        name: STRING
      assertions:
      - method: assertions.equals
        expected: patched_string
    - description: Patch number with another number
      patches:
      - method: value
        value: 2
        name: NUMBER
      arguments:
        name: NUMBER
      assertions:
      - method: assertions.equals
        expected: 2
    - description: Patch an existing dictionary key
      patches:
      - method: value
        value: patched_value
        name: DICTIONARY.key
      arguments:
        name: DICTIONARY
      assertions:
      - method: assertions.equals
        expected:
          key: patched_value
    - description: Patch a non-existing dictionary key
      patches:
      - method: value
        value: patched_value
        name: DICTIONARY.patched_key
      arguments:
        name: DICTIONARY
      assertions:
      - method: assertions.equals
        expected:
          key: value
          patched_key: patched_value
    - description: Patch a field in a dataclass as a callable
      patches:
      - method: callable
        value: patched_value
        name: DATA.field
      arguments:
        name: DATA
      assertions:
      - method: assertions.equals
        field: field.__name__
        expected: callable_patch
      - method: assertions.equals
        field: field.__class__.__name__
        expected: function
    - description: Patch a function as a side effect list
      patches:
      - method: side_effect_list
        value:
        - uno
        - dos
        - tres
        name: function_
      arguments:
        name: function_
      assertions:
      - method: assertions.function_calls
        expected:
          n: 4
          results:
          - uno
          - dos
          - tres
          - uno
    - description: Patch a function as a side effect dict
      patches:
      - value:
          a: A
          b: B
        method: side_effect_dict
        # name: function_
        name: TEMP
      arguments:
        # name: function_
        name: TEMP
      assertions:
      - method: assertions.function_calls
        expected:
          keys:
          - a
          - b
          results:
          - A
          - B
```

```python
# /examples/patch_example/assertions.py

from typing import Any, Callable


def equals(
  output: Any | None = None,
  expected: Any | None = None,
) -> dict:
  passed = output == expected
  return {
    'output': output,
    'expected': expected,
    'passed': passed, }


def function_calls(
  output: Callable | None = None,
  expected: Any | None = None,
) -> dict:
  store = []
  n = expected.get('n')
  keys = expected.get('keys')

  if n:
    n = range(n)
    for i in n:
      store.append(output())
  elif keys:
    for key in keys:
      store.append(output(key))

  output = store
  expected = expected.get('results', [])
  passed = output == expected

  return {
    'output': output,
    'expected': expected,
    'passed': passed, }
```

Execute the command below to call the plugin.

```console
pytest --project-directory=/examples/assertion_example -s -vvv
```

Here we see the results. The tests returning the original and patched objects all as expected.

![Alt text](./examples/patch_example/static/patch_example_results.png?raw=true "Patch Example Results")

</details>


<details>
<summary><h2>Environment</h2></summary><br>

</details>

<br>
<a
  href="https://www.buymeacoffee.com/olufemijemo"
  target="_blank"
>
  <img
    src="https://cdn.buymeacoffee.com/buttons/default-orange.png"
    alt="Buy Me A Coffee"
    height="41"
    width="174"
  >
</a>
