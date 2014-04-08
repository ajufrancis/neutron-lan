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
        for path in chain: 
            net = lxc_network.replace('$', path)

            conf = os.path.join('/var/lib/lxc', name, 'config')
            with open(conf, 'a') as f:
                f.write(net)

    cmd = cmdutil.check_cmd
    cmd('lxc-start -d -n', name)

    # OVSDB transaction
    # r = Row('services')
    # r.setrow(model)




