import asyncio
import json

import pytest
from aiohttp import web
from aiohttp_swagger import *


@asyncio.coroutine
@swagger_validation
def post1(request, *args, **kwargs):
    """
    ---
    description: Post resources
    tags:
    - Function View
    produces:
    - application/json
    consumes:
    - application/json
    parameters:
    - in: body
      name: body
      required: true
      schema:
        type: object
        properties:
          test:
            type: string
            default: default
            minLength: 2
          test1:
            type: string
            default: default1
            minLength: 2
    responses:
        "200":
            description: successful operation.
        "405":
            description: invalid HTTP Method
    """
    return web.json_response(data=request.validation['body'])


@asyncio.coroutine
@swagger_validation
def post2(request, *args, **kwargs):
    """
    ---
    description: Post resources
    tags:
    - Function View
    produces:
    - text/plain
    consumes:
    - text/plain
    parameters:
    - in: body
      name: body
      required: true
      schema:
        type: string
        default: default
        minLength: 2
    responses:
        "200":
            description: successful operation.
        "405":
            description: invalid HTTP Method
    """
    return web.Response(text=request.validation['body'])


POST1_METHOD_PARAMETERS = [
    # success
    (
        'post',
        '/example12',
        {'test': 'default'},
        {'Content-Type': 'application/json'},
        200
    ),
    # success
    (
        'post',
        '/example12',
        {},
        {'Content-Type': 'application/json'},
        200
    ),
    # error
    (
        'post',
        '/example12',
        None,
        {'Content-Type': 'application/json'},
        400
    ),
]

POST2_METHOD_PARAMETERS = [
    # success
    (
        'post',
        '/example12',
        '1234',
        {'Content-Type': 'text/plain'},
        200
    ),
    (
        'post',
        '/example12',
        None,
        {'Content-Type': 'text/plain'},
        400
    ),
]


@pytest.mark.parametrize("method,url,body,headers,response",
                         POST1_METHOD_PARAMETERS)
@asyncio.coroutine
def test_function_post1_method_body_validation(
        test_client, loop, swagger_file, method, url, body, headers, response):
    app = web.Application(loop=loop)
    app.router.add_post("/example12", post1)
    setup_swagger(
        app,
        swagger_merge_with_file=True,
        swagger_validate_schema=True,
        swagger_from_file=swagger_file,
    )
    client = yield from test_client(app)
    data = json.dumps(body) \
        if headers['Content-Type'] == 'application/json' else body
    resp = yield from getattr(client, method)(url, data=data, headers=headers)
    text = yield from resp.json()
    assert resp.status == response, text
    if response != 200:
        assert 'error' in text
    else:
        assert 'error' not in text
        assert 'test' in text
        assert text['test'] == 'default'
        assert text['test1'] == 'default1'


@pytest.mark.parametrize("method,url,body,headers,response",
                         POST2_METHOD_PARAMETERS)
@asyncio.coroutine
def test_function_post2_method_body_validation(
        test_client, loop, swagger_file, method, url, body, headers, response):
    app = web.Application(loop=loop)
    app.router.add_post("/example12", post2)
    setup_swagger(
        app,
        swagger_merge_with_file=True,
        swagger_validate_schema=True,
        swagger_from_file=swagger_file,
    )
    client = yield from test_client(app)
    data = json.dumps(body) \
        if headers['Content-Type'] == 'application/json' else body
    resp = yield from getattr(client, method)(url, data=data, headers=headers)
    text = yield from resp.text()
    assert resp.status == response, text
    if response != 200:
        assert 'error' in text
    else:
        assert isinstance(text, str)
