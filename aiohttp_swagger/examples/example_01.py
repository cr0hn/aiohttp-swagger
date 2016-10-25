from os.path import join, dirname

from aiohttp import web

if __name__ == '__main__':
    import os
    import sys
    
    parent_dir = os.path.dirname(os.path.dirname(os.path.join("..", os.path.abspath(__file__))))
    sys.path.insert(1, parent_dir)
    import aiohttp_swagger
    
    __package__ = str("aiohttp_swagger")
    
    from aiohttp_swagger import *

    async def example_1(request):
        """
        Description end-point

        ---
        tags:
        - Example
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
        """
        return web.Response(text="Example")


    @swagger_path("example_swagger_partial.yaml")
    async def example_2(request):
        """
        Description end-point
        
        ---
        tags:
        - Example
        summary: Create user
        description: This can only be done by the logged in user.
        operationId: examples.api.api.createUser
        produces:
        - application/json
        responses:
        "302":
            description: successful operation
            schema:
              type: string
            headers:
              Location:
                description: URL of redirected site
                type: string
        "404":
            description: short URL not found
        "405":
            description: invalid HTTP Method
        
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
    app.router.add_route('GET', "/example3", example_3)
    
    setup_swagger(app)
    
    web.run_app(app, host="127.0.0.1")
