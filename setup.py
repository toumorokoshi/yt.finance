#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='yt.finance',
      version='0.1',
      description='A very basic finance library',
      author='Yusuke Tsutsumi',
      author_email='yusuke@yusuketsutsumi.com',
      url='https://github.com/toumorokoshi/yt.finance',
      packages=['yt', 'yt.finance'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
      ],
      test_suite="tests"
     )
