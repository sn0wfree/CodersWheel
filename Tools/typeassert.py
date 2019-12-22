# coding=utf8
import inspect

from functools import wraps

# try:
from inspect import signature


# except ImportError as e:
#     from funcsigs import signature


def typeassert(*ty_args, **ty_kwargs):
    def decorate(func):
        if not __debug__:
            return func
        sig = signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments
        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(value, bound_types[name]):
                        raise TypeError('Argument {} must be {}'.format(name.bound_types[name]))
            return func(*args, **kwargs)
        return wrapper
    return decorate


if __name__ == '__main__':
    @typeassert(a=str, b=int)
    def test1(a: str, b: int = 1):
        return b + 1


    pass
