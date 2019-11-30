from os.path import (
    abspath,
    dirname,
    join,
)

import yaml
import pytest


@pytest.fixture
def swagger_file():
    tests_path = abspath(join(dirname(__file__)))
    return join(tests_path, "data", "example_swagger.yaml")


@pytest.fixture
def swagger_ref_file():
    tests_path = abspath(join(dirname(__file__)))
    return join(tests_path, "data", "example_swagger_with_ref.yaml")


@pytest.fixture
def swagger_info():
    filename = abspath(join(dirname(__file__))) + "/data/example_swagger.yaml"
    return yaml.load(open(filename).read())


