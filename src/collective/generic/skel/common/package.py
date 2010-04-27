import sys
import os
import re

from paste.script.templates import var
from paste.script.templates import Template

from minitage.paste.common import boolify
from minitage.paste.projects.plone3 import common
running_user = common.running_user
reflags = common.reflags


REGENERATE_MSG = """
Lot of files generated by the collective.generic packages  will try to load user defined objects in user specific files.
The final goal is to regenerate easyly the test infrastructure on templates updates without impacting
user-specific test boilerplate.
We do not use paster local commands (insert/update) as it cannot determine witch is specific or not and we prefer to totally
separe generated stuff and what is user specific
"""
REGENERATE_FILE = """
If you need to edit something in this file, you must have better to do it in:
"""

SHARP_LINE = '#' * 80

REGENERATE_OBJECTS = """
Objects that you can edit and get things overidden are:
"""
class Package(Template):
    """
    Package template to do a double namespace egg.
    Althout it prentends to do that, it is a base for sub templates that need to have all sort
    of variables defined. That's why there is some curious plone bits there.
    """
    _template_dir = 'tmpl'
    summary = "A Generic double namespaced egg."
    egg_plugins = ['PasteScript',]
    use_cheetah = True
    vars = [
        var('namespace', 'Namespace', default='%(namespace)s'),
        var('nested_namespace', 'Nested Namespace', default='%(package)s'),
        var('version', 'Version', default='1.0'),
        var('author', 'Author', default = running_user,),
        var('author_email', 'Email', default = '%s@%s' % (running_user, 'localhost')),
        var('url', 'URL of homepage', default=''),
        var('description', 'One-line description of the package', default='Project %s'),
        var('keywords', 'Space-separated keywords/tags'),
        var('license_name', 'License name', default='GPL'),
        var('project_name', 'Project namespace name (to override the first given project name forced by some derivated templates, left empty in doubt)', default=''),
    ]

    def run(self, command, output_dir, vars):
        self.boolify(vars)
        self.pre(command, output_dir, vars)
        # may we have register variables ?
        if self.output_dir:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            output_dir = self.output_dir
        if not os.path.isdir(output_dir):
            raise Exception('%s is not a directory' % output_dir)
        self.write_files(command, self.output_dir, vars)
        self.post(command, output_dir, vars)
        if not command.options.quiet:
            print "-" * 79
            print "The template has been generated in %s" % self.output_dir
            print "-" * 79

    def boolify(self, d, keys=None):
        return boolify(d, keys)

    def read_vars(self, command=None):
        vars = Template.read_vars(self, command)
        infos = {}
        project = ''
        if command:
            project = command.args[0]
        if '.' in project:
            try:
                infos['namespace'], infos['nested_namespace'], infos['project'] = project.split('.')
                if getattr(self, 'project', None):
                    infos['project'] = self.project
            except:
                try:
                    # user may try to only give namespace/project as he is doing a template with a predefined project.
                    infos['nested_namespace'], infos['project'] = project.split('.')
                    infos['namespace'] = ''
                except:
                    print "Your project name must either in the form \"project\" or \"namespace.package.project\""
                    print "Invalid name: '%s'." % project
                    sys.exit(255)
            self.project = infos['project']
        else:
            infos['namespace'] = ''
            infos['nested_namespace'] = project
            infos['project'] = 'core'
            self.project = getattr(self, 'project', infos['project'])
        ndot = '.'
        if not infos['namespace']:
            ndot = ''


        self.dn = '%s%s%s.%s' % (infos['namespace'], ndot,
                           infos['nested_namespace'] ,
                           self.project)
        for i, var in enumerate(vars[:]):
            if var.name == 'plone_version':
                plone_v = getattr(self, 'plone_version', None)
                if plone_v:
                    vars[i].default = plone_v
            if var.name == 'description' and '%s' in vars[i].default and command:
                vars[i].default = vars[i].default % command.args[0]
            for name in infos.keys():
                if var.name == name:
                    vars[i].default = infos[name]
            if var.name == 'project_name':
                vars[i].default = self.project
            if var.name == 'url':
                if '%s' in vars[i].default:
                    vars[i].default = vars[i].default % self.dn
        # this allow to fix the egg-info bug
        # As we are using namespaces constructed, and args[0] was maybe not yet ready
        # by default paster will fail to resolve the distrbition name.
        from paste.script import pluginlib
        pluginlib.old_egg_info_dir = pluginlib.egg_info_dir
        self.module = self.__class__.__module__
        def wrap_egg_info_dir(c, n):
            print "%s" % (
                "%s> Monkey patching egg_info_dir "
                "to resolve good distro name: "
                "'%s' (old was '%s')" % (
                    self.module, self.dn, n
                )
            )
            return pluginlib.old_egg_info_dir(c, self.dn)
        pluginlib.egg_info_dir = wrap_egg_info_dir
        return vars

    def pre(self, command, output_dir, vars):
        Template.pre(self, command, output_dir, vars)
        if not vars['project_name']:
            vars['project_name'] = vars['project']
        else:
            self.project = vars['project_name']
        vars['project'] = self.project
        vars['ndot'] = '.'
        vars['nunderscore'] = '_'
        if not vars['namespace']:
            vars['ndot'] = ''
            vars['nunderscore'] = ''
        vars['hr'] = SHARP_LINE
        vars['generate_msg'] = REGENERATE_MSG % vars
        vars['generate_file'] = REGENERATE_FILE % vars
        vars['generate_objects'] = REGENERATE_OBJECTS % vars
        self.dn = '%s%s%s.%s' % (
            vars['namespace'], vars['ndot'],
            vars['nested_namespace'] ,
            vars['project']
        )

        self.output_dir = os.path.join(command.options.output_dir)

    def post(self, command, output_dir, vars):
        Template.post(self, command, output_dir, vars) 
        isolated_init = os.path.join(output_dir, 'src', '__init__.py')
        if os.path.exists(isolated_init) and not bool(vars['namespace']):
            os.remove(isolated_init)

"""
PLONE RELATED STUFF
"""
from minitage.paste.projects import plone3
from minitage.paste.projects import plone4

borrowed_vars = [re.compile('with_ploneproduct.*'),
                 re.compile('with_binding_ldap')]

plone_vars = Package.vars + [ ] 
excluded_vars = []
p3_vars = []
p4_vars = []
items = ((p3_vars, plone3.Template),
         (p4_vars, plone4.Template),)

for vars, template in items:
    for cvar in template.vars:
        found = False
        for sre in borrowed_vars:
            if sre.match(cvar.name) and not found:
                found = True
                vars.append(cvar)
                if cvar.name.startswith('with_ploneproduct'):
                    vars.append(
                        var(
                            cvar.name.replace(
                                'ploneproduct',
                                'autoinstall_ploneproduct'
                            ),
                            description = cvar.description,
                            default = 'y'
                        )
                    )
                    break 


class P3Package(Package):
    plone_version = None
    plone_template = plone3.Template
    vars = plone_vars + p3_vars

    def __init__(self, *args, **kwargs):
        Template.__init__(self, *args, **kwargs)
        self.plone_version = self.plone_template.packaged_version
        self.plone_major = int(self.plone_version[0])

    def pre(self, command, output_dir, vars):
        Package.pre(self, command, output_dir, vars)
        vars['plone_version'] = self.plone_version
        vars['major'] = self.plone_major
        self.load_plone_vars(command, output_dir, vars)
        if not 'with_ploneproduct_fss' in vars:
            vars['with_ploneproduct_fss'] = False

    def load_plone_vars(self, command, output_dir, vars):
        eggs_mappings = getattr(self.plone_template, 'eggs_mappings')
        zcml_mappings = getattr(self.plone_template, 'zcml_mappings')
        zcml_loading_order = getattr(self.plone_template, 'zcml_loading_order')
        qi_mappings = getattr(self.plone_template, 'qi_mappings')
        qi_hidden_mappings = getattr(self.plone_template, 'qi_hidden_mappings')
        gs_mappings = getattr(self.plone_template, 'gs_mappings')
        z2products = getattr(self.plone_template, 'z2products')
        z2packages = getattr(self.plone_template, 'z2packages')
        
        vars['products'], vars['tested_products'] = [], []
        # quick install / appconfig
        if not "qi" in vars: vars["qi"] = {}
        for key in qi_mappings:
            if vars.get(key, False):
                if not key in vars["qi"]:
                    vars["qi"][key] = []
                aikey = key.replace('ploneproduct', 
                                    'autoinstall_ploneproduct')
                if vars.get(aikey, False):
                    vars["qi"][key].extend(qi_mappings[key])
                else:
                    vars["qi"][key].extend(
                        ["     #'%s'," % i for i in qi_mappings[key]]
                    )
        # quick install / appconfig
        if not "hqi" in vars: vars["hqi"] = {}
        for key in qi_hidden_mappings:
            if vars.get(key, False):
                if not key in vars["hqi"]:
                    vars["hqi"][key] = []
                aikey = key.replace('ploneproduct', 
                                    'autoinstall_ploneproduct')
                if vars.get(aikey, False):
                    vars["hqi"][key].extend(qi_hidden_mappings[key])
                else:
                    vars["hqi"][key].extend(
                        ["     #'%s'," % i for i in qi_hidden_mappings[key]]
                    )

       # Zope2 new zope products
        if not "z2packages" in vars: vars["z2packages"] = {}
        for key in z2packages:
            if vars.get(key, False):
                if not key in vars["z2packages"]:
                    vars["z2packages"][key] = []
                aikey = key.replace('ploneproduct', 
                                    'autoinstall_ploneproduct')
                if vars.get(aikey, False):
                    vars["z2packages"][key].extend(z2packages[key])
                else:
                    vars["z2packages"][key].extend(
                        ["#%s" % i for i in z2packages[key]]
                    )

        # Zope2 old school products
        if not "z2products" in vars: vars["z2products"] = {}
        for key in z2products:
            if vars.get(key, False):
                if not key in vars["z2products"]:
                    vars["z2products"][key] = []
                aikey = key.replace('ploneproduct', 'autoinstall_ploneproduct')
                # a zope2 product must not have its namespace 
                # in the ztc.installProduct call
                if vars.get(aikey, False):
                    vars["z2products"][key].extend([i.replace('Products.', '')
                                                    for i in z2products[key]])
                else:
                    vars["z2products"][key].extend(
                        ["#%s" % i.replace('Products.', '')
                         for i in z2products[key]]
                    )

        def zcmlsort(obja, objb):
            apackage = re.sub('^#', '', obja[0]).strip()
            bpackage = re.sub('^#', '', objb[0]).strip()
            aslug = obja[1].strip()
            bslug = objb[1].strip()
            aorder = zcml_loading_order.get((apackage, aslug), 50000)
            border = zcml_loading_order.get((bpackage, bslug), 50000)
            return aorder - border

        # Zope2 old school products
        if not "zcml" in vars: vars["zcml"] = []
        seen = []
        for key in zcml_mappings:
            if vars.get(key, False):
                aikey = key.replace('ploneproduct', 'autoinstall_ploneproduct')
                if vars.get(aikey, False):
                    for i in zcml_mappings[key]:
                        if not i in seen:
                            vars["zcml"].append(i)
                            seen.append(i)
                else:
                    for i in zcml_mappings[key]:
                        if not i in seen:
                            vars["zcml"].append(("#%s" % i[0], i[1]))
                            seen.append(i)

        # generic setup
        vars['gs'] = []
        gsk = gs_mappings.keys()
        gsk.sort(lambda x,y: x[2] - y[2])
        for k in gsk:
            for o in gs_mappings[k]:
                if vars.get(o, False):
                    if not k in vars['gs']:
                        vars['gs'].append(k)

        vars['zcml'].sort(zcmlsort)
        # add option marker
        for option in zcml_mappings:
            for p in zcml_mappings[option]:
                packages = [p, ('#%s' % p[0], p[1])]
                for package in packages:
                    if package in vars['zcml']:
                        i = vars['zcml'].index(package)
                        vars['zcml'][i:i] = ['%s' % option]

        # gather python moduloes to import
        vars['py_modules'], imported_modules = {}, []
        for v in vars['z2packages']:
            found = False
            for w in vars["z2packages"][v]:
                if not w in imported_modules:
                    if not v in vars['py_modules']:
                        vars['py_modules'][v] = []
                    vars['py_modules'][v].append(w)
                    if not w in vars['py_modules'][v]:
                        imported_modules.append(w)

        # normallly thz zope products are needed only if they need zcml slugs.
        #for v in vars['z2packages']:
        #     found = False
        #     for w in vars["z2packages"][v]:
        #         if not w in imported_modules:
        #             if not v in vars['py_modules']:
        #                 vars['py_modules'][v] = []
        #             vars['py_modules'][v].append(w)
        #             imported_modules.append(w)

        opt = '#default'
        for v in vars['zcml']:
            if isinstance(v, basestring):
                opt = v
            if not isinstance(v, basestring):
                w = v[0]
                if not w in imported_modules:
                    if not opt in vars['py_modules']:
                        vars['py_modules'][opt] = []
                    if not w in vars['py_modules'][opt]:
                        vars['py_modules'][opt].append(w)

class P4Package(P3Package):
    plone_template = plone4.Template
    vars = plone_vars + p4_vars
 
