import os
from paste.script.templates import var as pvar
from collective.generic.skel.common import package as c

PROJECT_NAME = "policy"
policy_vars = [\
             pvar('smtp_host', 'SMTP host', default='localhost'),
             pvar('smtp_port', 'SMTP port', default='25'),
              ]

def policy_post(self, command, output_dir, vars):
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

class P3Package(c.P3Package):
    """Package template"""
    project = PROJECT_NAME
    summary = "A Generic Plone3 portal policy"
    vars = c.P3Package.vars + policy_vars

    def post(self, command, output_dir, vars):
        c.P3Package.post(self, command, output_dir, vars)
        policy_post(self, command, output_dir, vars)

class P4Package(c.P4Package):
    """Package template"""
    project = PROJECT_NAME
    summary = "A Generic Plone4 portal policy"
    vars = c.P4Package.vars + policy_vars

    def post(self, command, output_dir, vars):
        c.P4Package.post(self, command, output_dir, vars)
        policy_post(self, command, output_dir, vars) 


