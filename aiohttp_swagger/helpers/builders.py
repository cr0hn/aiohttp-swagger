from collections import defaultdict
from os.path import abspath, dirname, join

import yaml
from aiohttp import web
from aiohttp.hdrs import METH_ANY, METH_ALL
from jinja2 import Environment, BaseLoader

try:
    import ujson as json
except ImportError: # pragma: no cover
    import json


SWAGGER_TEMPLATE = abspath(join(dirname(__file__), "..", "templates"))


def _extract_swagger_docs(end_point_doc, method="get"):
    # Find Swagger start point in doc
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
    return {method: end_point_swagger_doc}

def _build_doc_from_func_doc(route):

    out = {}

    if issubclass(route.handler, web.View) and route.method == METH_ANY:
        method_names = {
            attr for attr in dir(route.handler) \
            if attr.upper() in METH_ALL
        }
        for method_name in method_names:
            method = getattr(route.handler, method_name)
            if method.__doc__ is not None and "---" in method.__doc__:
                end_point_doc = method.__doc__.splitlines()
                out.update(_extract_swagger_docs(end_point_doc, method=method_name))

    else:
        try:
            end_point_doc = route.handler.__doc__.splitlines()
        except AttributeError:
            return {}
        out.update(_extract_swagger_docs(end_point_doc))
    return out

def generate_doc_from_each_end_point(
        app: web.Application,
        *,
        api_base_url: str = "/",
        description: str = "Swagger API definition",
        api_version: str = "1.0.0",
        title: str = "Swagger API",
        contact: str = "",
        security_definitions: dict = None):
    # Clean description
    _start_desc = 0
    for i, word in enumerate(description):
        if word != '\n':
            _start_desc = i
            break
    cleaned_description = "    ".join(description[_start_desc:].splitlines())

    def nesteddict2yaml(d, indent=10, result=""):
        for key, value in d.items():
            result += " " * indent + str(key) + ':'
            if isinstance(value, dict):
                result = nesteddict2yaml(value, indent + 2, result + "\n")
            else:
                result += " " + str(value) + "\n"
        return result

    # Load base Swagger template
    jinja2_env = Environment(loader=BaseLoader())
    jinja2_env.filters['nesteddict2yaml'] = nesteddict2yaml

    with open(join(SWAGGER_TEMPLATE, "swagger.yaml"), "r") as f:
        swagger_base = (
            jinja2_env.from_string(f.read()).render(
                description=cleaned_description,
                version=api_version,
                title=title,
                contact=contact,
                base_path=api_base_url,
                security_definitions=security_definitions)
        )

    # The Swagger OBJ
    swagger = yaml.load(swagger_base)
    swagger["paths"] = defaultdict(dict)

    for route in app.router.routes():

        end_point_doc = None

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

    return json.dumps(swagger)


def load_doc_from_yaml_file(doc_path: str):
    loaded_yaml = yaml.load(open(doc_path, "r").read())
    return json.dumps(loaded_yaml)


__all__ = ("generate_doc_from_each_end_point", "load_doc_from_yaml_file")
