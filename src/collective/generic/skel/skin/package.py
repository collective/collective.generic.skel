import os
import sys
from collective.generic.skel.common  import package as c
from paste.script.templates import var
PROJECT_NAME = "skin"

p3_themes = {
    'default': 'Plone Default',
} 
p4_themes = {
    'sunburst': 'Sunburst Theme',
    'classic': 'Plone Classic Theme',
} 
skin3_vars = [var('default_theme', 'default theme %s' % (tuple(p3_themes.keys()),), default='default'),]
skin4_vars = [var('default_theme', 'default theme %s' % (tuple(p4_themes.keys()),), default='classic'),] 
skin41_vars = [var('default_theme', 'default theme %s' % (tuple(p4_themes.keys()),), default='sunburst'),] 

def skin_chooser(self, command, output_dir, vars):
    s = vars.get('default_theme').lower().strip()
    if not s in self.themes: s = 'classic'
    vars['plone_theme'] = s
    vars['first_layer'] = 'custom'
    vars['plone_skin'] = self.themes[s] 
    if 'with_ploneproduct_cynin' in vars:
        if vars['with_ploneproduct_cynin']:
            vars['plone_skin'] = 'cynin'
            vars['first_layer'] = 'icons'
 
class P3Package(c.P3Package):
    """Package template"""
    project = PROJECT_NAME
    summary = "A Generic Plone3 portal skin"
    vars = skin3_vars + c.P3Package.vars
    themes = p3_themes

    def pre(self, command, output_dir, vars):
        c.P3Package.pre(self, command, output_dir, vars)
        skin_chooser(self, command, output_dir, vars)

    def post(self, command, output_dir, vars):
        c.P3Package.post(self, command, output_dir, vars)
        otp = os.path.join(
            self.output_dir,
            '%s%s%s.%s' % (vars['namespace'], vars['ndot'], vars['nested_namespace'], vars['project_name']),
            'src',
            vars['namespace'],
            vars['nested_namespace'],
            vars['project_name'],
        )
        for f in [ff for ff in os.listdir(otp) if ff.endswith('.sh')]:
            fp = os.path.join(otp, f)
            os.chmod(fp, 0755)


class P4Package(c.P4Package):
    """Package template"""
    project = PROJECT_NAME
    summary = "A Generic Plone4 portal skin"
    vars = skin4_vars + c.P4Package.vars
    themes = p4_themes

    def pre(self, command, output_dir, vars):
        c.P4Package.pre(self, command, output_dir, vars)
        skin_chooser(self, command, output_dir, vars)

    def post(self, command, output_dir, vars):
        c.P4Package.post(self, command, output_dir, vars)
 
class P41Package(c.P41Package):
    """Package template"""
    project = PROJECT_NAME
    summary = "A Generic Plone41 portal skin"
    vars = skin41_vars + c.P41Package.vars
    themes = p4_themes

    def pre(self, command, output_dir, vars):
        c.P41Package.pre(self, command, output_dir, vars)
        skin_chooser(self, command, output_dir, vars)

    def post(self, command, output_dir, vars):
        c.P41Package.post(self, command, output_dir, vars)
 
 
