Quick start
===========

Document an API is so simple:

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

    setup_swagger(app)

    web.run_app(app, host="127.0.0.1")

It produces:

.. image:: _static/swagger_ping.jpg

Where to access to API Doc
--------------------------

By default, API will be generated at URL: :samp:`yourdomain.com/api/doc`.

You can modify the URI adding the parameter :samp:`swagger_url` in :samp:`setup_swagger`:

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

    setup_swagger(app, swagger_url="/api/v1/doc")  # <-- NEW Doc URI

    web.run_app(app, host="127.0.0.1")