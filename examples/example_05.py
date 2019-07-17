from os.path import join, dirname

from aiohttp import web

if __name__ == '__main__':
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

"""
    
    setup_swagger(app,
                  swagger_url="/api/v1/doc",
                  description=long_description,
                  title="My Custom Title",
                  api_version="1.0.3",
                  contact="my.custom.contact@example.com",
                  security_definitions={
                      'basicAuth': {
                          'type': 'basic',
                      },
                      'OAuth2': {
                          'type': 'oauth2',
                          'flow': 'accessCode',
                          'authorizationUrl': 'https://example.com/oauth/authorize',
                          'tokenUrl': 'https://example.com/oauth/token',
                          'scopes': {
                              'read': 'Grants read access',
                              'write': 'Grants write access',
                              'admin': 'Grants read and write access to administrative information',
                          }
                      }
                  })
    
    web.run_app(app, host="127.0.0.1")
