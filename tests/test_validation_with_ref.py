import asyncio
import json

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
    - in: body
      name: body
      description: Created user object
      required: false
      schema:
        $ref: '#/definitions/UserData'
    responses:
        "200":
            description: successful operation.
        "405":
            description: invalid HTTP Method
    """
    return web.Response(text="OK")


METHOD_PARAMETERS = [
    # wrong gender
    (
        'post',
        '/example2',
        {'user_id': '123', 'gender': 'aaa'},
        {'Content-Type': 'application/json'},
        400
    ),
    # success
    (
        'post',
        '/example2',
        {'user_id': '123', 'gender': 'male'},
        {'Content-Type': 'application/json'},
        200
    ),
]


@pytest.mark.parametrize("method,url,body,headers,response", METHOD_PARAMETERS)
async def test_function_post_with_swagger_ref(
        test_client, loop, swagger_ref_file,
        method, url, body, headers, response):
    app = web.Application(loop=loop)
    app.router.add_post("/example2", post)
    setup_swagger(
        app,
        swagger_merge_with_file=True,
        swagger_validate_schema=True,
        swagger_from_file=swagger_ref_file,
    )
    client = await test_client(app)
    data = json.dumps(body) \
        if headers['Content-Type'] == 'application/json' else body
    resp = await getattr(client, method)(url, data=data, headers=headers)
    text = await resp.text()
    assert resp.status == response, text
    if response != 200:
        assert 'error' in text
    else:
        assert 'error' not in text
