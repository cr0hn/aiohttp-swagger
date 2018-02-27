import logging
from typing import (
    MutableMapping,
    Mapping,
)
from collections import defaultdict
from os.path import (
    abspath,
    dirname,
    join,
)

import yaml
from aiohttp import web
from aiohttp.hdrs import METH_ANY, METH_ALL
from jinja2 import Template
try:
    import ujson as json
except ImportError:  # pragma: no cover
    import json

from .validation import validate_decorator


SWAGGER_TEMPLATE = abspath(join(dirname(__file__), "..", "templates"))


def _extract_swagger_docs(end_point_doc: str) -> Mapping:
    """
    Find Swagger start point in doc.
    """
    end_point_swagger_start = 0
    for i, doc_line in enumerate(end_point_doc):
        if "---" in doc_line:
            end_point_swagger_start = i + 1
            break

    # Build JSON YAML Obj
    try:
        end_point_swagger_doc = (
            yaml.load("\n".join(end_point_doc[end_point_swagger_start:]))
        )
    except yaml.YAMLError:
        end_point_swagger_doc = {
            "description": "⚠ Swagger document could not be loaded "
                           "from docstring ⚠",
            "tags": ["Invalid Swagger"]
        }
    return end_point_swagger_doc


def _build_doc_from_func_doc(route):

    out = {}

    if issubclass(route.handler, web.View) and route.method == METH_ANY:
        method_names = {
            attr for attr in dir(route.handler)
            if attr.upper() in METH_ALL
        }
        for method_name in method_names:
            method = getattr(route.handler, method_name)
            if method.__doc__ is not None and "---" in method.__doc__:
                end_point_doc = method.__doc__.splitlines()
                out[method_name] = _extract_swagger_docs(end_point_doc)

    else:
        try:
            end_point_doc = route.handler.__doc__.splitlines()
        except AttributeError:
            return {}
        out[route.method.lower()] = _extract_swagger_docs(end_point_doc)
    return out


def generate_doc_from_each_end_point(
        app: web.Application,
        *,
        api_base_url: str = "/",
        description: str = "Swagger API definition",
        api_version: str = "1.0.0",
        title: str = "Swagger API",
        contact: str = "") -> MutableMapping:
    # Clean description
    _start_desc = 0
    for i, word in enumerate(description):
        if word != '\n':
            _start_desc = i
            break
    cleaned_description = "    ".join(description[_start_desc:].splitlines())

    # Load base Swagger template
    with open(join(SWAGGER_TEMPLATE, "swagger.yaml"), "r") as f:
        swagger_base = (
            Template(f.read()).render(
                description=cleaned_description,
                version=api_version,
                title=title,
                contact=contact,
                base_path=api_base_url)
        )

    # The Swagger OBJ
    swagger = yaml.load(swagger_base)
    swagger["paths"] = defaultdict(dict)

    for route in app.router.routes():

        # If route has a external link to doc, we use it, not function doc
        if getattr(route.handler, "swagger_file", False):
            try:
                with open(route.handler.swagger_file, "r") as f:
                    end_point_doc = {
                        route.method.lower():
                            yaml.load(f.read())
                    }
            except yaml.YAMLError:
                end_point_doc = {
                    route.method.lower(): {
                        "description": "⚠ Swagger document could not be "
                                       "loaded from file ⚠",
                        "tags": ["Invalid Swagger"]
                    }
                }
            except FileNotFoundError:
                end_point_doc = {
                    route.method.lower(): {
                        "description":
                            "⚠ Swagger file not "
                            "found ({}) ⚠".format(route.handler.swagger_file),
                        "tags": ["Invalid Swagger"]
                    }
                }

        # Check if end-point has Swagger doc
        else:
            end_point_doc = _build_doc_from_func_doc(route)

        # there is doc available?
        if end_point_doc:
            url_info = route._resource.get_info()
            if url_info.get("path", None):
                url = url_info.get("path")
            else:
                url = url_info.get("formatter")

            swagger["paths"][url].update(end_point_doc)
    return swagger


def load_doc_from_yaml_file(doc_path: str) -> MutableMapping:
    return yaml.load(open(doc_path, "r").read())


def add_swagger_validation(app, swagger_info: Mapping):
    for route in app.router.routes():
        method = route.method.lower()
        handler = route.handler
        url_info = route.get_info()
        url = url_info.get('path') or url_info.get('formatter')

        if method != '*':
            swagger_endpoint_info_for_method = \
                swagger_info['paths'].get(url, {}).get(method)
            swagger_endpoint_info = \
                {method: swagger_endpoint_info_for_method} if \
                swagger_endpoint_info_for_method is not None else {}
        else:
            # all methods
            swagger_endpoint_info = swagger_info['paths'].get(url, {})
        for method, info in swagger_endpoint_info.items():
            logging.debug(
                'Added validation for method: {}. Path: {}'.
                format(method.upper(), url)
            )
            if issubclass(handler, web.View) and route.method == METH_ANY:
                # whole class validation
                should_be_validated = getattr(handler, 'validation', False)
                cls_method = getattr(handler, method, None)
                if cls_method is not None:
                    if not should_be_validated:
                        # method validation
                        should_be_validated = \
                            getattr(handler, 'validation', False)
                    if should_be_validated:
                        new_cls_method = \
                            validate_decorator(swagger_info, info)(cls_method)
                        setattr(handler, method, new_cls_method)
            else:
                should_be_validated = getattr(handler, 'validation', False)
                if should_be_validated:
                    route._handler = \
                        validate_decorator(swagger_info, info)(handler)


__all__ = (
    "generate_doc_from_each_end_point",
    "load_doc_from_yaml_file",
    "add_swagger_validation",
)
