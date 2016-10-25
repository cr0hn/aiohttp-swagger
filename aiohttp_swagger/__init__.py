from os.path import join, dirname, abspath

from aiohttp import web

from .helpers import swagger_path, generate_doc_from_each_end_point, load_doc_from_yaml_file


async def _swagger_home(request):
    """
    Return the index.html main file
    """
    return web.Response(text=request.app["SWAGGER_TEMPLATE_CONTENT"], content_type="text/html")


async def _swagger_def(request):
    """
    Returns the Swagger JSON Definition
    """
    return web.json_response(text=request.app["SWAGGER_DEF_CONTENT"])


STATIC_PATH = abspath(join(dirname(__file__), "swagger_ui"))


def setup_swagger(app: web.Application,
                  *,
                  swagger_from_file: str = None,
                  swagger_url: str = "/api/doc",
                  api_base_url: str = "/",
                  description: str = "Swagger API definition",
                  api_version: str = "1.0.0",
                  title: str = "Swagger API",
                  contact: str = ""):
    _swagger_url = "/{}".format(swagger_url) if not swagger_url.startswith("/") else swagger_url
    _swagger_def_url = '{}/swagger.json'.format(_swagger_url)
    
    # Build Swagget Info
    if swagger_from_file:
        swagger_info = load_doc_from_yaml_file(swagger_from_file)
    else:
        swagger_info = generate_doc_from_each_end_point(app,
                                                        api_base_url=api_base_url,
                                                        description=description,
                                                        api_version=api_version,
                                                        title=title,
                                                        contact=contact)
    
    # Add API routes
    app.router.add_route('GET', _swagger_url, _swagger_home)
    app.router.add_route('GET', "{}/".format(_swagger_url), _swagger_home)
    app.router.add_route('GET', _swagger_def_url, _swagger_def)
    
    # Set statics
    statics_path = '{}/swagger_static'.format(_swagger_url)
    app.router.add_static(statics_path, STATIC_PATH)
    
    # --------------------------------------------------------------------------
    # Build templates
    # --------------------------------------------------------------------------
    app["SWAGGER_DEF_CONTENT"] = swagger_info
    app["SWAGGER_TEMPLATE_CONTENT"] = open(join(STATIC_PATH, "index.html"), "r").read() \
        .replace("##SWAGGER_CONFIG##", _swagger_def_url) \
        .replace("##STATIC_PATH##", statics_path)


__all__ = ("setup_swagger", "swagger_path")
