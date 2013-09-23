import sys

import setuptools

with open('readme.txt') as readme:
	_long_description = readme.read()

# it seems that dateutil 2.0 only works under Python 3
dateutil_req=(
	['python-dateutil>=1.4,<2.0dev'] if sys.version_info < (3,0)
	else ['python-dateutil>=2.0'] )

setup_params=dict(
	name="svg.charts",
	use_hg_version=True,
	description="Python SVG Charting Library",
	long_description=_long_description,
	author="Jason R. Coombs",
	author_email="jaraco@jaraco.com",
	url="http://svg-charts.sourceforge.net",
	packages=setuptools.find_packages(),
	zip_safe=True,
	namespace_packages=['svg'],
	include_package_data=True,
	install_requires=[
		'cssutils>=0.9.8a3',
		'lxml>=2.0',
	] + dateutil_req,
	license="MIT",
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Intended Audience :: Science/Research",
		"Programming Language :: Python :: 2.6",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
	],
	entry_points={
	},
	tests_require=[
		'pytest',
	],
	setup_requires=[
		'hgtools',
		'pytest-runner',
	],
	use_2to3=True,
)

if __name__ == '__main__':
	setuptools.setup(**setup_params)
