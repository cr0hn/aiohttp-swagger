import asyncio
import json
import pytest
import yaml
from os.path import join, dirname, abspath

from aiohttp import web
from aiohttp_swagger import *


@asyncio.coroutine
def ping(request):
    """
    ---
    description: This end-point allow to test that service is up.
    tags:
    - Health check
    produces:
    - text/plain
    responses:
        "200":
            description: successful operation. Return "pong" text
        "405":
            description: invalid HTTP Method
    """
    return web.Response(text="pong")


@asyncio.coroutine
def undoc_ping(request):
    return web.Response(text="pong")


class ClassView(web.View):
    def _irrelevant_method(self):
        pass

    @asyncio.coroutine
    def get(self):
        """
        ---
        description: Get resources
        tags:
        - Class View
        produces:
        - text/plain
        responses:
            "200":
                description: successful operation.
            "405":
                description: invalid HTTP Method
        """
        return web.Response(text="OK")

    @asyncio.coroutine
    def post(self):
        """
        ---
        description: Post resources
        tags:
        - Class View
        produces:
        - text/plain
        responses:
            "200":
                description: successful operation.
            "405":
                description: invalid HTTP Method
        """
        return web.Response(text="OK")

    @asyncio.coroutine
    def patch(self):
        """
        This method is undocumented in the swagger sense.
        """
        return web.Response(text="OK")


@swagger_path(abspath(join(dirname(__file__))) + '/data/partial_swagger.yaml')
@asyncio.coroutine
def ping_partial(request):
    return web.Response(text="pong")


@asyncio.coroutine
def test_ping(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', "/ping", ping)

    client = yield from test_client(app)
    resp = yield from client.get('/ping')
    assert resp.status == 200
    text = yield from resp.text()
    assert 'pong' in text


@asyncio.coroutine
def test_swagger_file_url(test_client, loop):
    TESTS_PATH = abspath(join(dirname(__file__)))

    app = web.Application(loop=loop)
    setup_swagger(app,
                  swagger_from_file=TESTS_PATH + "/data/example_swagger.yaml")

    client = yield from test_client(app)
    resp1 = yield from client.get('/api/doc/swagger.json')
    assert resp1.status == 200
    text = yield from resp1.text()
    result = json.loads(text)
    assert '/example1' in result['paths']
    assert '/example2' in result['paths']
    assert 'API Title' in result['info']['title']


@asyncio.coroutine
def test_partial_swagger_file(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', "/ping-partial", ping_partial)
    setup_swagger(app)

    client = yield from test_client(app)
    resp1 = yield from client.get('/api/doc/swagger.json')
    assert resp1.status == 200
    text = yield from resp1.text()
    result = json.loads(text)
    assert '/ping-partial' in result['paths']


@asyncio.coroutine
def test_custom_swagger(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', "/ping", ping)
    description = "Test Custom Swagger"
    setup_swagger(app,
                  swagger_url="/api/v1/doc",
                  description=description,
                  title="Test Custom Title",
                  api_version="1.0.0",
                  contact="my.custom.contact@example.com")

    client = yield from test_client(app)
    resp1 = yield from client.get('/api/v1/doc/swagger.json')
    assert resp1.status == 200
    text = yield from resp1.text()
    result = json.loads(text)
    assert '/ping' in result['paths']
    assert 'Test Custom Title' in result['info']['title']


@asyncio.coroutine
def test_swagger_home_decorator(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', "/ping", ping)
    description = "Test Custom Swagger"
    setup_swagger(app,
                  swagger_url="/api/v1/doc",
                  description=description,
                  title="Test Custom Title",
                  api_version="1.0.0",
                  contact="my.custom.contact@example.com",
                  swagger_home_decor=lambda x: x)

    client = yield from test_client(app)
    resp1 = yield from client.get('/api/v1/doc/swagger.json')
    assert resp1.status == 200
    text = yield from resp1.text()
    result = json.loads(text)
    assert '/ping' in result['paths']
    assert 'Test Custom Title' in result['info']['title']


@asyncio.coroutine
def test_swagger_def_decorator(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', "/ping", ping)
    description = "Test Custom Swagger"
    setup_swagger(app,
                  swagger_url="/api/v1/doc",
                  description=description,
                  title="Test Custom Title",
                  api_version="1.0.0",
                  contact="my.custom.contact@example.com",
                  swagger_def_decor=lambda x: x)

    client = yield from test_client(app)
    resp1 = yield from client.get('/api/v1/doc/swagger.json')
    assert resp1.status == 200
    text = yield from resp1.text()
    result = json.loads(text)
    assert '/ping' in result['paths']
    assert 'Test Custom Title' in result['info']['title']


@pytest.fixture
def swagger_info():
    filename = abspath(join(dirname(__file__))) + "/data/example_swagger.yaml"
    return yaml.load(open(filename).read())


@asyncio.coroutine
def test_swagger_info(test_client, loop, swagger_info):
    app = web.Application(loop=loop)
    app.router.add_route('GET', "/ping", ping)
    description = "Test Custom Swagger"
    setup_swagger(app,
                  swagger_url="/api/v1/doc",
                  swagger_info=swagger_info)

    client = yield from test_client(app)
    resp1 = yield from client.get('/api/v1/doc/swagger.json')
    assert resp1.status == 200
    text = yield from resp1.text()
    result = json.loads(text)
    assert '/example1' in result['paths']
    assert '/example2' in result['paths']
    assert 'API Title' in result['info']['title']


@asyncio.coroutine
def test_undocumented_fn(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', "/undoc_ping", undoc_ping)
    setup_swagger(app)
    client = yield from test_client(app)
    resp = yield from client.get('/undoc_ping')
    assert resp.status == 200
    swagger_resp1 = yield from client.get('/api/doc/swagger.json')
    assert swagger_resp1.status == 200
    text = yield from swagger_resp1.text()
    result = json.loads(text)
    assert not result['paths']

@asyncio.coroutine
def test_class_view(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_route('*', "/class_view", ClassView)
    setup_swagger(app)

    client = yield from test_client(app)
    # GET
    resp = yield from client.get('/class_view')
    assert resp.status == 200
    text = yield from resp.text()
    assert 'OK' in text
    swagger_resp1 = yield from client.get('/api/doc/swagger.json')
    assert swagger_resp1.status == 200
    text = yield from swagger_resp1.text()
    result = json.loads(text)
    assert "/class_view" in result['paths']
    assert "get" in result['paths']["/class_view"]
    assert "post" in result['paths']["/class_view"]

    # POST
    resp = yield from client.post('/class_view')
    assert resp.status == 200
    text = yield from resp.text()
    assert 'OK' in text
    text = yield from swagger_resp1.text()
    result = json.loads(text)
    assert "/class_view" in result['paths']
    assert "get" in result['paths']["/class_view"]
    assert "post" in result['paths']["/class_view"]

    # Undocumented PATCH
    resp = yield from client.patch('/class_view')
    assert resp.status == 200
    text = yield from resp.text()
    assert 'OK' in text
    text = yield from swagger_resp1.text()
    result = json.loads(text)
    assert "/class_view" in result['paths']
    assert "patch" not in result['paths']["/class_view"]


@asyncio.coroutine
def test_sub_app(test_client, loop):
    sub_app = web.Application(loop=loop)
    sub_app.router.add_route('*', "/class_view", ClassView)
    setup_swagger(sub_app, api_base_url='/sub_app')
    app = web.Application(loop=loop)
    app.add_subapp(prefix='/sub_app', subapp=sub_app)

    client = yield from test_client(app)
    # GET
    resp = yield from client.get('/sub_app/class_view')
    assert resp.status == 200
    text = yield from resp.text()
    assert 'OK' in text
    swagger_resp1 = yield from client.get('/sub_app/api/doc/swagger.json')
    assert swagger_resp1.status == 200
    text = yield from swagger_resp1.text()
    result = json.loads(text)
    assert "/class_view" in result['paths']
    assert "get" in result['paths']["/class_view"]
    assert "post" in result['paths']["/class_view"]
