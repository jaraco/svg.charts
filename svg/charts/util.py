from more_itertools import always_iterable


def reverse_mapping(mapping):
    """
    For every key, value pair, return the mapping for the
    equivalent value, key pair

    >>> reverse_mapping({'a': 'b'}) == {'b': 'a'}
    True
    """
    keys, values = zip(*mapping.items())
    return dict(zip(values, keys))


def flatten_mapping(mapping):
    """
    For every key that has an __iter__ method, assign the values
    to a key for each.

    >>> flatten_mapping({'ab': 3, ('c','d'): 4}) == {'ab': 3, 'c': 4, 'd': 4}
    True
    """
    return {
        key: value for keys, value in mapping.items() for key in always_iterable(keys)
    }


def float_range(start=0, stop=None, step=1):
    """
    Much like the built-in function range, but accepts floats

    >>> tuple(float_range(0, 9, 1.5))
    (0.0, 1.5, 3.0, 4.5, 6.0, 7.5)
    """
    start = float(start)
    while start < stop:
        yield start
        start += step
