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

README =read((os.path.dirname(__file__),'README.txt'))
CHANGELOG  = read((os.path.dirname(__file__), 'docs', 'HISTORY.txt'))

long_description = '\n'.join([README,
                              CHANGELOG])+'\n' 

setup(
  name='collective.generic.skel',
  version=version,
  description=("PasteScript templates for collective.generic suite sponsorised by Makina Corpus"),
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
                      'collective.generic.skel.policy',
                      'collective.generic.skel.tma',
                      'collective.generic.skel.skin',
                      'collective.generic.skel.testing',
                     ],
  include_package_data=True,
  install_requires=['setuptools',
                    'PasteScript',
                    'Cheetah',
                    'minitage.paste',],
  entry_points="""
  # -*- Entry points: -*-
  [paste.paster_create_template]
  collective.generic.plone3_policy = collective.generic.skel.policy.package:P3Package
  collective.generic.plone4_policy = collective.generic.skel.policy.package:P4Package
  collective.generic.plone3_skin  = collective.generic.skel.skin.package:P3Package
  collective.generic.plone4_skin  = collective.generic.skel.skin.package:P4Package
  collective.generic.plone3_tma  = collective.generic.skel.tma.package:P3Package
  collective.generic.plone4_tma  = collective.generic.skel.tma.package:P4Package
  collective.generic.egg  = collective.generic.skel.common.package:Package
  collective.generic.testing    = collective.generic.skel.testing.package:Package
  """
)
# vim: set ts=4 sts=4 et :
