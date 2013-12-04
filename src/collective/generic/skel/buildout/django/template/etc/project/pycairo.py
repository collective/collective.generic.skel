import sys
import os
import re

ref = re.M | re.I | re.U


def which(program, environ=None, key='PATH', split=':'):
    if not environ:
        environ = os.environ
    PATH = environ.get(key, '').split(split)
    for entry in PATH:
        fp = os.path.abspath(os.path.join(entry, program))
        if os.path.exists(fp):
            return fp
        if (
            (sys.platform.startswith('win')
             or sys.platform.startswith('cyg'))
            and os.path.exists(fp + '.exe')
        ):
            return fp + '.exe'
    raise IOError('Program not fond: %s in %s ' % (program, PATH))


def pycairo(options, buildout):
    cwd = os.getcwd()
    if not os.path.isfile(options['configure']):
        options['configure'] = which(options['configure'])
    os.chdir(options['compile-directory'])
    cmd = '%s %s%s %s' % (
        options['configure'],
        options['prefix-option'],
        options['prefix'],
        options['configure-options']
    )
    print "Running %s" % cmd
    os.system(cmd)
    os.chdir(cwd)
