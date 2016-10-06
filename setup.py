#!/usr/bin/env python

from distutils.core import setup
import os

version = '0.0.0'

os.name

setup(name='nclddump',
      version=version,
      packages=[
          'nclddump',
          'nclddump.test'
      ],
      package_data={
          'nclddump.test': ['sst.ltm.1971-2000_skos.nc']
      },
      scripts=(['bin/nclddump.sh'] if (os.name == 'posix') 
               else (['bin\\nclddump.bat'] if (os.name == 'nt') 
                     else [])),
      requires=[
          'distutils',
          'lxml',
          'rdflib',
          'requests',
      ],
      url='https://github.com/nicholascar/nclddump',
      author='Nicholas Car & Alex Ip - Geoscience Australia',
      maintainer='Nicholas Car & Alex Ip - Geoscience Australia',
      maintainer_email='nicholas.car@ga.gov.au',
      description='NetCDF Linked Data Dump utility',
      long_description='Prototype NetCDF Linked Data Dump utility - extends ncdump with SKOS vocabulary lookup',
      license='Apache License 2.0'
      )
