import os
from collective.generic.skel.common import package as c
from collective.generic.skel.buildout import pyramid

borrowed_vars = []
c.borrow_vars(borrowed_vars, pyramid.Package)


class Package(c.Package):
    """Package template"""
    summary = "A Generic Pyramid portal"
    vars = c.Package.vars[:] + borrowed_vars[:]
    buildout_template = pyramid.Package
