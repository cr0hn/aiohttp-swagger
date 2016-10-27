import json

from aiohttp import web
from aiohttp_swagger import *

from os.path import join, dirname, abspath

async def ping(request):
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


async def test_ping(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', "/ping", ping)

    client = await test_client(app)
    resp = await client.get('/ping')
    assert resp.status == 200
    text = await resp.text()
    assert 'pong' in text

async def test_swagger_file_url(test_client, loop):
    TESTS_PATH = abspath(join(dirname(__file__)))

    app = web.Application(loop=loop)
    setup_swagger(app,
                  swagger_from_file=TESTS_PATH + "/data/example_swagger.yaml")

    client = await test_client(app)
    resp1 = await client.get('/api/doc/swagger.json')
    assert resp1.status == 200
    text = await resp1.text()
    result = json.loads(text)
    assert '/example1' in result['paths']
    assert '/example2' in result['paths']
    assert 'API Title' in result['info']['title']

async def test_custom_swagger(test_client, loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', "/ping", ping)
    description = "Test Custom Swagger"
    setup_swagger(app,
                  swagger_url="/api/v1/doc",
                  description=description,
                  title="Test Custom Title",
                  api_version="1.0.0",
                  contact="my.custom.contact@example.com")

    client = await test_client(app)
    resp1 = await client.get('/api/v1/doc/swagger.json')
    assert resp1.status == 200
    text = await resp1.text()
    result = json.loads(text)
    assert '/ping' in result['paths']
    assert 'Test Custom Title' in result['info']['title']
