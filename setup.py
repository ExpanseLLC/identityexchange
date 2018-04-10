#!/usr/bin/env python3.6

from distutils.core import setup

from setuptools import find_packages

setup(name="IdentityExchange",
      version="1.0",
      description="Python Identity Exchange for Google and AWS",
      author="ExpanseLLC",
      author_email="info@expansellc.io",
      url="http://expansellc.io/",
      packages=find_packages(exclude=["tests"]),
      tests_require=["pytest"],
      install_requires=[
          "boto3==1.7.3",
          "google-api-python-client==1.6.6",
          "google-auth==1.4.1",
          "requests-oauthlib==0.8.0",
          "google-auth-oauthlib==0.2.0",
          "PyYAML==3.12"
      ],
      extras_require={
          "dev": [
              "pycodestyle",
              "pytest-mock",
              "pytest-cov",
              "coverage"
          ]
      },
      entry_points={
          "console_scripts": [
              "expanse-idx=identityexchange.main:main"
          ]
      },
      )
