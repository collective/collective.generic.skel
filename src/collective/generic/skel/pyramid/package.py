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

    def post(self, command, output_dir, vars):
        c.PyramidPackage.post(self, command, output_dir, vars)
        os.path.join(
            self.output_dir,
            '%s%s%s.%s' % (vars['namespace'],
                           vars['ndot'],
                           vars['nested_namespace'],
                           vars['project_name']),
            'src',
            vars['namespace'],
            vars['nested_namespace'],
            vars['project_name'],
        )
