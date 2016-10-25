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

    async def ping(request):
        """
        This is my usually Sphinx doc
    
        >>> import json
        >>> ping(None)
        
        :param request: Context injected by aiohttp framework
        :type request: RequestHandler
        
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
