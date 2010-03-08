from collective.generic.skel.policy import package as c
PROJECT_NAME = "skin"

class P3Package(c.P3Package):
    """Package template"""
    project = PROJECT_NAME
    summary = "A Generic Plone3 portal skin"

class P4Package(c.P4Package):
    """Package template"""
    project = PROJECT_NAME
    summary = "A Generic Plone4 portal skin"
