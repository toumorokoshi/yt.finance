"""
lib.py: a set of utility methods for yt.finance
"""
import functools

__author__ = 'yusuke tsutsumi'


def precision(f):
    """
    A decorator method for adding an optional precision attribute to
    methods, which would retroactively round the return values.

    """

    @functools.wraps(f)
    def precision_f(*args, **kwargs):
        precision = -1
        if 'precision' in kwargs:
            precision = kwargs['precision']
            del(kwargs['precision'])

        return_value = f(*args, **kwargs)

        if precision > -1:
            return recursive_round(return_value, precision)
        return return_value

    return precision_f


def recursive_round(value, precision):
    """
    Recursively round an arbitrary python object, to an precision precision

    >>> recursive_round({'a': 1.000808, 'b': 'c'}, 2)
    {'a': 1.0, 'b': 'c'}
    >>> recursive_round(1.070980, 2)
    1.07
    """
    if type(value) == float:
        return round(value, precision)
    elif type(value) == list:
        return [recursive_round(v, precision) for v in value]
    elif type(value) == dict:
        return dict([(k, recursive_round(v, precision)) for k, v in value.items()])
    else:
        return value
