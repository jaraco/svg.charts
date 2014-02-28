class PlotTester:
	def test_index_error_2010_04(self):
		"""
		Reported by Jean Schurger
		a 'IndexError: tuple index out of range' when there are only two
		values returned by float_range (in the case there are only two
		different 'y' values in the data) and 'scale_y_integers == True'.

		Credit to Jean for the test code as well.
		"""
		from svg.charts.plot import Plot
		g = Plot(dict(scale_y_integers = True))
		g.add_data(dict(data=[1, 0, 2, 1], title='foo'))
		g.burn()
