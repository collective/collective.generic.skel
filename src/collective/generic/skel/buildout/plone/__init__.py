# Copyright (C) 2009, Mathieu PASQUET <kiorky@cryptelium.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the <ORGANIZATION> nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

__docformat__ = 'restructuredtext en'

import os
from glob import glob
import copy
import re

import pkg_resources

from collective.generic.skel.buildout import common


class NoDefaultTemplateError(Exception):
    pass


package_slug_re = re.compile(
    '(.*)-(meta|configure|overrides)', common.re_flags)
default_config = pkg_resources.resource_filename(
    'collective.generic.skel', 'buildout/plone/genericskel.plone.xml')
user_config = os.path.join(os.path.expanduser('~'), '.genericskel.plone.xml')
xmlvars = common.read_vars(default_config, user_config)
# plone quickinstaller option/names mappings
qi_mappings = xmlvars.get('qi_mappings', {})
qi_hidden_mappings = xmlvars.get('qi_hidden_mappings', {})
gs_mappings = xmlvars.get('gs_mappings', {})
# eggs registered as Zope2 packages
z2packages = xmlvars.get('z2packages', {})
z2products = xmlvars.get('z2products', {})
#/p variables discovered via configuration
addons_vars = xmlvars.get('addons_vars', {})
# mappings option/eggs to install
eggs_mappings = xmlvars.get('eggs_mappings', {})
# scripts to generate
scripts_mappings = xmlvars.get('scripts_mappings', {})
# mappings option/zcml to install
zcml_loading_order = xmlvars.get('zcml_loading_order', {})
zcml_mappings = xmlvars.get('zcml_mappings', {})
# mappings option/versions to pin
versions_mappings = xmlvars.get('versions_mappings', {})
# mappings option/versions to pin if the user wants really stable sets
checked_versions_mappings = xmlvars.get('checked_versions_mappings', {})
# mappings option/productdistros to install
urls_mappings = xmlvars.get('urls_mappings', {})
# mappings option/nested packages/version suffix packages  to install
plone_np_mappings = xmlvars.get('plone_np_mappings', {})
plone_vsp_mappings = xmlvars.get('plone_vsp_mappings', {})
plone_sources = xmlvars.get('plone_sources', {})
dev_desc = 'Install %s in development mode.'
dev_vars = []
sources_k = plone_sources.keys()
sources_k.sort()
for name in sources_k:
    dev_vars.append(
        common.var(
            'with_autocheckout_%s' % name,
            description=name,
            default="n",
        )
    )


class Package(common.Package):
    packaged_version = '4.3.2'
    summary = 'Template for creating a plone43 project'
    python = 'python-2.7'
    _template_dir = pkg_resources.resource_filename(
        'collective.generic.skel', 'buildout/plone/tmpl')

    # buildout <-> genericskel config vars mapping
    sections_mappings = {
        'additional_eggs': eggs_mappings,
        'plone_zcml': zcml_mappings,
        'plone_products': urls_mappings,
        'plone_np': plone_np_mappings,
        'plone_vsp': plone_vsp_mappings,
        'plone_scripts': scripts_mappings,
    }
    qi_mappings = qi_mappings
    qi_hidden_mappings = qi_hidden_mappings
    gs_mappings = gs_mappings
    z2packages = z2packages
    z2products = z2products
    addons_vars = common.get_ordered_discovered_options(addons_vars.values())
    eggs_mappings = eggs_mappings
    scripts_mappings = scripts_mappings
    zcml_loading_order = zcml_loading_order
    zcml_mappings = zcml_mappings
    versions_mappings = versions_mappings
    checked_versions_mappings = checked_versions_mappings
    urls_mappings = urls_mappings
    plone_np_mappings = plone_np_mappings
    plone_vsp_mappings = plone_vsp_mappings
    plone_sources = plone_sources

    def read_vars(self, command=None):
        if command:
            if not command.options.quiet:
                for msg in getattr(self, 'init_messages', []):
                    print msg
        vars = common.Package.read_vars(self, command)
        for i, var in enumerate(vars[:]):
            if var.name in ['deliverance_project'] and command:
                sane_name = common.SPECIALCHARS.sub('', command.args[0])
                vars[i].default = sane_name
            if var.name in ['reverseproxy_host'] and command:
                sane_name = '%s.localhost' % common.SPECIALCHARS.sub(
                    '', command.args[0])
                vars[i].default = sane_name
        return vars

    def get_sources_url(self, cvars=None):
        if not cvars:
            cvars = {}
        v = cvars.get('plone_version', self.packaged_version)
        sources = 'http://dist.plone.org/release/%s/sources.cfg' % v
        return sources

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        common.Package.pre(self, command, output_dir, vars)
        vars['mode'] = 'zeo'
        if not 'with_ploneproduct_paasync' in vars:
            vars['with_ploneproduct_paasync'] = False
        vars['plonesite'] = 'Plone'
        vars['major'] = int(vars['plone_version'][0])
        vars['sources_url'] = self.get_sources_url(vars)
        #vars['versions_url'] = self.get_versions_url(vars)
        #vars['zope2_url'] = self.get_zope2_url(vars)
        #vars['ztk_url'] = self.get_ztk_url(vars)
        if not vars.get('ztk_url', None):
            vars['ztk_url'] = False
        vars['sane_name'] = common.SPECIALCHARS.sub('', vars['project'])
        vars['category'] = 'zope'
        vars['includesdirs'] = ''
        vars['hr'] = '#' * 120
        common.Package.pre(self, command, output_dir, vars)
        vars['mode'] = vars['mode'].lower().strip()

        # transforming eggs requirements as lists
        for var in self.sections_mappings:
            if var in vars:
                vars[var] = [a.strip() for a in vars[var].split(',')]

        vars['autocheckout'] = []
        for var in vars:
            if var.startswith('with_autocheckout') and vars[var]:
                vn = var.replace('with_autocheckout_', '')
                vars['autocheckout'].append(
                    self.plone_sources[vn]['name']
                )

        for var in self.plone_sources:
            if self.plone_sources[var].get('autocheckout', '') == 'y':
                if not self.plone_sources[var]['name'] in vars['autocheckout']:
                    if (
                        (True in [vars.get(o, False)
                                  for o in self.plone_sources[var]['options']])
                        and (self.plone_sources[var]['name']
                             not in vars['autocheckout'])
                    ):
                        vars['autocheckout'].append(
                            self.plone_sources[var]['name']
                        )

        lps = copy.deepcopy(self.plone_sources)
        for item in self.plone_sources:
            col = self.plone_sources[item]
            found = False
            for option in col['options']:
                if vars.get(option, False):
                    found = True
                    break
            if not found:
                del lps[item]
        vars['plone_sources'] = lps

        # ZODB3 from egg
        if vars['major'] < 4:
            vars['additional_eggs'].append('#ZODB3 is installed as an EGG!')
            vars['additional_eggs'].append('ZODB3')

        # do we need some pinned version
        vars['plone_versions'] = []
        pin_added = []
        for var in self.versions_mappings:
            vars['plone_versions'].append(('# %s' % var, '',))
            vmap = self.versions_mappings[var]
            vmap.sort()
            for pin in vmap:
                if not pin in pin_added:
                    pin_added.append(pin)
                    vars['plone_versions'].append(pin)

        if not vars['mode'] in ['zeo']:
            raise Exception('Invalid mode (not in zeo')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for section in self.sections_mappings:
            for var in [k
                        for k in self.sections_mappings[
                            section]
                        if vars.get(k, '')]:
                # skip plone products which are already in
                # the product 's setup.py
                if vars['with_generic'] and section == 'additional_eggs':
                    pass
                if not section == 'plone_zcml':
                    vars[section].append('#%s' % var)
                for item in self.sections_mappings[section][var]:
                    if section == 'plone_zcml':
                        item = '-'.join(item)
                    if not '%s\n' % item in vars[section]:
                        if not item in vars[section]:
                            vars[section].append(item)

        # order zcml

        def zcmlsort(obja, objb):
                obja = re.sub('^#', '', obja).strip()
                objb = re.sub('^#', '', objb).strip()
                ma, mb = (package_slug_re.match(obja),
                          package_slug_re.match(objb))
                if not obja:
                    return 1
                if not objb:
                    return -1
                apackage, aslug = (obja, 'configure')
                if ma:
                    apackage, aslug = ma.groups()
                bpackage, bslug = (objb, 'configure')
                if mb:
                    bpackage, bslug = mb.groups()
                aorder = self.zcml_loading_order.get((apackage, aslug), 50000)
                border = self.zcml_loading_order.get((bpackage, bslug), 50000)
                return aorder - border

        vars["plone_zcml"].sort(zcmlsort)
        vars["plone_zcml"] = [a for a in vars["plone_zcml"] if a.strip()]

        # add option marker
        for option in self.zcml_mappings:
            for p in self.zcml_mappings[option]:
                id = '-'.join(p)
                if id in vars['plone_zcml']:
                    i = vars['plone_zcml'].index(id)
                    vars['plone_zcml'][i:i] = ['#%s' % option]
        vars['plone_zcml'][0:0] = ['']

        if not os.path.exists(self.output_dir):
            self.makedirs(self.output_dir)
        vars['plone_products_install'] = ''
        vars['zope2_install'] = ''
        vars['debug_mode'] = 'off'
        vars['verbose_security'] = 'off'

        # and getting stuff from it.
        ep = None
        try:
            if not getattr(self, 'default_template_package', None):
                raise NoDefaultTemplateError('')

            epk = pkg_resources.load_entry_point(
                self.default_template_package,
                self.default_template_epn,
                self.default_template_templaten
            )
            ep = epk(self)
            coo = command.options.overwrite
            command.options.overwrite = True

            def null(a, b, c):
                pass
            ep.post = null
            ep.check_vars(vars, command)
            ep.run(command, vars['path'], vars)
            command.options.overwrite = coo
        except NoDefaultTemplateError, e:
            pass
        except Exception, e:
            print 'Error executing plone buildout, %s' % e
        # be sure our special python is in priority
        if vars['with_supervisor_instance4']:
            vars['with_supervisor_instance3'] = True
        if vars['with_supervisor_instance3']:
            vars['with_supervisor_instance2'] = True
        if vars['with_supervisor_instance2']:
            vars['with_supervisor_instance1'] = True

        for port in range(500):
            vars['http_port%s' % port] = int(
                vars['http_port']) + port
        #if 'socket' == vars['zeo_port'].strip():
        #    vars['zeo_port_buildbot'] = int(vars['zeo_port']) + 1
        vars['running_user'] = common.running_user
        vars['instances_description'] = common.INSTANCES_DESCRIPTION % vars
        suffix = vars['major']
        if vars['major'] > 3:
            suffix = self.name.replace('genericskel.plone', '')
        zaztk_path = pkg_resources.resource_filename(
            'collective.generic.skel',
            'projects/plone%s/zopeapp.versions.cfg' % suffix
        )
        ztk_path = pkg_resources.resource_filename(
            'collective.generic.skel',
            'projects/plone%s/ztk.versions.cfg' % suffix
        )
        vars['have_ztk'] = False
        if vars['with_supervisor_instance1']:
            vars['first_instance'] = 'instance1'
        else:
            vars['first_instance'] = 'instance'
        if os.path.exists(ztk_path):
            vars['have_ztk'] = True
            vars['ztk_path'] = ztk_path
            vars['zaztk_path'] = zaztk_path
        vars['default_plone_profile'] = '%s.policy:default' % vars['project']
        if vars['with_generic_addon']:
            vars['default_plone_profile'] = '%s:default' % vars['project']
        vars['ndot'] = '.'

    def post(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        common.Package.post(self, command, output_dir, vars)
        os.rename(os.path.join(vars['path'], 'gitignore'),
                  os.path.join(vars['path'], '.gitignore'))
        for f in glob(os.path.join(output_dir, 'scripts/*')):
            os.chmod(f, 0700)
        if not vars['with_supervisor']:
            common.remove_path(self.output_dir + '/etc/sys/supervisor.cfg')
            common.remove_path(self.output_dir + '/etc/templates/supervisor')
        if not vars['with_cache_support']:
            common.remove_path(self.output_dir + '/etc/sys/cache.cfg')
            common.remove_path(self.output_dir + '/etc/templates/varnish')
        if not vars['with_haproxy']:
            common.remove_path(self.output_dir + '/etc/sys/ha.cfg')
            common.remove_path(self.output_dir + '/etc/templates/ha')
        if not vars['with_ploneproduct_etherpad']:
            common.remove_path(self.output_dir + '/etc/project/etherpad.cfg')
            common.remove_path(self.output_dir + '/etc/templates/etherpad')


plone_vars = [
    common.var('address',
               'Address to listen on', default='localhost',),
    common.var('http_port',
               'Port to listen to', default='8081',),
    common.var('zeo_host',
               'Address for the zeoserver (zeo mode only)',
               default='localhost',),
    common.var('with_zeo_socket',
               'Use socket for zeo, y/n', default='n',),
    common.var('zope_user',
               'Administrator login', default='admin',),
    common.var('zope_password',
               'Admin Password in the ZMI', default='secret',),
    common.var('with_cache_support',
               'Proxy cache (varnish)  support y/n', default='y',),
    common.var('with_supervisor',
               'Supervisor support (monitoring), '
               'http://supervisord.org/ y/n', default='y',),
    common.var('with_supervisor_instance1',
               'Supervisor will automaticly '
               'launch instance 1 in production mode  y/n', default='y',),
    common.var('with_supervisor_instance2',
               'Supervisor will automaticly '
               'launch instance 2 in production mode, y/n', default='n',),
    common.var('with_supervisor_instance3',
               'Supervisor will automaticly '
               'launch instance 3 in production mode, y/n', default='n',),
    common.var('with_supervisor_instance4',
               'Supervisor will automaticly '
               'launch instance 4 in production mode, y/n', default='n',),
    common.var('with_haproxy',
               'haproxy support (loadbalancing), '
               'http://haproxy.1wt.eu/ y/n', default='y',),
    common.var('with_no_zcml',
               'Do not include zcml information', default='n',),
    common.var('with_generic',
               'with_generic', default='n',),
    common.var('with_generic_addon',
               'with_generic_addon', default='n',),
]

Package.vars = common.Package.vars + [
    common.var('plone_version',
               'Plone version, default is the one supported and packaged',
               default=Package.packaged_version,),
] + plone_vars + Package.addons_vars + dev_vars
# vim:set et sts=4 ts=4 tw=0:
