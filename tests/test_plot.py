from svg.charts.plot import Plot


class TestPlot:
	def test_index_error_2010_04(self):
		"""
		Reported by Jean Schurger
		a 'IndexError: tuple index out of range' when there are only two
		values returned by float_range (in the case there are only two
		different 'y' values in the data) and 'scale_y_integers == True'.

		Credit to Jean for the test code as well.
		"""
		g = Plot(dict(scale_y_integers = True))
		g.add_data(dict(data=[1, 0, 2, 1], title='foo'))
		g.burn()

	def test_inline_styles(self):
		g = Plot(dict(css_inline=True))
		g.add_data(dict(data=[1, 0, 2, 1], title='foo'))
		g.burn()

	def test_python3_show_points(self):
		"""
		Test that show_data_points creates
		circle elements in output.
		"""
		g = Plot(dict(show_data_points=True))
		g.add_data(dict(data=[1, 0, 2, 1], title='foo'))
		assert b'circle' in g.burn()

	def test_pairs(self):
		"""
		Test that it is acceptable to use pairs for data.
		"""
		g = Plot(dict(show_data_points=True))
		g.add_data(dict(data=[(1, 0), (2, 1)], title='pairs'))
		assert b'circle' in g.burn()

	def test_text(self):
		"""
		Test that data with .text attributes make
		text labels.
		"""
		from collections import namedtuple

		D = namedtuple("D", 'x y text')

		g = Plot(dict(show_data_values=True))
		g.add_data(dict(data=[
			D(1, 0, 'Sam'),
			D(2, 1, 'Dan'),
			],
			title='labels'))
		svg = g.burn()
		assert b'Sam' in svg
		assert b'Dan' in svg

