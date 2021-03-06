
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
      install_requires=[
          "boto3==1.7.3",
          "google-api-python-client==1.6.6",
          "google-auth==1.4.1",
          "requests-oauthlib==0.8.0",
          "google-auth-oauthlib==0.2.0",
          "PyYAML==4.2b1"
      ],
      extras_require={
          "dev": [
	      "pytest==4.1.1",
              "pycodestyle",
              "pytest-mock",
              "pytest-cov",
              "coverage==4.5.2"
          ]
      },
      entry_points={
          "console_scripts": [
              "identityexchange=identityexchange.main:main"
          ]
      },
      )
