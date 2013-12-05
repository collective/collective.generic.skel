import os

from setuptools import setup, find_packages
version = '0.1.0'
classifiers = [
    "Programming Language :: Python",
    "Framework :: Paste",
    "Framework :: Plone",
    "Topic :: Software Development :: Libraries :: Python Modules",
]


name = 'collective.generic.skel'
slug = 'genericskel'
EP = {
    'paste.paster_create_template': [
        '{0}.buildout.pyramid = {1}.buildout.pyramid:Package'.format(
             slug, name),
        '{0}.buildout.django  = {1}.buildout.django:Package'.format(
             slug, name),
        '{0}.buildout.plone   = {1}.buildout.plone:Package'.format(
             slug, name),
        '{0}.pyramid          = {1}.pyramid.package:Package'.format(
             slug, name),
        '{0}.plone_addon      = {1}.addon.package:Package'.format(
             slug, name),
        '{0}.egg              = {1}.common.package:Package'.format(
             slug, name),
        '{0}.testing          = {1}.testing.package:Package'.format(
            slug, name),
    ]}


def read(rnames):
    setupdir = os.path.dirname(os.path.abspath(__file__))
    return open(
        os.path.join(setupdir, *rnames)
    ).read()

README = read((os.path.dirname(__file__), 'README.rst'))
CHANGELOG = read((os.path.dirname(__file__), 'docs', 'HISTORY.txt'))

long_description = '\n'.join([README, CHANGELOG]) + '\n'

setup(
    name=name,
    version=version,
    description=("PasteScript templates for "
                 "collective.generic suite by Makina Corpus"),
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
                        'collective.generic.skel.testing'],
    include_package_data=True,
    install_requires=['setuptools',
                      'PasteScript',
                      'Cheetah'],
    entry_points = EP,
)
# vim: set ts=4 sts=4 et :
