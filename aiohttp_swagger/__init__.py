import asyncio
from os.path import (
    abspath,
    dirname,
    join,
)
from types import FunctionType

from aiohttp import web

from .helpers import (
    generate_doc_from_each_end_point,
    load_doc_from_yaml_file,
    load_doc_from_yaml_str,
    swagger_path,
    swagger_validation,
    add_swagger_validation,
)

try:
    import ujson as json
except ImportError:
    import json

__all__ = (
    "setup_swagger",
    "swagger_path",
    "swagger_validation",
)


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
                  swagger_from_str: str = None,
                  swagger_url: str = "/api/doc",
                  api_base_url: str = "/",
                  swagger_validator_url: str = "",
                  description: str = "Swagger API definition",
                  api_version: str = "1.0.0",
                  title: str = "Swagger API",
                  contact: str = "",
                  swagger_home_decor: FunctionType = None,
                  swagger_def_decor: FunctionType = None,
                  swagger_merge_with_file: bool = False,
                  swagger_validate_schema: bool = False,
                  swagger_info: dict = None):
    _swagger_url = ("/{}".format(swagger_url)
                    if not swagger_url.startswith("/")
                    else swagger_url)
    _base_swagger_url = _swagger_url.rstrip('/')
    _swagger_def_url = '{}/swagger.json'.format(_base_swagger_url)

    # Build Swagger Info
    if swagger_info is None:
        if swagger_from_file or swagger_from_str:
            if swagger_from_file:
                swagger_info = load_doc_from_yaml_file(swagger_from_file)
            elif swagger_from_str:
                swagger_info = load_doc_from_yaml_str(swagger_from_str)
            if swagger_merge_with_file:
                swagger_end_points_info = generate_doc_from_each_end_point(
                    app, api_base_url=api_base_url, description=description,
                    api_version=api_version, title=title, contact=contact
                )
                paths = swagger_end_points_info.pop('paths', None)
                swagger_info.update(swagger_end_points_info)
                if paths is not None:
                    if 'paths' not in swagger_info:
                        swagger_info['paths'] = {}
                    for ph, description in paths.items():
                        for method, desc in description.items():
                            if ph not in swagger_info['paths']:
                                swagger_info['paths'][ph] = {}
                            swagger_info['paths'][ph][method] = desc
        else:
            swagger_info = generate_doc_from_each_end_point(
                app, api_base_url=api_base_url, description=description,
                api_version=api_version, title=title, contact=contact
            )

    if swagger_validate_schema:
        add_swagger_validation(app, swagger_info)

    swagger_info = json.dumps(swagger_info)

    _swagger_home_func = _swagger_home
    _swagger_def_func = _swagger_def

    if swagger_home_decor is not None:
        _swagger_home_func = swagger_home_decor(_swagger_home)

    if swagger_def_decor is not None:
        _swagger_def_func = swagger_def_decor(_swagger_def)

    # Add API routes
    app.router.add_route('GET', _swagger_url, _swagger_home_func)
    app.router.add_route('GET', "{}/".format(_base_swagger_url),
                         _swagger_home_func)
    app.router.add_route('GET', _swagger_def_url, _swagger_def_func)

    # Set statics
    statics_path = '{}/swagger_static'.format(_base_swagger_url)
    app.router.add_static(statics_path, STATIC_PATH)

    # --------------------------------------------------------------------------
    # Build templates
    # --------------------------------------------------------------------------
    app["SWAGGER_DEF_CONTENT"] = swagger_info
    with open(join(STATIC_PATH, "index.html"), "r") as f:
        app["SWAGGER_TEMPLATE_CONTENT"] = (
            f.read()
            .replace("##SWAGGER_CONFIG##", '{}{}'.
                     format(api_base_url.lstrip('/'), _swagger_def_url))
            .replace("##STATIC_PATH##", '{}{}'.
                     format(api_base_url.lstrip('/'), statics_path))
            .replace("##SWAGGER_VALIDATOR_URL##", swagger_validator_url)
        )
