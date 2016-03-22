Changes
-------

3.1.1
~~~~~

* #8: Subtitle is now rendering the subtitle and not the title
  again.

3.1
~~~

* Adding a couple small dependencies eliminated a lot of duplicated code
  in the ``util`` module.
* Corrected error when ``stacked`` was used in Line charts.

3.0
~~~

* Dropped support for Python 2.6.
* Requires setuptools for installation.
* Filter out comments when parsing CSS.
* Corrected errors in ``Graph.render_inline_styles``.

2.3
~~~

* #4: Added hook in Graph to allow overriding of the attributes on the
  root SVG element. One can now override or monkeypatch
  ``Graph._get_root_attributes`` to alter the rendering of the root
  attributes such as width and height. For example, to omit width and height::

    class MyPlot(plot.Plot):
        def _get_root_attributes(self):
            attrs = super(MyPlot, self)._get_root_attributes()
            del attrs['width']
            del attrs['height']
            return attrs

2.2.2
~~~~~

* #1: Fixed javascript ID names in TimeSeries labels.

2.2.1
~~~~~

* #5: Fixed references to class attributes in ``graph.py``.

2.2
~~~

* SF Issue #1: Fixed installation on Unix systems again. Author's preference
  for lowercase ``readme.txt`` was trumped by `setuptools #100
  <https://bitbucket.org/pypa/setuptools/issue/100/>`_.
* Moved hosting to BitBucket.
* Established Continuous Integration Tests on Github mirror using Travis-CI.

2.1
~~~

* Project now builds and tests pass on Python 3 without 2to3.

2.0.9
~~~~~

* Corrected buggy logic in y-axis label rendering (thanks to Emmanuel
  Blot).
* Converted to Unix line endings.

2.0.8
~~~~~

* Updated to latest cssutils with Python 3 support. Thanks Christof!
* Fixed a few remaining issues with Python 3 compatibility.

2.0.7
~~~~~

* Fixed bug in rendering of Pie Chart styles.
* Improved testing framework. Now samples are at least generated as part
  of the test suite.
* Fixed bug in javascript when label ids had spaces. See #3139197.
* Fixed build issue where package data wasn't included due to 2to3
  technique. Now using distribute technique and installation on Python
  3 requires distribute.

2.0.6
~~~~~

* Fixed bug where x axis labels would not be rendered properly if the
  largest value was the same as the largest visible x value on the
  chart.

2.0.5
~~~~~

* Altered the way CSS files are loaded, so they can be more easily
  customized by subclasses (and less dependent on the class names).

2.0.4
~~~~~

* A small attempt to improve the documentation - added links to examples
  that already exist.

2.0.3
~~~~~

* Fix IndexError in ``svg.charts.plot.Plot.field_size`` when there are
  only two values returned by float_range (in the case there are only
  two different 'y' values in the data) and scale_y_integers == True.
  Credit to `Jean Schurger <http://schurger.org/>`_ for the patch.
* Fixed problem in setup.py installing on Unix OS (case sensitivity of
  readme.txt). Credit to Luke Miller and Jean Schurger for supplying
  a patch for this issue.

2.0.2
~~~~~

* Updated cssutils dependency to 0.9.6 (currently in beta) to require the CSS profiles support.
* Completed an SVG CSS profile according to the SVG 1.1 spec.

2.0.1
~~~~~

* Added preliminary SVG CSS profile, suitable for stock CSS properties.

2.0
~~~~~

* First major divergence from the Ruby reference implementation
* Now implemented as a namespace package (svg.charts instead of svg_charts)
* Changed XML processor to lxml
* Enabled extensible css support using cssutils, greatly reducing static CSS
* Renamed modules and methods to be more consistent with PEP-8 naming convention

1.2
~~~

* Bug fixes

1.1
~~~

* First public release