import os
import sys
import re
from collective.generic.skel.common.package import Package as Template
from collective.generic.skel.common.package import plone_vars
from paste.script.templates import var as pvar

from minitage.paste.projects.plone3 import Template as Plone3Template
from minitage.paste.projects.plone4 import Template as Plone4Template


borrowed_vars = [re.compile('with_ploneproduct.*'),
                 re.compile('with_binding_ldap')]

excluded_vars = []
p3_vars = []
p4_vars = []
items = ((p3_vars, Plone3Template),
         (p4_vars, Plone4Template),)

for vars, template in items:
    for var in template.vars:
        found = False
        for sre in borrowed_vars:
            if sre.match(var.name) and not found:
                found = True
                vars.append(var)
                if var.name.startswith('with_ploneproduct'):
                    vars.append(
                        pvar(
                            var.name.replace(
                                'ploneproduct',
                                'autoinstall_ploneproduct'
                            ),
                            description = var.description,
                            default = 'y'
                        )
                    )
                    break

policy_vars = [\
             pvar('smtp_host', 'SMTP host', default='localhost'),
             pvar('smtp_port', 'SMTP port', default='25'),
              ]
class P3Package(Template):
    """Package template"""
    project = 'policy'
    plone_version = '3'
    summary = "A Generic Plone %s portal policy" % plone_version
    vars = Template.vars + plone_vars + p3_vars + policy_vars


    def post(self, command, output_dir, vars):
        Template.post(self, command, output_dir, vars)
        path = os.path.join(
            output_dir,
            self.dn,
            'src',
            vars['namespace'],
            vars['nested_namespace'],
            vars['project_name'], 'tests', 'ldap.txt'
        )
        # removing package.policy/package/policy/tests/ldap.txt if not needed
        if not vars['with_ploneproduct_ldap'] and os.path.exists(path):
            if not command.options.quiet:
                print "     * cleaning policy/tests/ldap.txt"
            os.remove(path)


class P4Package(P3Package):
    """Package template"""
    vars = Template.vars + plone_vars + p4_vars
    plone_version = '4'
    summary = "A Generic Plone %s portal policy" % plone_version



