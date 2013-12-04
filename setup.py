import os

from setuptools import setup, find_packages
version = '0.1.0'
classifiers = [
  "Programming Language :: Python",
  "Framework :: Paste",
  "Framework :: Plone",
  "Topic :: Software Development :: Libraries :: Python Modules",
]




def read(rnames):
    setupdir =  os.path.dirname( os.path.abspath(__file__))
    return open(
        os.path.join(setupdir, *rnames)
    ).read()

README =read((os.path.dirname(__file__),'README.rst'))
CHANGELOG  = read((os.path.dirname(__file__), 'docs', 'HISTORY.txt'))

long_description = '\n'.join([README,
                              CHANGELOG])+'\n'

setup(
  name='collective.generic.skel',
  version=version,
  description=("PasteScript templates for collective.generic suite by Makina Corpus"),
  long_description=long_description,
  classifiers=classifiers,
  keywords='paste templates',
  author='Mathieu Pasquet / Jean-Philippe Camguilhem',
  author_email='kiorky@cryptelium.net, jpc@makina-corpus.com',
  url='http://makina-corpus.com',
  license='GPL',
  packages=find_packages('src'),
  package_dir = {'': 'src'},
  namespace_packages=['collective',
                      'collective.generic',
                      'collective.generic.skel',
                      'collective.generic.skel.buildout',
                      'collective.generic.skel.addon',
                      'collective.generic.skel.testing',
                     ],
  include_package_data=True,
  install_requires=['setuptools',
                    'PasteScript',
                    'Cheetah',],
  entry_points="""
  # -*- Entry points: -*-
  [paste.paster_create_template]
  genericskel.buildout.pyramid = collective.generic.skel.buildout.pyramid.Template
  genericskel.buildout.django = collective.generic.skel.buildout.django.Template
  genericskel.buildout.plone25 = collective.generic.skel.buildout.plone25.Template
  genericskel.buildout.plone3 = collective.generic.skel.buildout.plone3.Template
  genericskel.buildout.plone4 = collective.generic.skel.buildout.plone4.Template
  genericskel.buildout.plone41 = collective.generic.skel.buildout.plone41.Template
  genericskel.buildout.plone42 = collective.generic.skel.buildout.plone42.Template
  genericskel.buildout.plone43 = collective.generic.skel.buildout.plone43.Template
  genericskel.pyramid = collective.generic.skel.pyramid.package:PyramidPackage
  genericskel.plone_addon  = collective.generic.skel.addon.package:PAddon
  genericskel.egg  = collective.generic.skel.common.package:Package
  genericskel.testing    = collective.generic.skel.testing.package:Package
  """
)
# vim: set ts=4 sts=4 et :
