from setuptools import setup, find_packages
import sys

import mbtoolbox

with open('mbtoolbox/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue

open_kwds = {}
if sys.version_info > (3,):
    open_kwds['encoding'] = 'utf-8'

with open('README.md', **open_kwds) as f:
    readme = f.read()

setup(
    name='mbtoolbox',
    version=mbtoolbox.__version__,
    description="MBTiles toolbox tool for optimizing and verifying MBTiles files",
    long_description=readme,
    classifiers=[],
    keywords='',
    author='Lukas Martinelli',
    author_email='me@lukasmartinelli.ch',
    url='https://github.com/lukasmartinelli/mbtoolbox',
    license='BSD',
    packages=find_packages(exclude=[]),
    include_package_data=True,
    zip_safe=False,
    dependency_links = ['git://github.com/mapbox/mbutil.git@master#egg=mbutil-0.2.1'],
    install_requires=['docopt==0.6.2', 'mercantile==0.8.3',
                      'humanize==0.5.1', 'mbutil==0.2.1'],
    scripts = ['bin/mbverify', 'bin/mboptimize']
)
