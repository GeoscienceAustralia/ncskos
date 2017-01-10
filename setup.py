#!/usr/bin/env python

from distutils.core import setup
import os

version = '0.0.1'

setup(name='ncskosdump',
      version=version,
      packages=[
          'ncskosdump'
      ],
      package_data={
      },
      scripts=(['bin/ncskosdump'] if (os.name == 'posix')
               else (['bin\\ncskosdump.bat'] if (os.name == 'nt')
                     else [])),
      requires=[
          'distutils',
          'glob',
          'logging',
          'lxml',
          'netCDF4',
          'os',
          'pprint',
          'rdflib',
          're',
          'requests',
          'StringIO',
          'subprocess',
          'sys',
          'tempfile',
          'time',
          'unittest',
      ],
      url='https://github.com/nicholascar/ncskos',
      author='Nicholas Car & Alex Ip - Geoscience Australia',
      maintainer='Nicholas Car & Alex Ip - Geoscience Australia',
      maintainer_email='nicholas.car@ga.gov.au',
      description='NetCDF SKOS tools',
      long_description='Prototype NetCDF SKOS tools, including NetCDF Linked Data Dump utility which extends ncdump with SKOS vocabulary lookup',
      license='Creative Commons Attribution 4.0 International'
      )
