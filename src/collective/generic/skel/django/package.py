import os
from collective.generic.skel.buildout import django
from collective.generic.skel.common import package as c


borrowed_vars = []
c.borrow_vars(borrowed_vars, django.Package)


class Package(c.Package):
    """Package template"""
    summary = "A Generic Django portal"
    vars = c.Package.vars[:] + borrowed_vars[:]
    buildout_template = django.Package

    def pre(self, command, output_dir, vars):
        c.Package.pre(self, command, output_dir, vars)
        self.load_django_vars(command, output_dir, vars)

    def load_django_vars(self, command, output_dir, vars):
        vars['eggs_mappings'] = getattr(
            self.buildout_template, 'eggs_mappings')

    def post(self, command, output_dir, vars):
        c.Package.post(self, command, output_dir, vars)
