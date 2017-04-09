from more_itertools.recipes import flatten

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
		assert 'circle' in g.burn()

	def test_pairs(self):
		"""
		Test that it is acceptable to use pairs for data.
		"""
		g = Plot(dict(show_data_points=True))
		g.add_data(dict(data=[(1, 0), (2, 1)], title='pairs'))
		assert 'circle' in g.burn()

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
		assert 'Sam' in svg
		assert 'Dan' in svg

	@staticmethod
	def get_data():
		yield (1, 0)
		yield (2, 1)

	def test_iterable_data_grouped(self):
		g = Plot()
		spec = dict(
			data=self.get_data(),
			title='labels',
		)
		g.add_data(spec)
		svg = g.burn()
		assert 'text="(1.00, 0.00)"' in svg

	def test_iterable_data_flat(self):
		g = Plot()
		spec = dict(
			data=flatten(self.get_data()),
			title='labels',
		)
		g.add_data(spec)
		svg = g.burn()
		assert 'text="(1.00, 0.00)"' in svg

	def test_issue_19(self):
		graph = Plot()
		options = dict(
			area_fill=True,
			key=True,
			width=1900,
			height=1040,
			graph_title="test issue 19",
			show_graph_title=True,
			no_css=False,
			# make sure the graph is always based at 0,0
			min_y_value=0,
			top_align=True,
			# only show integers on the x-axis
			scale_x_integers=True,
			# only show integers on the y-axis
			scale_y_integers=True,
		)
		graph.__dict__.update(options)

		durations = [0.0, 0.0, 0.0, 0.0]
		x_labels = range(len(durations))
		pairs = [item for items in zip(x_labels, durations) for item in items]

		graph.add_data(dict(data=pairs, title='test'))
		graph.burn()
