import copy
import os
import shutil

from minitage.paste.projects import common
from collective.generic.skel.common import package as c
import glob

var = common.var
remove_path = common.remove_path

vars3 = [var('default_theme', 'default theme %s' % (
    tuple(c.p3_themes.keys()),), default='default'), ] + c.P3Package.vars[:]
vars4 = [var('default_theme', 'default theme %s' % (
    tuple(c.p4_themes.keys()),), default='classic'), ] + c.P4Package.vars[:]
vars41 = [var('default_theme', 'default theme %s' % (
    tuple(c.p4_themes.keys()),), default='sunburst')] + c.P41Package.vars[:]
vars42 = [var('default_theme', 'default theme %s' % (
    tuple(c.p4_themes.keys()),), default='sunburst')] + c.P42Package.vars[:]
vars43 = [var('default_theme', 'default theme %s' % (
    tuple(c.p4_themes.keys()),), default='sunburst')] + c.P43Package.vars[:]
#vars44 = [var('default_theme', 'default theme %s' % (
#    tuple(c.p4_themes.keys()),), default='sunburst')] + c.P44Package.vars[:]


class P4Addon(c.P4Package):
    vars = vars4


class P41Addon(c.P4Package):
    vars = vars41


class P42Addon(c.P4Package):
    vars = vars42


class P43Addon(c.P4Package):
    vars = vars43


#class P44Addon(c.P4Package):
#    vars = vars44


class PAddon(c.P43Package):
    """Package template"""
    summary = "A Generic Plone Addon product"
    vars = vars43 + [
        var('with_zope2_skins', 'install zope2 skin directory', default='n'),
        var('with_policy_support',
            'install this product as a plone policy',
            default='n'),
        var('smtp_host',
            'SMTP host if you are creating a policy addon',
            default='localhost'),
        var('smtp_port',
            'SMTP port if you are creating a policy addon',
            default='25'),
        var('pthemename', 'ploneapptheming theme name', default=''),
    ]

    def post(self, command, output_dir, vars):
        c.P42Package.post(self, command, output_dir, vars)
        out = os.path.join(output_dir, self.dn)
        egg = os.path.join(out, 'src', self.dn.replace('.', '/'))
        if not vars['with_zope2_skins']:
            remove_path(glob.glob(egg + '/skins')[0])
        if not vars['with_policy_support']:
            remove_path(egg + '/profiles/default/mailhost.xml')
        if not vars['with_ploneproduct_patheming']:
            remove_path(egg + '/diazo_theme')
        for f in glob.glob(out + '/scripts/*') + [egg + '/rebuild_i18n.sh']:
            os.chmod(f, 0700)

    def pre(self, command, output_dir, vars):
        op4_command = copy.deepcopy(command)
        op4_output_dir = copy.deepcopy(output_dir)

        op4_vars = copy.deepcopy(vars)
        skin_chooser(self, command, output_dir, vars)
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
            vars['p%s_versions' % packagever] = p4_vars['plone_versions']
        vars['dot'] = '.'
        if not vars['with_policy_support']:
            vars['policy_tag'] = '<!--'
            vars['policy_end'] = '-->'
            vars['default_skin_slug'] = ''
        else:
            vars['default_skin_slug'] = 'default_skin="%s"' % vars['pdn']
            vars['with_zope2_skins'] = True
            vars['policy_tag'] = ''
            vars['policy_end'] = ''
        if not vars['with_zope2_skins']:
            vars['skins_comment_tag'] = '%s' % (
                '<!-- activate this statement '
                'to include a zope2 skin directory'
            )
            vars['skins_comment_end'] = '-->'
        else:
            vars['skins_comment_tag'] = ''
            vars['skins_comment_end'] = ''
        if not vars['pthemename']:
            vars['pthemename'] = vars['pdn']
        return ret

    def __init__(self, *args, **kwargs):
        c.PlonePackage.__init__(self, *args, **kwargs)
        self.packages = {
            '4':  P4Addon(*args, **kwargs),
            '41': P41Addon(*args, **kwargs),
            '42': P42Addon(*args, **kwargs),
            '43': P43Addon(*args, **kwargs),
            #'44': P44Addon(*args, **kwargs),
        }


def skin_chooser(self, command, output_dir, vars):
    s = vars.get('default_theme').lower().strip()
    if not s in self.themes:
        s = 'classic'
    vars['plone_theme'] = s
    vars['first_layer'] = 'custom'
    vars['plone_skin'] = self.themes[s]
    if 'with_ploneproduct_cynin' in vars:
        if vars['with_ploneproduct_cynin']:
            vars['plone_skin'] = 'cynin'
            vars['first_layer'] = 'icons'
