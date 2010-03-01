#-*- coding: utf-8 -*-
"""
Providing site properties from profile to generics tests.
"""

import os.path
from xml.dom import minidom
from read_xml_properties import getProperties


def getSiteProperties(xml_file):
    """Get Site properties from Profile.

    >>> site_prop_file = 'xml_doctests/site_properties.xml'
    >>> properties = getSiteProperties(xml_file=site_prop_file)
    >>> for prop, value in properties.iteritems():
    ...     print '%s : %r' %(prop, value)
    email_from_address : 'testeur@makina-corpus.com'
    email_from_name : 'Site Administrator'
    description : "Your's site description"
    title : 'A Makina Plone site'
    default_page : 'front-page'
    enable_permalink : False
    validate_email : True
    selectable_views : (u'folder_listing', u'news_listing')
    email_charset : 'utf-8'

    """
    site_props = {}
    try:
        props_file = open(xml_file)
        site_properties = minidom.parse(props_file)
    finally:
        props_file.close()

    site = site_properties.documentElement
    site_props = getProperties(site)
    
    return site_props

if __name__ == "__main__":
    import doctest
    OPTIONS = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS |\
               doctest.NORMALIZE_WHITESPACE
    doctest.testmod(verbose=True, optionflags=OPTIONS)
