import asyncio
import json

import pytest
from aiohttp import web
from aiohttp_swagger import *


@swagger_validation
class ClassViewWithSwaggerDoc(web.View):

    def _irrelevant_method(self):
        pass

    async def get(self, *args, **kwargs):
        """
        ---
        description: Get resources
        tags:
        - Class View
        produces:
        - application/json
        consumes:
        - application/json
        parameters:
        - in: path
          name: user_id
          description: User ID
          required: true
          type: string
          minLength: 1
          pattern: '^\d+$'
        - in: query
          name: user_name
          description: User Name
          required: false
          type: string
          minLength: 1
          pattern: '^[a-d]+$'
        - in: query
          name: user_sex
          description: User Sex
          required: false
          type: string
          minLength: 1
          enum:
            - male
            - female
        - in: query
          name: user_login
          description: User Login
          required: false
          type: string
          minLength: 5
        - in: body
          name: body
          description: Created user object
          required: false
          schema:
            type: object
            properties:
              id:
                type: integer
                format: int64
              username:
                type: string
                allowEmptyValue: true
            required:
              - id
              - username
        responses:
            "200":
                description: successful operation.
            "405":
                description: invalid HTTP Method
        """
        return web.Response(text="OK")

    async def post(self, *args, **kwargs):
        """
        ---
        description: Post resources
        tags:
        - Class View
        produces:
        - application/json
        consumes:
        - application/x-www-form-urlencoded
        parameters:
        - in: header
          name: user_id
          description: User ID
          required: false
          type: string
          minLength: 1
          pattern: '^\d+$'
        - in: path
          name: user_id
          description: User ID
          required: true
          type: string
          minLength: 1
          pattern: '^\d+$'
        - in: query
          name: user_name
          description: User Name
          required: false
          type: string
          minLength: 1
          pattern: '^[a-d]+$'
        - in: query
          name: user_login
          description: User Login
          required: false
          type: string
          minLength: 5
        - in: formData
          name: id
          type: string
          pattern: '^\d+'
          minLength: 1
          require: true
        - in: formData
          name: username
          type: string
          minLength: 2
          require: false
        responses:
            "200":
                description: successful operation.
            "405":
                description: invalid HTTP Method
        """
        return web.Response(text="OK")


@swagger_validation
async def get(request, *args, **kwargs):
    """
    ---
    description: Get resources
    tags:
    - Function View
    produces:
    - application/json
    consumes:
    - application/json
    parameters:
    - in: path
      name: user_id
      description: User ID
      required: true
      type: string
      minLength: 1
      pattern: '^\d+$'
    - in: query
      name: user_name
      description: User Name
      required: false
      type: string
      minLength: 1
      pattern: '^[a-d]+$'
    - in: query
      name: user_login
      description: User Login
      required: false
      type: string
      minLength: 5
    - in: query
      name: user_sex
      description: User Sex
      required: false
      type: string
      minLength: 1
      enum:
        - male
        - female
    - in: body
      name: body
      description: Created user object
      required: false
      schema:
        type: object
        properties:
          id:
            type: integer
            format: int64
          username:
            type: string
        required:
          - id
          - username
    responses:
        "200":
            description: successful operation.
        "405":
            description: invalid HTTP Method
    """
    return web.Response(text="OK")


@swagger_validation
async def post(request, *args, **kwargs):
    """
    ---
    description: Post resources
    tags:
    - Function View
    produces:
    - application/json
    consumes:
    - application/x-www-form-urlencoded
    parameters:
    - in: header
      name: user_id
      description: User ID
      required: false
      type: string
      minLength: 1
      pattern: '^\d+$'
    - in: path
      name: user_id
      description: User ID
      required: true
      type: string
      minLength: 1
      pattern: '^\d+$'
    - in: query
      name: user_name
      description: User Name
      required: false
      type: string
      minLength: 1
      pattern: '^[a-d]+$'
    - in: query
      name: user_login
      description: User Login
      required: false
      type: string
      minLength: 5
    - in: formData
      name: id
      type: string
      pattern: '^\d+'
      minLength: 1
      require: true
    - in: formData
      name: username
      type: string
      minLength: 2
      require: false
    responses:
        "200":
            description: successful operation.
        "405":
            description: invalid HTTP Method
    """
    return web.Response(text="OK")


@swagger_validation(True)
async def get_turn_on_validation(request, *args, **kwargs):
    """
    ---
    description: Test validation
    tags:
    - Post
    produces:
    - application/json
    consumes:
    - application/json
    parameters:
    - in: path
      name: user_id
      description: User ID
      required: true
      type: string
      minLength: 1
      pattern: '^\d+$'
    responses:
        "200":
            description: successful operation.
        "405":
            description: invalid HTTP Method
    """
    return web.Response(text="OK")


@swagger_validation(False)
async def get_turn_off_validation(request, *args, **kwargs):
    """
    ---
    description: Test validation
    tags:
    - Post
    produces:
    - application/json
    consumes:
    - application/json
    parameters:
    - in: path
      name: user_id
      description: User ID
      required: true
      type: string
      minLength: 1
      pattern: '^\d+$'
    responses:
        "200":
            description: successful operation.
        "405":
            description: invalid HTTP Method
    """
    return web.Response(text="OK")


POST_METHOD_PARAMETERS = [
    # success
    (
        'post',
        '/example2/122212?user_login=12232323a',
        'id=2&username=12',
        {'Content-Type': 'application/x-www-form-urlencoded'},
        200
    ),
    # success
    (
        'post',
        '/example2/122212?user_login=12232323a',
        'id=2',
        {'Content-Type': 'application/x-www-form-urlencoded'},
        200
    ),
    # wrong. username too short
    (
        'post',
        '/example2/122212?user_login=12232323a',
        'id=2&username=1',
        {'Content-Type': 'application/x-www-form-urlencoded'},
        400
    ),
    # success
    (
        'post',
        '/example2/122212?user_login=12232323a',
        'id=2&username=12',
        {'Content-Type': 'application/x-www-form-urlencoded'},
        200
    ),
    # wrong user_id header
    (
        'post',
        '/example2/122212?user_login=12232323a',
        'id=2&username=12',
        {
            'Content-Type': 'application/x-www-form-urlencoded',
            'user_id': 'aaa'
        },
        400
    ),
    # correct user_id header
    (
        'post',
        '/example2/122212?user_login=12232323a',
        'id=2&username=12',
        {
            'Content-Type': 'application/x-www-form-urlencoded',
            'user_id': '123'
        },
        200
    ),
    # unsupported content-type
    (
        'post',
        '/example2/122212?user_login=12232323a',
        'id=2&username=12',
        {
            'Content-Type': 'application11',
            'user_id': '123'
        },
        400
    ),
]

GET_METHOD_PARAMETERS = [
    # wrong user_id test12
    (
        'get',
        '/example2/test12',
        {'id': 1, 'username': 'test'},
        {'Content-Type': 'application/json'},
        400
    ),
    # wrong user_id test12 and body
    (
        'get',
        '/example2/test12',
        {'id': 1},
        {'Content-Type': 'application/json'},
        400
    ),
    # wrong user_name
    (
        'get',
        '/example2/122212?user_name=123',
        {'id': 1, 'username': 'test'},
        {'Content-Type': 'application/json'},
        400
    ),
    # wrong blank body
    (
        'get',
        '/example2/122212',
        {},
        {'Content-Type': 'application/json'},
        400
    ),
    # wrong body. required username
    (
        'get',
        '/example2/122212',
        {'id': 2},
        {'Content-Type': 'application/json'},
        400
    ),
    # success. Not mandatory body
    (
        'get',
        '/example2/122212',
        None,
        {'Content-Type': 'application/json'},
        200
    ),
    # success
    (
        'get',
        '/example2/122212',
        {'id': 1, 'username': 'test'},
        {'Content-Type': 'application/json'},
        200
    ),
    # too short user_login
    (
        'get',
        '/example2/122212?user_login=1',
        {'id': 1, 'username': 'test'},
        {'Content-Type': 'application/json'},
        400
    ),
    # success
    (
        'get',
        '/example2/122212?user_login=12232323a',
        {'id': 1, 'username': 'test'},
        {'Content-Type': 'application/json'},
        200
    ),
    # wrong user sex
    (
        'get',
        '/example2/122212?user_sex=aaa',
        {'id': 1, 'username': 'test'},
        {'Content-Type': 'application/json'},
        400
    ),
    # success user sex
    (
        'get',
        '/example2/122212?user_sex=male',
        {'id': 1, 'username': 'test'},
        {'Content-Type': 'application/json'},
        200
    ),
]

ALL_METHODS_PARAMETERS = GET_METHOD_PARAMETERS + POST_METHOD_PARAMETERS


@pytest.mark.parametrize("method,url,body,headers,response",
                         ALL_METHODS_PARAMETERS)
async def test_class_swagger_view_validation(test_client, loop, swagger_file,
                                       method, url, body, headers, response):
    app = web.Application(loop=loop)
    app.router.add_route('*', "/example2/{user_id}", ClassViewWithSwaggerDoc)
    setup_swagger(
        app,
        swagger_merge_with_file=True,
        swagger_validate_schema=True,
        swagger_from_file=swagger_file,
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


@pytest.mark.parametrize("method,url,body,headers,response",
                         GET_METHOD_PARAMETERS)
async def test_function_get_method_swagger_view_validation(
        test_client, loop, swagger_file, method, url, body, headers, response):
    app = web.Application(loop=loop)
    app.router.add_get("/example2/{user_id}", get)
    setup_swagger(
        app,
        swagger_merge_with_file=True,
        swagger_validate_schema=True,
        swagger_from_file=swagger_file,
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


@pytest.mark.parametrize("method,url,body,headers,response",
                         POST_METHOD_PARAMETERS)
async def test_function_post_method_swagger_view_validation(
        test_client, loop, swagger_file, method, url, body, headers, response):
    app = web.Application(loop=loop)
    app.router.add_post("/example2/{user_id}", post)
    setup_swagger(
        app,
        swagger_merge_with_file=True,
        swagger_validate_schema=True,
        swagger_from_file=swagger_file,
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


@pytest.mark.parametrize("method,url,headers,response", [
    # wrong user_id test12
    (
        'get',
        '/example2/test12',
        {'Content-Type': 'application/json'},
        400
    ),
    (
        'get',
        '/example2/123123',
        {'Content-Type': 'application/json'},
        200
    ),
    # wrong header
    (
            'get',
            '/example2/123123',
            {'Content-Type': 'application/oops'},
            400
    ),
])
async def test_function_get_turn_on_validation(
        test_client, loop, swagger_file, method, url, headers, response):
    app = web.Application(loop=loop)
    app.router.add_get("/example2/{user_id}", get_turn_on_validation)
    setup_swagger(
        app,
        swagger_merge_with_file=True,
        swagger_validate_schema=True,
        swagger_from_file=swagger_file,
    )
    client = await test_client(app)
    resp = await getattr(client, method)(url, headers=headers)
    text = await resp.text()
    assert resp.status == response, text
    if response != 200:
        assert 'error' in text
    else:
        assert 'error' not in text


@pytest.mark.parametrize("method,url,headers,response", [
    # wrong user_id test12
    (
            'get',
            '/example2/test12',
            {'Content-Type': 'application/json'},
            200
    ),
    (
            'get',
            '/example2/123123',
            {'Content-Type': 'application/json'},
            200
    ),
    # wrong header
    (
            'get',
            '/example2/123123',
            {'Content-Type': 'application/oops'},
            200
    ),
])
async def test_function_get_turn_off_validation(
        test_client, loop, swagger_file, method, url, headers, response):
    app = web.Application(loop=loop)
    app.router.add_get("/example2/{user_id}", get_turn_off_validation)
    setup_swagger(
        app,
        swagger_merge_with_file=True,
        swagger_validate_schema=True,
        swagger_from_file=swagger_file,
    )
    client = await test_client(app)
    resp = await getattr(client, method)(url, headers=headers)
    text = await resp.text()
    assert resp.status == response, text
    if response != 200:
        assert 'error' in text
    else:
        assert 'error' not in text


async def test_validate_swagger_ui(test_client, loop, swagger_file):
    app = web.Application(loop=loop)
    app.router.add_route('*', "/example2/{user_id}", ClassViewWithSwaggerDoc)
    setup_swagger(
        app,
        swagger_merge_with_file=True,
        swagger_validate_schema=True,
        swagger_from_file=swagger_file,
        swagger_validator_url='//online.swagger.io/validator',
    )
    client = await test_client(app)
    swagger_resp = await client.get('/api/doc')
    assert swagger_resp.status == 200
    text = await swagger_resp.text()
    assert 'online.swagger.io/validator' in text
