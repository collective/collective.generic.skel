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

def skin_chooser(self, command, output_dir, vars):
    s = vars.get('default_theme').lower().strip()
    if not s in self.themes: s = 'classic'
    vars['plone_theme'] = s
    vars['plone_skin'] = self.themes[s] 
 
class P3Package(c.P3Package):
    """Package template"""
    project = PROJECT_NAME
    summary = "A Generic Plone3 portal skin"
    vars = skin3_vars + c.P3Package.vars
    default_theme = 'default'
    themes = p3_themes

    def pre(self, command, output_dir, vars):
        c.P3Package.pre(self, command, output_dir, vars)
        skin_chooser(self, command, output_dir, vars)

class P4Package(c.P4Package):
    """Package template"""
    project = PROJECT_NAME
    summary = "A Generic Plone4 portal skin"
    vars = skin4_vars + c.P4Package.vars
    default_theme = 'classic'
    themes = p4_themes

    def pre(self, command, output_dir, vars):
        c.P4Package.pre(self, command, output_dir, vars)
        skin_chooser(self, command, output_dir, vars)


