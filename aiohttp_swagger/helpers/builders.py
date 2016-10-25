from os.path import join, dirname, abspath
from collections import defaultdict

import yaml

try:
    import ujson as json
except ImportError:
    import json

from aiohttp import web
from jinja2 import Template

SWAGGER_TEMPLATE = abspath(join(dirname(__file__), "..", "templates"))


def _build_doc_from_func_doc(route):
    end_point_doc = route.handler.__doc__.splitlines()
    
    # Find Swagger start point in doc
    end_point_swagger_start = 0
    for i, doc_line in enumerate(end_point_doc):
        if "---" in doc_line:
            end_point_swagger_start = i + 1
            break
    
    # Build JSON YAML Obj
    end_point_swagger_doc = yaml.load("\n".join(end_point_doc[end_point_swagger_start:]))
    
    # Add to general Swagger doc
    return {route.method.lower(): end_point_swagger_doc}


def generate_doc_from_each_end_point(app: web.Application,
                                     *,
                                     api_base_url: str = "/",
                                     description: str = "Swagger API definition",
                                     api_version: str = "1.0.0",
                                     title: str = "Swagger API",
                                     contact: str = ""):
    # Clean description
    _start_desc = 0
    for i, word in enumerate(description):
        if word != '\n':
            _start_desc = i
            break
    cleaned_description = "    ".join(description[_start_desc:].splitlines())
    
    # Load base Swagger template
    swagger_base = Template(open(join(SWAGGER_TEMPLATE, "swagger.yaml"), "r").read()).render(
        description=cleaned_description,
        version=api_version,
        title=title,
        contact=contact,
        base_path=api_base_url
    )
    
    # The Swagger OBJ
    swagger = yaml.load(swagger_base)
    swagger["paths"] = defaultdict(dict)
    
    for route in app.router.routes():
        
        end_point_doc = None
        
        # If route has a external link to doc, we use it, not function doc
        if getattr(route.handler, "swagger_file", False):
            end_point_doc = yaml.load(open(route.handler.swagger_file, "r").read())
        
        # Check if end-point has Swagger doc
        elif route.handler.__doc__ is not None and "---" in route.handler.__doc__:
            end_point_doc = _build_doc_from_func_doc(route)
        
        # there is doc available?
        if end_point_doc:
            url_info = route._resource.get_info()
            if url_info.get("path", None):
                url = url_info.get("path")
            else:
                url = url_info.get("formatter")
    
            swagger["paths"][url] = end_point_doc
    
    return json.dumps(swagger)


def load_doc_from_yaml_file(doc_path: str):
    loaded_yaml = yaml.load(open(doc_path, "r").read())
    return json.dumps(loaded_yaml)


__all__ = ("generate_doc_from_each_end_point", "load_doc_from_yaml_file")

