import copy
import sys
import os
import re

from paste.script.templates import var
from paste.script.templates import Template

from collective.generic.skel.buildout import (
    common,
    plone,
    django,
    pyramid,
)


boolify = common.boolify
running_user = common.running_user
re_flags = common.re_flags

SHARP_LINE = common.SHARP_LINE
REGENERATE_OBJECTS = common.REGENERATE_OBJECTS
REGENERATE_FILE = common.REGENERATE_FILE
REGENERATE_MSG = common.REGENERATE_MSG


class Package(common.Package):
    """
    Package template to do a double namespace egg.
    Althout it prentends to do that, it is a base for sub templates
    that need to have all sort
    of variables defined. That's why there is some curious plone bits there.
    """
    summary = "OVERRIDE ME"
    egg_plugins = ['PasteScript']
    buildout_template = None
    vars = common.metadata_vars[:] + []

    def read_vars(self, command=None):
        vars = super(Package, self).read_vars(command)
        for i, var in enumerate(vars[:]):
            if var.name == 'plone_version':
                plone_v = getattr(self, 'plone_version', None)
                if plone_v:
                    vars[i].default = plone_v
            if (
                var.name == 'description'
                and '%s' in vars[i].default and command
            ):
                vars[i].default = vars[i].default % command.args[0]
        # this allow to fix the egg-info bug
        # As we are using namespaces constructed, and args[0]
        # was maybe not yet ready
        # by default paster will fail to resolve the distrbition name.
        from paste.script import pluginlib
        if not 'old_egg_info_dir' in dir(pluginlib):
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
                ret = None
                try:
                    ret = pluginlib.old_egg_info_dir(c, self.dn)
                except Exception:
                    try:
                        os.makedirs(os.path.join(
                            c,
                            "src",
                            "%s.egg-info" % self.dn
                        ))
                    except Exception:
                        pass
                    try:
                        ret = pluginlib.old_egg_info_dir(c, self.dn)
                    except Exception:
                        raise
                return ret
            pluginlib.egg_info_dir = wrap_egg_info_dir
        return vars

    def load_xml_vars(self, command, output_dir, vars):
        if getattr(self, 'buildout_template', None) is None:
            return
        eggs_mappings = getattr(self.buildout_template, 'eggs_mappings', {})
        zcml_mappings = getattr(self.buildout_template, 'zcml_mappings', {})
        zcml_loading_order = getattr(self.buildout_template,
                                     'zcml_loading_order', {})
        qi_mappings = getattr(self.buildout_template, 'qi_mappings', {})
        qi_hidden_mappings = getattr(self.buildout_template,
                                     'qi_hidden_mappings', {})
        gs_mappings = getattr(self.buildout_template, 'gs_mappings', {})
        z2products = getattr(self.buildout_template, 'z2products', {})
        z2packages = getattr(self.buildout_template, 'z2packages', {})

        vars['python_eggs'] = []
        vars['python_eggs_mapping'] = {}
        for var in eggs_mappings:
            if vars.get(var, None):
                for e in eggs_mappings[var]:
                    if not e in vars['python_eggs']:
                        vars['python_eggs'].append(e)
                        if not var in vars['python_eggs_mapping']:
                            vars['python_eggs_mapping'][var] = []
                        vars['python_eggs_mapping'][var].append(e)
        if self.buildout_template == pyramid.Package:
            for e in pyramid.base_pyramid_eggs:
                if not e in vars['python_eggs']:
                    vars['python_eggs'].append(e)
                    if not var in vars['python_eggs_mapping']:
                        vars['python_eggs_mapping'][var] = []
                    vars['python_eggs_mapping'][var].append(e)

        vars['products'], vars['tested_products'] = [], []
        # quick install / appconfig
        if not "qi" in vars:
            vars["qi"] = {}
        for key in qi_mappings:
            if vars.get(key, False):
                if not key in vars["qi"]:
                    vars["qi"][key] = []
                #aikey = key.replace('ploneproduct',
                #                    'autoinstall_ploneproduct')
                if True:  # vars.get(aikey, False):
                    vars["qi"][key].extend(
                        [i['name'] for i in qi_mappings[key]])
                else:
                    vars["qi"][key].extend(
                        ["     #'%s'," % i['name'] for i in qi_mappings[key]]
                    )
        # quick install / appconfig
        if not "hqi" in vars:
            vars["hqi"] = {}
        for key in qi_hidden_mappings:
            if vars.get(key, False):
                if not key in vars["hqi"]:
                    vars["hqi"][key] = []
                #aikey = key.replace('ploneproduct',
                #                    'autoinstall_ploneproduct')
                if True:  # vars.get(aikey, False):
                    vars["hqi"][key].extend(qi_hidden_mappings[key])
                else:
                    vars["hqi"][key].extend(
                        ["     #'%s'," % i for i in qi_hidden_mappings[key]]
                    )

        # Zope2 new zope products
        if not "z2packages" in vars:
            vars["z2packages"] = {}
        for key in z2packages:
            if vars.get(key, False):
                if not key in vars["z2packages"]:
                    vars["z2packages"][key] = []
                #aikey = key.replace('ploneproduct',
                #                    'autoinstall_ploneproduct')
                if True:  # vars.get(aikey, False):
                    vars["z2packages"][key].extend(z2packages[key])
                else:
                    vars["z2packages"][key].extend(
                        ["#%s" % i for i in z2packages[key]]
                    )

        # Zope2 old school products
        if not "z2products" in vars:
            vars["z2products"] = {}
        for key in z2products:
            if vars.get(key, False):
                if not key in vars["z2products"]:
                    vars["z2products"][key] = []
                # a zope2 product must not have its namespace
                # in the ztc.installProduct call
                if True:  # vars.get(aikey, False):
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
        if not "zcml" in vars:
            vars["zcml"] = []
        seen = []
        for key in zcml_mappings:
            if vars.get(key, False):
                if True:  # vars.get(aikey, False):
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
        gsk.sort(lambda x, y: x[2] - y[2])
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
            for w in vars["z2packages"][v]:
                if not w in imported_modules:
                    if not v in vars['py_modules']:
                        vars['py_modules'][v] = []
                    vars['py_modules'][v].append(w)
                    if not w in vars['py_modules'][v]:
                        imported_modules.append(w)

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

    def pre(self, command, output_dir, vars):
        super(Package, self).pre(command, output_dir, vars)
        self.output_dir = os.path.join(command.options.output_dir)
        self.load_xml_vars(command, output_dir, vars)

    def post(self, command, output_dir, vars):
        super(Package, self).post(command, output_dir, vars)
        isolated_init = os.path.join(output_dir, 'src', '__init__.py')
        isolated_init2 = os.path.join(
            output_dir,
            '%s%s%s%s%s' % (
                vars['namespace'],
                vars['ndot'],
                vars['nested_namespace'],
                vars['nsdot'],
                vars['project_name'],
            ),
            'src', '__init__.py'
        )
        for i in [isolated_init2, isolated_init]:
            if os.path.exists(i) and (
                not bool(vars['namespace'])
                or not bool(vars['nested_namespace'])
            ):
                os.remove(i)

borrowed_vars = [re.compile('with_ploneproduct.*'),
                 re.compile('with_binding.*'),
                 re.compile('with_egg.*'),
                 re.compile('address'),
                 re.compile('http_port'),
                 re.compile('uri'),
                 re.compile('scm_type'),
                 re.compile('opt_deps'),
                 re.compile('inside_minitage'),
                 re.compile('smtp.*'),
                 re.compile('with_database.*')]
excluded_vars = []


def borrow_vars(vars, template):
    for cvar in template.vars:
        found = False
        bv = borrowed_vars[:]
        for sre in bv:
            if sre.match(cvar.name) and not found:
                found = True
                vars.append(cvar)
