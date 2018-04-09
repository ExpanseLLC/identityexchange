#!/usr/bin/env python3.6

from distutils.core import setup

from setuptools import find_packages

setup(name='IdentityExchange',
      version='1.0',
      description='Python Identity Exchange for Google and AWS',
      author='ExpanseLLC',
      author_email='info@expansellc.io',
      url='http://expansellc.io/',
      packages=find_packages(exclude=["tests"]),
      tests_require=['pytest'],
      # uncomment and add dependencies when needed
      # install_requires=[
      #     'name==1.0.0',
      # ],
      extras_require={
          'dev': [
              'pytest-mock',
              'pytest-cov'
          ]
      },
      entry_points={
          'console_scripts': [
              'hello-world=hello_world.main:main'
          ]
      },
      )
