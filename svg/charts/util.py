from __future__ import division

import six

from tempora import divide_timedelta


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
	return dict(flatten_items(mapping.items()))

def flatten_items(items):
	for keys, value in items:
		if hasattr(keys, '__iter__') and not isinstance(keys, six.string_types):
			for key in keys:
				yield (key, value)
		else:
			yield (keys, value)

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

class TimeScale(object):
	"Describes a scale factor based on time instead of a scalar"
	def __init__(self, width, range):
		self.width = width
		self.range = range

	def __mul__(self, delta):
		scale = divide_timedelta(delta, self.range)
		return scale*self.width

# the following three functions were copied from jaraco.util.iter_

# todo, factor out caching capability
class iterable_test(dict):
	"Test objects for iterability, caching the result by type"
	def __init__(self, ignore_classes=six.string_types):
		"""ignore_classes must include str, because if a string
		is iterable, so is a single character, and the routine runs
		into an infinite recursion"""
		str_included = set(ignore_classes) >= set(six.string_types)
		assert str_included, 'str must be in ignore_classes'
		self.ignore_classes = ignore_classes

	def __getitem__(self, candidate):
		return dict.get(self, type(candidate)) or self._test(candidate)

	def _test(self, candidate):
		try:
			if isinstance(candidate, self.ignore_classes):
				raise TypeError
			iter(candidate)
			result = True
		except TypeError:
			result = False
		self[type(candidate)] = result
		return result

def iflatten(subject, test=None):
	if test is None:
		test = iterable_test()
	if not test[subject]:
		yield subject
	else:
		for elem in subject:
			for subelem in iflatten(elem, test):
				yield subelem

def flatten(subject, test=None):
	"""flatten an iterable with possible nested iterables.
	Adapted from
	http://mail.python.org/pipermail/python-list/2003-November/233971.html
	>>> flatten(['a','b',['c','d',['e','f'],'g'],'h']) == ['a','b','c','d','e','f','g','h']
	True

	Note this will normally ignore string types as iterables.
	>>> flatten(['ab', 'c'])
	['ab', 'c']
	"""
	return list(iflatten(subject, test))
