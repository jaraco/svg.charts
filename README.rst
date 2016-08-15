.. image:: https://img.shields.io/pypi/v/svg.charts.svg
   :target: https://pypi.org/project/svg.charts

.. image:: https://img.shields.io/pypi/pyversions/svg.charts.svg

.. image:: https://img.shields.io/pypi/dm/svg.charts.svg

.. image:: https://img.shields.io/travis/jaraco/svg.charts/master.svg
   :target: http://travis-ci.org/jaraco/svg.charts

Status and License
------------------

``svg.charts`` is a pure-python library for generating charts and graphs
in SVG, originally based on the SVG::Graph Ruby package by Sean E. Russel.

``svg.charts`` supercedes ``svg_charts`` 1.1 and 1.2.

``svg.charts`` is written by Jason R. Coombs.  It is licensed under an
MIT-style permissive license.

You can install it with easy_install or pip::

  easy_install svg.charts
  pip install svg.charts

Or, check out the `repository source
<https://github.com/jaraco/svg.charts>`_.

Tests are continuously run by Travis-CI: |BuildStatus|_

.. |BuildStatus| image:: https://secure.travis-ci.org/jaraco/svg.charts.png
.. _BuildStatus: http://travis-ci.org/jaraco/svg.charts

To run the tests, refer to the .travis.yml file for the steps run on the
Travis-CI hosts.


Acknowledgements
----------------

``svg.charts`` depends heavily on lxml and cssutils. Thanks to the
contributors of those projects for stable, performant, standards-based
packages.

Sean E. Russel for creating the SVG::Graph Ruby package from which this
Python port was originally derived.

Leo Lapworth for creating the SVG::TT::Graph package which the Ruby
port was based on.

Stephen Morgan for creating the TT template and SVG.

Getting Started
---------------

``svg.charts`` has some examples (taken directly from the reference implementation)
in `tests/samples.py
<https://github.com/jaraco/svg.charts/blob/master/tests/samples.py>`_.
These examples show sample usage of the various chart types. They should provide a
good starting point for learning the usage of the library.

An example of using ``svg.charts`` in a `CherryPy
<http://www.cherrypy.org/>`_ web app can be found in `jaraco.site.charts
<https://github.com/jaraco/jaraco.site/blob/master/jaraco/site/charts.py>`_.
If the site is working, you can see the `rendered output here
<https://www.jaraco.com/charts/plot>`_.

``svg.charts`` also provides `API documentation
<http://pythonhosted.org/svg.charts/>`_.

Upgrade Notes
-------------

Upgrading from 1.x to 2.0

I suggest removing SVG 1.0 from the python installation.  This involves removing the SVG directory (or svg_chart*) from site-packages.

Change import statements to import from the new namespace, so::

    from SVG import Bar
    Bar.VerticalBar(...)

becomes::

    from svg.charts.bar import VerticalBar
    VerticalBar(...)

More To-Dos
-----------

-  Documentation! This package desperately needs some high-level,
   tutorial-style how-tos, and not just links to example code.
-  Implement javascript-based animation (See JellyGraph for a
   Silverlight example of what simple animation can do for a
   charting library).

Reporting Bugs and Getting Help
-------------------------------

This project is `hosted at Github
<https://github.com/jaraco/svg.charts>`_. Please use that site for
reporting bugs and requesting help. Patches are also welcome.
