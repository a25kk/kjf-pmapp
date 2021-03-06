from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='pressapp.policy',
      version=version,
      description="Core policy package for the press release application.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pressapp'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'pressapp.channelmanagement',
          'pressapp.dispatcher',
          'pressapp.memberprofiles',
          'pressapp.overlays',
          'pressapp.presscontent',
          'pressapp.search',
          'pressapp.sitetheme',
          'pressapp.statusbar',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
