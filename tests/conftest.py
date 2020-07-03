import pytest

# TODO This fixture is depricated and should be removed. It is used to support tests for aiohttp 2.3.x
@pytest.fixture
def aiohttp_client(test_client):
    return test_client