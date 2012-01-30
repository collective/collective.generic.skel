import copy
import os
from paste.script.templates import var as pvar
from collective.generic.skel.common import package as c
from paste.script.templates import var
from collective.generic.skel.skin import package as skin
import glob
import shutil

from minitage.core.common import remove_path

vars4  = c.P4Package.vars[:]
vars41 = c.P41Package.vars[:]
vars42 = c.P42Package.vars[:]

for cvars, pv in ((vars4,  skin.P4Package.vars[:]),
                  (vars41, skin.P41Package.vars[:]),
                  (vars42, skin.P42Package.vars[:])):
    for v in pv:
        if not v in cvars:
            cvars.append(v)

class P4Addon(c.P4Package):
    vars = vars4

class P41Addon(c.P4Package):
   vars = vars41

class P42Addon(c.P4Package):
    vars = vars42

class PAddon(c.P42Package):
    """Package template"""
    summary = "A Generic Plone Addon product"
    vars = vars42 + [
        var('with_zope2_skins', 'install zope2 skin directory', default = 'n'),
        var('with_policy_support', 'install this product as a plone policy', default = 'n'),
        pvar('smtp_host', 'SMTP host if you are creating a policy addon', default='localhost'),
        pvar('smtp_port', 'SMTP port if you are creating a policy addon', default='25'),
    ]

    def post(self, command, output_dir, vars):
        c.P42Package.post(self, command, output_dir, vars)
        out = os.path.join(output_dir, self.dn)
        egg = os.path.join(out, 'src', self.dn.replace('.', '/'))
        if not vars['with_zope2_skins']:
            remove_path(glob.glob(egg+'/skins')[0])
        if not vars['with_policy_support']:
            remove_path(egg+'/profiles/default/mailhost.xml')
        for f in glob.glob(out+'/scripts/*') + [egg+'/rebuild_i18n.sh']:
            os.chmod(f, 0700)

    def pre(self, command, output_dir, vars):
        op4_command = copy.deepcopy(command)
        op4_output_dir = copy.deepcopy(output_dir)
        op4_vars = copy.deepcopy(vars)
        skin.skin_chooser(self, command, output_dir, vars)
        ret = c.PlonePackage.pre(self, command, output_dir, vars)

        for packagever in self.packages:
            package = self.packages[packagever]
            p4_command = copy.deepcopy(op4_command)
            p4_output_dir = copy.deepcopy(op4_output_dir)
            p4_vars = copy.deepcopy(op4_vars)
            p4_vars = package.check_vars(p4_vars, p4_command)
            p4_vars['booleans'] = p4_vars.get('booleans', [])
            p4_vars['booleans'].extend(
                [a
                 for a in p4_vars
                 if (a.startswith('with_') and not a in p4_vars['booleans'])]
            )
            package.boolify(p4_vars, p4_vars['booleans'])
            package.pre(p4_command, p4_output_dir, p4_vars)
            vars['p%s_versions'%packagever] = p4_vars['plone_versions']
        vars['dot'] = '.'
        if not vars['with_zope2_skins']:
            vars['skins_comment_tag'] = '%s' % (
                '<!-- activate this statement '
                'to include a zope2 skin directory'
            )
            vars['skins_comment_end'] = '-->'
        else:
            vars['skins_comment_tag'] = ''
            vars['skins_comment_end'] = ''
        if not vars['with_policy_support']:
            vars['policy_tag']='<!--'
            vars['policy_end']='-->'
            vars['default_skin_slug']=''
        else:
            vars['default_skin_slug']='default_skin="%s"' % vars['pdn']
            vars['policy_tag']=''
            vars['policy_end']=''
        return ret

    def __init__(self, *args, **kwargs):
        c.PlonePackage.__init__(self, *args, **kwargs)
        self.packages = {
            '4':  P4Addon(*args, **kwargs),
            '41': P41Addon(*args, **kwargs),
            '42': P42Addon(*args, **kwargs),
        }

