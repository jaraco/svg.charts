.. image:: https://img.shields.io/pypi/v/svg.charts.svg
   :target: https://pypi.org/project/svg.charts

.. image:: https://img.shields.io/pypi/pyversions/svg.charts.svg

.. image:: https://github.com/jaraco/svg.charts/actions/workflows/main.yml/badge.svg
   :target: https://github.com/jaraco/svg.charts/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. image:: https://readthedocs.org/projects/svgcharts/badge/?version=latest
   :target: https://svgcharts.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2025-informational
   :target: https://blog.jaraco.com/skeleton

``svg.charts`` is a pure-python library for generating charts
and graphs using Scalable Vector Graphics.

Acknowledgements
================

``svg.charts`` depends heavily on lxml and cssutils. Thanks to the
contributors of those projects for stable, performant, standards-based
packages.

Thanks to Sean E. Russel for creating the SVG::Graph Ruby
package from which this Python port was originally derived.

Thanks to Leo Lapworth for creating the SVG::TT::Graph
package which the Ruby port was based on.

Thanks to Stephen Morgan for creating the TT template and SVG.

Getting Started
===============

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
<http://svgcharts.readthedocs.io/en/latest>`_.

Contributing
============

This project is `hosted at Github
<https://github.com/jaraco/svg.charts>`_.

Please use that site for
reporting bugs and requesting help. Patches and contributions
of any kind are encouraged.
