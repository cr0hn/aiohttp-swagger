from copy import deepcopy
import sys
import json
import logging
from functools import (
    wraps,
    reduce,
)
from traceback import format_exc
from itertools import groupby
from operator import itemgetter
from typing import (
    Mapping,
    Iterable,
    Any,
)

from aiohttp import web
from aiohttp.web import (
    Request,
    Response,
    json_response,
)
from collections import defaultdict
from jsonschema import (
    validate,
    ValidationError,
    FormatChecker,
)
from jsonschema.validators import validator_for


__all__ = (
    'validate_decorator',
)


logger = logging.getLogger(__name__)


def serialize_error_response(message: str, code: int, padding='error',
                             traceback: bool=False, **kwargs):
    obj = {padding: dict(message=message, code=code, **kwargs)}
    if traceback and sys.exc_info()[0]:
        obj[padding]['traceback'] = format_exc()
    return json.dumps(obj, default=lambda x: str(x))


def multi_dict_to_dict(mld: Mapping) -> Mapping:
    return {
        key: value[0]
        if isinstance(value, (list, tuple)) and len(value) == 1 else value
        for key, value in mld.items()
    }


def validate_schema(obj: Mapping, schema: Mapping):
    validate(obj, schema, format_checker=FormatChecker())


def validate_multi_dict(obj, schema):
    validate(multi_dict_to_dict(obj), schema, format_checker=FormatChecker())


def validate_content_type(swagger: Mapping, content_type: str):
    consumes = swagger.get('consumes')
    if consumes and not any(content_type == consume for consume in consumes):
        raise ValidationError(
            message='Unsupported content type: {}'.format(content_type))


async def validate_request(
        request: Request,
        parameter_groups: Mapping,
        swagger: Mapping):
    validate_content_type(swagger, request.content_type)
    for group_name, group_schemas in parameter_groups.items():
        if group_name == 'header':
            headers = request.headers
            for schema in group_schemas:
                validate_multi_dict(headers, schema)
        if group_name == 'query':
            query = request.query
            for schema in group_schemas:
                validate_multi_dict(query, schema)
        if group_name == 'formData':
            try:
                data = await request.post()
            except ValueError:
                data = None
            for schema in group_schemas:
                validate_multi_dict(data, schema)
        if group_name == 'body':
            try:
                content = await request.json()
            except json.JSONDecodeError:
                content = None
            for schema in group_schemas:
                validate_schema(content, schema)
        if group_name == 'path':
            params = dict(request.match_info)
            for schema in group_schemas:
                validate_schema(params, schema)


def adjust_swagger_item_to_json_schemes(*schemes: Mapping) -> Mapping:
    new_schema = {
        'type': 'object',
        'properties': {},
    }
    required_fields = []
    for schema in schemes:
        required = schema.get('required', False)
        name = schema['name']
        _schema = schema.get('schema')
        if _schema is not None:
            new_schema['properties'][name] = _schema
        else:
            new_schema['properties'][name] = {
                key: value for key, value in schema.items()
                if key not in ('required',)
            }
        if required:
            required_fields.append(name)
    if required_fields:
        new_schema['required'] = required_fields
    validator_for(new_schema).check_schema(new_schema)
    return new_schema


def adjust_swagger_body_item_to_json_schema(schema: Mapping) -> Mapping:
    required = schema.get('required', False)
    _schema = schema.get('schema')
    new_schema = deepcopy(_schema)
    if not required:
        new_schema = {
            'anyOf': [
                {'type': 'null'},
                new_schema,
            ]
        }
    validator_for(new_schema).check_schema(new_schema)
    return new_schema


def adjust_swagger_to_json_schema(parameter_groups: Iterable) -> Mapping:
    res = defaultdict(list)
    for group_name, group_schemas in parameter_groups:
        if group_name in ('query', 'header', 'path', 'formData'):
            json_schema = adjust_swagger_item_to_json_schemes(*group_schemas)
            res[group_name].append(json_schema)
        else:
            # only one possible schema for in: body
            schema = list(group_schemas)[0]
            json_schema = adjust_swagger_body_item_to_json_schema(schema)
            res[group_name].append(json_schema)
    return res


def validation_exc_to_dict(exc, code=400):
    paths = list(exc.path)
    field = str(paths[-1]) if paths else ''
    value = exc.instance
    validator = exc.validator
    message = exc.message
    try:
        schema = dict(exc.schema)
    except TypeError:
        schema = {}
    return {
        'message': message,
        'code': code,
        'description': {
            'validator': validator,
            'schema': schema,
            'field': field,
            'value': value,
        }
    }


def dereference_schema(swagger: Mapping, schema: Any) -> Any:

    def get_ref(ref: str):
        path = filter(None, ref.lstrip('#').split('/'))
        return reduce(dict.__getitem__, path, swagger)

    if isinstance(schema, dict):
        res = {}
        for key, value in schema.items():
            if key == '$ref':
                res.update(get_ref(value))
            else:
                res[key] = dereference_schema(swagger, value)
        return res
    elif isinstance(schema, list):
        res = []
        for value in schema:
            res.append(dereference_schema(swagger, value))
        return res
    else:
        return schema


def validate_decorator(swagger: Mapping, schema: Mapping):

    parameters = dereference_schema(swagger, schema).get('parameters', [])
    parameter_groups = adjust_swagger_to_json_schema(
        groupby(parameters, key=itemgetter('in'))
    )

    def _func_wrapper(func):

        @wraps(func)
        async def _wrapper(*args, **kwargs) -> Response:
            request = args[0].request \
                if isinstance(args[0], web.View) else args[0]
            try:
                await validate_request(request, parameter_groups, schema)
            except ValidationError as exc:
                logger.exception(exc)
                exc_dict = validation_exc_to_dict(exc)
                return json_response(
                    text=serialize_error_response(**exc_dict),
                    status=400
                )
            return await func(*args, **kwargs)

        return _wrapper

    return _func_wrapper
