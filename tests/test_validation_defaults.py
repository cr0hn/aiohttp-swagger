import asyncio

import pytest
from aiohttp import web
from aiohttp_swagger import *


@swagger_validation
async def post(request, *args, **kwargs):
    """
    ---
    description: Post User data
    tags:
    - Function View
    produces:
    - application/json
    consumes:
    - application/json
    parameters:
    - in: query
      name: test
      type: string
      minLength: 3
      required: true
      default: test
    - in: query
      name: test1
      type: string
      minLength: 3
      required: true
      default: test1
    responses:
        "200":
            description: successful operation.
        "405":
            description: invalid HTTP Method
    """
    return web.json_response(data=request.validation)


METHOD_PARAMETERS = [
    # too short test
    (
        'post',
        '/example2?test=1',
        {'Content-Type': 'application/json'},
        400
    ),
    # without test
    (
        'post',
        '/example2',
        {'Content-Type': 'application/json'},
        200
    ),
]


@pytest.mark.parametrize("method,url,headers,response", METHOD_PARAMETERS)
async def test_function_post_with_defaults(
        test_client, loop, swagger_ref_file,
        method, url, headers, response):
    app = web.Application(loop=loop)
    app.router.add_post("/example2", post)
    setup_swagger(
        app,
        swagger_merge_with_file=True,
        swagger_validate_schema=True,
        swagger_from_file=swagger_ref_file,
    )
    client = await test_client(app)
    resp = await getattr(client, method)(url, headers=headers)
    data = await resp.json()
    assert resp.status == response, data
    if response != 200:
        assert 'error' in data
    else:
        assert 'error' not in data
        # both default parameters
        assert data['query']['test1'] == 'test1'
        assert data['query']['test'] == 'test'
