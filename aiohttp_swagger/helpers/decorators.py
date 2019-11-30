from functools import partial
from inspect import isfunction, isclass

__all__ = (
    'swagger_path',
    'swagger_validation',
)


class swagger_path:

    def __init__(self, swagger_file):
        self.swagger_file = swagger_file
    
    def __call__(self, f):
        f.swagger_file = self.swagger_file
        return f


def swagger_validation(func=None, *, validation=True):

    if func is None or not (isfunction(func) or isclass(func)):
        validation = func
        return partial(swagger_validation, validation=validation)

    func.validation = validation
    return func
