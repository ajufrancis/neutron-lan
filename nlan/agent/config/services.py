# 2014/4/8
# services.py
#

import os
import cmdutil
from ovsdb import Row
from oputil import Model

lxc_network ="""
lxc.network.type = veth
lxc.network.flags = up
lxc.network.veth.pair = $ 
lxc.network.ipv4 = 0.0.0.0
"""

cmd = cmdutil.check_cmd

def add(model):

    model.params()

    cmd('lxc-stop -n', _name_)

    #print _name, name_
    conf = os.path.join('/var/lib/lxc', _name_, 'config')
    with open(conf, 'r') as f:
        lines = f.read()

    conf = os.path.join('/var/lib/lxc', _name_, 'config_nlan')
    with open(conf, 'w') as f:
        f.seek(0)
        f.truncate()
        f.write(lines)
        if _chain:
            for path in _chain: 
                net = lxc_network.replace('$', path)
                f.write(net)

    cmd('lxc-start -d -f', conf, '-n', _name_)

    #OVSDB transaction
    model.finalize()

def delete(model):
    model.params()
    
    if _name and not chain_ or _name and _chain:
        cmd('lxc-stop -n', name_)
    elif not _name and _chain:
        cmd('lxc-stop -n', name_)
        conf = os.path.join('/var/lib/lxc', name_, 'config')
        with open(conf, 'r') as f:
            lines = f.read()

        conf = os.path.join('/var/lib/lxc', name_, 'config_nlan')
        with open(conf, 'w') as f:
            f.seek(0)
            f.truncate()
            f.write(lines)

        cmd('lxc-start -d -f', conf, '-n', name_)
    else:
        raise ModelError("illegal operation", model=model.model)

    model.finalize()


def update(model):

    model.params()

    if _name:
        raise ModelError("renaming container not allowed", model=model.model)
    elif _chain:
        cmd('lxc-stop -n', name_)

        conf = os.path.join('/var/lib/lxc', name_, 'config')
        with open(conf, 'r') as f:
            lines = f.read()

        conf = os.path.join('/var/lib/lxc', name_, 'config_nlan')
        with open(conf, 'w') as f:
            f.seek(0)
            f.truncate()
            f.write(lines)
            for path in _chain: 
                net = lxc_network.replace('$', path)
                f.write(net)

        cmd('lxc-start -d -f', conf, '-n', name_)

    #OVSDB transaction
    model.finalize()
