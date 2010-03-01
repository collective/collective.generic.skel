
from collective.generic.skel.common.package import plone_vars
from collective.generic.skel.common.package import Package as Template

class P3Package(Template):
    """Package template"""
    project = "tma"
    vars = Template.vars + plone_vars
    plone_version = '3'
    summary = "A Generic Plone %s portal tma policy" % plone_version

class P4Package(P3Package):
    """Package template"""
    plone_version = '4'
    summary = "A Generic Plone %s portal tma policy" % plone_version
