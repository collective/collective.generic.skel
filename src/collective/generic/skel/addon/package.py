import copy
import os
from paste.script.templates import var as pvar
from collective.generic.skel.skin import package as c
from collective.generic.skel.policy import package as d

vars = c.P41Package.vars[:]
for v in d.P41Package.vars[:]:
    if not v in vars: vars.append(v)

class PAddon(c.P41Package, d.P41Package):
    """Package template"""
    summary = "A Generic Plone Addon product"
    vars = vars

    def pre(self, command, output_dir, vars):
        ret = c.P41Package.pre(self, command, output_dir, vars)
        self.p4_command = copy.deepcopy(command)
        self.p4_output_dir = copy.deepcopy(output_dir)
        self.p4_vars = copy.deepcopy(vars)
        self.p4.pre(self.p4_command, self.p4_output_dir, self.p4_vars)
        vars['dot'] = '.'
        vars['p4_versions'] = self.p4_vars['plone_versions']
        vars['p42_versions'] = vars['plone_versions']
        return ret

    def __init__(self, *args, **kwargs):
        c.P41Package.__init__(self, *args, **kwargs)
        self.p4 = c.P4Package(*args, **kwargs)






