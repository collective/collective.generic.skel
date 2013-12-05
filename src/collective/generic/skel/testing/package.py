
from collective.generic.skel.common.package import Package
from paste.script.templates import var as pvar

vars = []


class Package(Package):
    """Package template"""
    summary = "A Generic testing infrastructure."
    project = 'testing'
    vars = Package.vars + vars + [
        pvar('test_layer', 'Use a test layer (availables: Django', default='')]
