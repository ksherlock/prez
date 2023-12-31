from setuptools import setup

setup(
	name = 'prez',
	packages = ['prez'],
	author = 'Kelvin Sherlock',
	entry_points = {
		'console_scripts': ['prez=prez.cli:main']

	},
)