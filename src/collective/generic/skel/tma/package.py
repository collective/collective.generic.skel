from collective.generic.skel.policy import package as c

PROJECT_NAME = "tma"

class P3Package(c.P3Package):
    """Package template"""
    project = PROJECT_NAME
    summary = "A Generic Plone3 portal tma policy" 

class P4Package(c.P4Package):
    """Package template"""
    project = PROJECT_NAME
    summary = "A Generic Plone4 portal tma policy" 
