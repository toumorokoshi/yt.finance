"""
lib.py: a set of utility methods for yt.finance
"""
import functools
from numpy import float64

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
    if type(value) in [float, float64]:
        return round(value, precision)
    elif type(value) == list:
        return [recursive_round(v, precision) for v in value]
    elif type(value) == dict:
        return dict([(k, recursive_round(v, precision)) for k, v in value.items()])
    else:
        return value


def __calculate_lattice_value(initial_value, variance_up, variance_down,
                              positive_changes, negative_changes):
    return initial_value * (variance_up ** positive_changes) * \
        ((1.0 * variance_down) ** negative_changes)


@precision
def generate_lattice(periods, initial_value, variance_up, variance_down):
    """
    Generate a lattice
    """
    return_values = []
    for i in range(periods + 1):
        return_column = []
        for j in range(i):
            value = __calculate_lattice_value(initial_value,
                                              variance_up, variance_down,
                                              i - j, j)
            return_column.append(value)
        value = __calculate_lattice_value(initial_value,
                                          variance_up, variance_down,
                                          0, i)
        return_column.append(value)
        return_values.append(return_column)
    return return_values


def price_lattice(periods, lattice, initial_values, method):
    """
    Generate a price lattice with
    * p periods
    * a underlying security lattice l
    * initial_values
    * and a method m which takes:
      * the underlying security lattice
      * the return_lattice
    """
    return_lattice = initial_values
    for i in range(periods):
        lattice_column = periods - i - 1
        column = []
        for j in range(lattice_column + 1):
            value = method(lattice=lattice,
                           return_lattice=return_lattice,
                           col=lattice_column,
                           row=j)
            column.append(value)
        return_lattice.insert(0, column)
    column.append(value)
    return return_lattice
