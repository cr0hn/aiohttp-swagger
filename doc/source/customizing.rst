Customizing Doc description and more
====================================

You can change this valued for Swagger doc:

1. API **Base URL**: Modify global prefix of your API.
2. **Description**: Long description of your API
3. API **Version**: Version of your API
4. **Title**: Title for your API
5. **Contact**: Contact info.

.. code-block:: python

    from aiohttp import web
    from aiohttp_swagger import *

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

    app = web.Application()

    app.router.add_route('GET', "/ping", ping)

    long_description = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus vehicula, metus et sodales fringilla, purus leo aliquet odio, non tempor ante urna aliquet nibh. Integer accumsan laoreet tincidunt. Vestibulum semper vehicula sollicitudin. Suspendisse dapibus neque vitae mattis bibendum. Morbi eu pulvinar turpis, quis malesuada ex. Vestibulum sed maximus diam. Proin semper fermentum suscipit. Duis at suscipit diam. Integer in augue elementum, auctor orci ac, elementum est. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Maecenas condimentum id arcu quis volutpat. Vestibulum sit amet nibh sodales, iaculis nibh eget, scelerisque justo.

    Nunc eget mauris lectus. Proin sit amet volutpat risus. Aliquam auctor nunc sit amet feugiat tempus. Maecenas nec ex dolor. Nam fermentum, mauris ut suscipit varius, odio purus luctus mauris, pretium interdum felis sem vel est. Proin a turpis vitae nunc volutpat tristique ac in erat. Pellentesque consequat rhoncus libero, ac sollicitudin odio tempus a. Sed vestibulum leo erat, ut auctor turpis mollis id. Ut nec nunc ex. Maecenas eu turpis in nibh placerat ullamcorper ac nec dui. Integer ac lacus neque. Donec dictum tellus lacus, a vulputate justo venenatis at. Morbi malesuada tellus quis orci aliquet, at vulputate lacus imperdiet. Nulla eu diam quis orci aliquam vulputate ac imperdiet elit. Quisque varius mollis dolor in interdum.
    """

    setup_swagger(app,
                  description=long_description,
                  title="My Custom Title",
                  api_version="1.0.3",
                  contact="my.custom.contact@example.com")

    web.run_app(app, host="127.0.0.1")

It produces:

.. image:: _static/swagger_custom_params.jpg

Adding Swagger from external file
---------------------------------

Per End-Point level
+++++++++++++++++++

We can add the Swagger doc from an external YAML file at end-point level. You only need to decorate the end-point function handler:

.. code-block:: python

    from aiohttp import web
    from aiohttp_swagger import *


    @swagger_path("example_swagger_partial.yaml")  # <-- Load Swagger info from external file
    async def example_2(request):
        """
        Example 3 handler description. This description is only for Sphinx.
        """
        return web.Response(text="Example")


    async def example_3(request):
        """
        Description end-point
        """
        return web.Response(text="Example")

    app = web.Application()

    app.router.add_route('GET', "/example1", example_1)
    app.router.add_route('GET', "/example2", example_2)

    setup_swagger(app)

    web.run_app(app, host="127.0.0.1")


External file must have this format:

.. code-block:: yaml

    tags:
    - user
    summary: Create user
    description: This can only be done by the logged in user.
    operationId: examples.api.api.createUser
    produces:
    - application/json
    parameters:
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
            type:
              - "string"
              - "null"
          firstName:
            type: string
          lastName:
            type: string
          email:
            type: string
          password:
            type: string
          phone:
            type: string
          userStatus:
            type: integer
            format: int32
            description: User Status
    responses:
      "201":
        description: successful operation

.. note::

    Pay attention that file doesn't contain information about HTTP Method or End-Point name. This information will be added automatically

Global Swagger YAML
+++++++++++++++++++

:samp:`aiohttp-swagger` also allow to build an external YAML Swagger file and load it before:

.. code-block:: python

    from aiohttp import web
    from aiohttp_swagger import *

    async def ping(request):
        """
        This is my usually Sphinx doc

        >>> import json
        >>> ping(None)

        :param request: Context injected by aiohttp framework
        :type request: RequestHandler
        """
        return web.Response(text="pong")

    app = web.Application()

    app.router.add_route('GET', "/ping", ping)

    setup_swagger(app, swagger_from_file="example_swagger.yaml")  # <-- Loaded Swagger from external YAML file

    web.run_app(app, host="127.0.0.1")

Data Definitions
+++++++++++++++++++

:samp:`aiohttp-swagger` allow to specify data models and to reuse it later when documenting API.
Following example shows how to define nested object and reuse it when writing swagger doc.

.. code-block:: python

    @asyncio.coroutine
    def users_with_data_def(request):
        """
        ---
        description: This endpoint returns user which is defined though data definition during initialization.
        tags:
        - Users
        produces:
        - application/json
        responses:
            "200":
                description: Successful operation, returns User object nested permisiion list
                schema:
                  $ref: '#/definitions/User'
        """
        users = fetch_users()
        return web.Response(json.dumps(users))

    app = web.Application()

    app.router.add_route('GET', "/users", users_with_data_def)

    setup_swagger(app, definitions={
        "User": {
          "type": "object",
          "properties": {
            "username": {
              "type": "string",
              "description": "User's username name",
              "default": "John"
            },
            "permissions": {
              "type": "array",
              "items": {
                "$ref": "#/definitions/Permission"
              }
            }
          }
        },
        "Permission": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string",
              "description": "Permission name"
            }
          }
        }
    })

    web.run_app(app, host="127.0.0.1")

Nested applications
+++++++++++++++++++

:samp:`aiohttp-swagger` is compatible with aiohttp `Nested applications <http://aiohttp.readthedocs.io/en/stable/web.html>`_ feature.
In this case `api_base_url` argument of `setup_swagger` function should be the same as `prefix` argument of `add_subapp` method:


.. code-block:: python

    from aiohttp import web
    from aiohttp_swagger import *

    async def ping(request):
        return web.Response(text="pong")

    sub_app = web.Application()

    sub_app.router.add_route('GET', "/ping", ping)

    setup_swagger(sub_app,
                  swagger_from_file="example_swagger.yaml",
                  api_base_url='/sub_app_prefix')

    app = web.Application()

    app.add_subapp(prefix='/sub_app_prefix', subapp=sub_app)

    web.run_app(app, host="127.0.0.1")

Swagger validation
+++++++++++++++++++

:samp:`aiohttp-swagger` allows to perform online swagger validation. By default this feature is turned off `(swagger_validator_url='')`:


.. code-block:: python

    setup_swagger(app,
                  api_base_url='/sub_app_prefix',
                  swagger_validator_url='//online.swagger.io/validator'
                  )
