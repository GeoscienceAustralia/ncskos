#!/usr/bin/env python

from distutils.core import setup
import os

version = '0.0.0'

setup(name='ncskosdump',
      version=version,
      packages=[
          'ncskosdump',
          'ncskosdump.test'
      ],
      package_data={
          'ncskosdump.test': ['sst.ltm.1971-2000_skos.nc']
      },
      scripts=(['bin/ncskosdump'] if (os.name == 'posix')
               else (['bin\\ncskosdump.bat'] if (os.name == 'nt')
                     else [])),
      requires=[
          'distutils',
          'lxml',
          'rdflib',
          'requests',
      ],
      url='https://github.com/nicholascar/ncskosdump',
      author='Nicholas Car & Alex Ip - Geoscience Australia',
      maintainer='Nicholas Car & Alex Ip - Geoscience Australia',
      maintainer_email='nicholas.car@ga.gov.au',
      description='NetCDF Linked Data Dump utility',
      long_description='Prototype NetCDF Linked Data Dump utility - extends ncdump with SKOS vocabulary lookup',
      license='Creative Commons Attribution 4.0 International'
      )
