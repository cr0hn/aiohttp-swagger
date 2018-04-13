import asyncio
from os.path import abspath, dirname, join
from types import FunctionType

from aiohttp import web

from .helpers import (generate_doc_from_each_end_point,
                      load_doc_from_yaml_file, swagger_path)

try:
    import ujson as json
except ImportError:
    import json


@asyncio.coroutine
def _swagger_home(request):
    """
    Return the index.html main file
    """
    return web.Response(
        text=request.app["SWAGGER_TEMPLATE_CONTENT"],
        content_type="text/html"
    )


@asyncio.coroutine
def _swagger_def(request):
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
                  contact: str = "",
                  swagger_home_decor: FunctionType = None,
                  swagger_def_decor: FunctionType = None,
                  swagger_info: dict = None,
                  json_only: bool = False):
    _swagger_url = ("/{}".format(swagger_url)
                    if not swagger_url.startswith("/")
                    else swagger_url)
    _base_swagger_url = _swagger_url.rstrip('/')
    _swagger_def_url = '{}/swagger.json'.format(_base_swagger_url)

    # Build Swagget Info
    if swagger_info is None:
        if swagger_from_file:
            swagger_info = load_doc_from_yaml_file(swagger_from_file)
        else:
            swagger_info = generate_doc_from_each_end_point(
                app, api_base_url=api_base_url, description=description,
                api_version=api_version, title=title, contact=contact
            )
    else:
        swagger_info = json.dumps(swagger_info)

    _swagger_home_func = _swagger_home
    _swagger_def_func = _swagger_def

    if swagger_home_decor is not None:
        _swagger_home_func = swagger_home_decor(_swagger_home)

    if swagger_def_decor is not None:
        _swagger_def_func = swagger_def_decor(_swagger_def)

    # Add API routes
    app.router.add_route('GET', _swagger_def_url, _swagger_def_func)

    app["SWAGGER_DEF_CONTENT"] = swagger_info

    if json_only:
        return

    app.router.add_route('GET', _swagger_url, _swagger_home_func)
    app.router.add_route('GET', "{}/".format(_base_swagger_url),
                         _swagger_home_func)

    # Set statics
    statics_path = '{}/swagger_static'.format(_base_swagger_url)
    app.router.add_static(statics_path, STATIC_PATH)

    # --------------------------------------------------------------------------
    # Build templates
    # --------------------------------------------------------------------------
    with open(join(STATIC_PATH, "index.html"), "r") as f:
        app["SWAGGER_TEMPLATE_CONTENT"] = (
            f.read()
            .replace("##SWAGGER_CONFIG##", '/{}{}'.
                     format(api_base_url.lstrip('/'), _swagger_def_url))
            .replace("##STATIC_PATH##", '/{}{}'.
                     format(api_base_url.lstrip('/'), statics_path))
        )


__all__ = ("setup_swagger", "swagger_path")
