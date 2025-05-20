
# Copyright (C) 2009, Makina Corpus <freesoftware@makina-corpus.com>
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

import copy
import os

import pkg_resources

from collective.generic.skel.buildout import common
var = common.var
running_user = common.running_user
gid = common.gid
group = common.group


default_config = pkg_resources.resource_filename(
    'collective.generic.skel',
    'buildout/pyramid/genericskel.pyramid.xml')
user_config = os.path.join(os.path.expanduser('~'), '.genericskel.pyramid.xml')
xmlvars = common.read_vars(default_config, user_config)
# variables discovered via configuration
addons_vars = xmlvars.get('addons_vars', {})
# mappings option/eggs to install
eggs_mappings = xmlvars.get('eggs_mappings', {})
# scripts to generate
scripts_mappings = xmlvars.get('scripts_mappings', {})
# mappings option/versions to pin
versions_mappings = xmlvars.get('versions_mappings', {})
# mappings option/versions to pin if the user wants really stable sets
checked_versions_mappings = xmlvars.get('checked_versions_mappings', {})
# mappings option/nested packages/version suffix packages  to install
plone_np_mappings = xmlvars.get('plone_np_mappings', {})
plone_vsp_mappings = xmlvars.get('plone_vsp_mappings', {})
plone_sources = xmlvars.get('plone_sources', {})
framework_apps = xmlvars.get('framework_apps', {})
dev_desc = 'Install %s in development mode.'
dev_vars = []
sources_k = plone_sources.keys()
sources_k.sort()
for name in sources_k:
    dev_vars.append(
        var(
            'with_autocheckout_%s' % name,
            description=name,
            default="n",
        )
    )

base_pyramid_eggs = [
    'CherryPy',
    'cryptacular',
    'gunicorn',
    'iniparse',
    'Paste',
    'PasteDeploy',
    'Pastescript',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_zcml',
    'repoze.tm2',
    'repoze.vhm',
    'waitress',
    'WebError',
    'WebOb',
    'zope.component',
]


class Package(common.Package):

    summary = (
        'Package for creating a '
        'basic pyramid project')
    _template_dir = pkg_resources.resource_filename(
        'collective.generic.skel', 'buildout/pyramid/tmpl')
    python = 'python-2.7'
    init_messages = ()

    # buildout <-> genericskel config vars mapping
    sections_mappings = {
        'pyramid_np': plone_np_mappings,
        'pyramid_vsp': plone_vsp_mappings,
        'additional_eggs': eggs_mappings,
        'plone_scripts': scripts_mappings,
        'framework_apps': framework_apps,
    }
    addons_vars = common.get_ordered_discovered_options(addons_vars.values())
    eggs_mappings = eggs_mappings
    scripts_mappings = scripts_mappings
    versions_mappings = versions_mappings
    checked_versions_mappings = checked_versions_mappings
    plone_np_mappings = plone_np_mappings
    plone_vsp_mappings = plone_vsp_mappings
    plone_sources = plone_sources

    def post(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        common.Package.post(self, command, output_dir, vars)
        if not vars['with_supervisor']:
            common.remove_path(self.output_dir + '/etc/sys/supervisor.cfg')
            common.remove_path(self.output_dir + '/etc/templates/supervisor')

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        vars['category'] = 'pyramid'
        common.Package.pre(self, command, output_dir, vars)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        vars['sane_name'] = common.SPECIALCHARS.sub('', vars['project'])
        vars['includesdirs'] = ''
        vars['hr'] = '#' * 120

        # transforming eggs requirements as lists
        for var in self.sections_mappings:
            if var in vars:
                vars[var] = [a.strip() for a in vars[var].split(',')]

        # Django core eggs
        vars['additional_eggs'].append('#Pyramid')
        vars['additional_eggs'].extend(base_pyramid_eggs)

        # databases
        for db in [var.replace('with_database_', '')
                   for var in vars
                   if 'with_database_' in var
                   and vars[var]]:
            if not db in ['sqlite']:
                vars['additional_eggs'].extend(
                    [a
                     for a in eggs_mappings['with_database_%s' % db]
                     if not a in vars['additional_eggs']]
                )
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        vars['framework_apps'] = []
        for section in self.sections_mappings:
            for var in [k
                        for k in self.sections_mappings[section]
                        if vars.get(k, '')]:
                vars[section].append('#%s' % var)
                for item in self.sections_mappings[section][var]:
                    if not '%s\n' % item in vars[section]:
                        if not item in vars[section]:
                            vars[section].append(item)
        # http serverS ports
        vars['supervisor_port'] = int(vars['http_port']) - 1
        vars['supervisor_host'] = vars['address']
        for i in range(30):
            vars['http_port%s' % i] = int(vars['http_port']) + i
        vars['running_user'] = common.running_user
        vars['instances_description'] = common.INSTANCES_DESCRIPTION % vars
        if not vars['reverseproxy_aliases']:
            vars['reverseproxy_aliases'] = ''
        vars['sreverseproxy_aliases'] = vars['reverseproxy_aliases'].split(',')
        # be sure our special python is in priority
        if vars['with_supervisor_instance4']:
            vars['with_supervisor_instance3'] = True
        if vars['with_supervisor_instance3']:
            vars['with_supervisor_instance2'] = True
        if vars['with_supervisor_instance2']:
            vars['with_supervisor_instance1'] = True

    def read_vars(self, command=None):
        vars = common.Package.read_vars(self, command)
        if command:
            if not command.options.quiet:
                for msg in getattr(self, 'init_messages', []):
                    print msg
        for i, var in enumerate(vars[:]):
            if var.name in ['deliverance_project',
                            'db_name',
                            'db_dbuser'] and command:
                sane_name = common.SPECIALCHARS.sub('', command.args[0])
                vars[i].default = sane_name
            if var.name in ['reverseproxy_host'] and command:
                sane_name = '%s.localhost' % (
                    common.SPECIALCHARS.sub('', command.args[0]))
                vars[i].default = sane_name
        return vars

Package.vars = common.Package.vars + [
    var('pyramid_version', 'Pyramid version', default='1.5a2',),
    var('address', 'Address to listen on', default='localhost',),
    var('license', 'License', default='BSD',),
    var('http_port', 'Port to listen to', default='8081',),
    var('db_type', ' database type (sqlite, postgresql, mysql)',
        default='postgresql',),
    var('db_host', 'database host', default='localhost',),
    var('db_port', 'databse port. (postgresql : 5432, mysql : 3306)',
        default='5432',),
    var('db_name', 'database name', default='pyramiddb',),
    var('db_user', 'database user', default=common.running_user),
    var('db_password', 'database password', default='secret',),

    var('admin_user', 'Administrator Login', default='admin',),
    var('admin_password', 'Admin Password', default='secret',),
    var('effective_user',
        'effective user to give the files to in production',
        default=running_user,),
    var('supervisor_user', 'Supervisor web user', default='admin',),
    var('supervisor_password', 'Supervisor web password', default='secret',),
    var('with_supervisor',
        'Supervisor support (monitoring), http://supervisord.org/ y/n',
        default='y',),
    var('with_supervisor_instance1', 'Supervisor will automaticly '
        'launch instance 1 in production mode  y/n', default='y',),
    var('with_supervisor_instance2', 'Supervisor will automaticly '
        'launch instance 2 in production mode, y/n', default='n',),
    var('with_supervisor_instance3', 'Supervisor will automaticly '
        'launch instance 3 in production mode, y/n', default='n',),
    var('with_supervisor_instance4', 'Supervisor will '
        'automaticly launch instance 4 in production mode, y/n', default='n',),
    var('plone_products',
        'comma separeted list of adtionnal products to '
        'install: eg: file://a.tz file://b.tgz', default='',),
    var('additional_eggs',
        'comma separeted list of additionnal eggs to install', default='',),
    var('plone_scripts',
        'comma separeted list of scripts to generate '
        'from installed eggs', default='',),
] + Package.addons_vars + dev_vars

# vim:set et sts=4 ts=4 tw=80:
