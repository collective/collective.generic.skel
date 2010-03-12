import os
import sys
import re

from collective.generic.skel.common.package import Package as Template
from paste.script.templates import var as pvar

vars = []
class Package(Template):
    """Package template"""
    summary = "A Generic testing infrastructure."
    project = 'testing'
    vars = Template.vars + vars +\
    [pvar('test_layer', 'Use a test layer (availables: Django', default='')]

