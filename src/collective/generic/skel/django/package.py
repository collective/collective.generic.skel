import os
import sys
from collective.generic.skel.common  import package as c
from paste.script.templates import var

class DjangoPackage(c.DjangoPackage):
    """Package template"""
    summary = "A Generic Django portal"
    vars = c.DjangoPackage.vars

    def post(self, command, output_dir, vars):
        c.DjangoPackage.post(self, command, output_dir, vars)
        otp = os.path.join(
            self.output_dir,
            '%s%s%s.%s' % (vars['namespace'], vars['ndot'], vars['nested_namespace'], vars['project_name']),
            'src',
            vars['namespace'],
            vars['nested_namespace'],
            vars['project_name'],
        )

