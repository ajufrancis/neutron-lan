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

def add(model):

    for key in model.keys():

        name = key[1]
        m = Model(model[key])
        function, mode, chain = m.getparam('function', 'mode', 'chain')

        conf = os.path.join('/var/lib/lxc', name, 'config')
        with open(conf, 'r') as f:
            lines = f.read()

        conf = os.path.join('/var/lib/lxc', name, 'config_nlan')
        with open(conf, 'w') as f:
            f.seek(0)
            f.truncate()
            f.write(lines)
            for path in chain: 
                net = lxc_network.replace('$', path)
                f.write(net)

        cmd = cmdutil.check_cmd
        cmd('lxc-start -d -f', conf, '-n', name)

    # OVSDB transaction
    # r = Row('services')
    # r.setrow(model)




