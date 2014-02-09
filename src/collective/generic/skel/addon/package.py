import copy
import os
import shutil

from collective.generic.skel.buildout import common, plone
from collective.generic.skel.common import package as c
import glob

var = common.var
remove_path = common.remove_path

p4_themes = {
    'sunburst': 'Sunburst Theme',
    'classic': 'Plone Classic Theme',
}


borrowed_vars = []
c.borrow_vars(borrowed_vars, plone.Package)
diazo_skins = ['bootstrap', '960']


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


class Package(c.Package):
    themes = p4_themes
    plone_version = None
    buildout_template = plone
    vars = c.Package.vars[:] + borrowed_vars[:] + [
        var('with_generic', 'with_generic', default='n',),
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
        var('pthemename', 'diazo theme name', default=''),
        var('diazo_skin',
            'one of: {0}'.format(', '.join(diazo_skins)),
            default='bootstrap'),
        var('default_theme', 'default theme %s' % (
            tuple(p4_themes.keys()),), default='sunburst'),
    ]

    def __init__(self, *args, **kwargs):
        super(Package, self).__init__(*args, **kwargs)
        self.plone_version = self.buildout_template.Package.packaged_version
        self.plone_major = int(self.plone_version[0])

    def pre(self, command, output_dir, vars):
        super(Package, self).pre(command, output_dir, vars)
        vars['plone_version'] = self.plone_version
        vars['major'] = self.plone_major
        self.load_xml_vars(command, output_dir, vars)
        skin_chooser(self, command, output_dir, vars)
        vars['dot'] = '.'
        if not vars['diazo_skin'] in diazo_skins:
            raise Exception('Invalid diazo skin')
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

    def post(self, command, output_dir, vars):
        super(Package, self).post(command, output_dir, vars)
        out = os.path.join(output_dir, self.dn)
        egg = os.path.join(out, 'src', self.dn.replace('.', '/'))
        if not vars['with_zope2_skins']:
            remove_path(glob.glob(egg + '/skins')[0])
        if not vars['with_policy_support']:
            remove_path(egg + '/profiles/default/mailhost.xml')
        for f in glob.glob(out + '/scripts/*') + [egg + '/rebuild_i18n.sh']:
            os.chmod(f, 0700)
        os.rename(
            egg + '/static_{0}'.format(vars['diazo_skin']),
            egg + '/static')
        for i in glob.glob(egg + '/static_*'):
            shutil.rmtree(i)

#
