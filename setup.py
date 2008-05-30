from setuptools import setup, find_packages
import sys, os
from glob import glob

version = '0.1'

setup(name='ipblocker',
      version=version,
      description="IP Blocker",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Justin Azoff',
      author_email='JAzoff@uamail.albany.edu',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "SQLAlchemy >= 0.4",
          "WebHelpers",
          "ren_isac",
          "cisco",
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [paste.app_install]
      main = paste.script.appinstall:Installer
      """,
      test_suite='nose.collector',
      scripts=glob('scripts/*'),
      )
