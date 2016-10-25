from os.path import join, dirname

from aiohttp import web

if __name__ == '__main__':
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
    
    setup_swagger(app, swagger_from_file="example_swagger.yaml")
    
    web.run_app(app, host="127.0.0.1")
