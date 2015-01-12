Introduction
=============

.. contents::

This package contains package into cgwb_, a web interface to generate full projects.
Goal is to have:

    - a template for a classical egg
    - a template for a plone addon (plone3, 4, etc), policy and skins are just splitted copies around the addon.
        
        - must have a zope2 product initialization method
        - must support migrations profiles
        - must have all GenericSetup steps as commented snippets
        - must have a testing layer based on plone.app.skin
        - must have CMF skin directories
        - must have a locales directory with po's and manual po's out of the box
        - must have a wrapper to i18ndude for translations
        - must have a zope3 browser layer well registered in plone
        - must have some snippets around to make quickly:
          
                - viewlets
                - portlets
                - browser views
                - dashboards

        - must have a zope3 browser resources directory
        - must have GenericSetup setup handlers wired
        - must integrate five.grok out of the box
        - must have buildouts for dev, stable and old stable plones (actually 42 41 40)

            - those buildouts contain any neccessary pins

    - a template for a plone policy (plone3, 4, etc)
    - a template for a plone skin (plone3, 4, etc)


Credits
======================================
|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact us <mailto:python@makina-corpus.org>`_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
.. _cgwb: http://pypi.python.org/pypi/collective.generic.webbuilder






