# 2014/3/17
# bridges.py
#

import cmdutil

def add(model):

    print '>>> Adding bridges: br-int and br-tun'
    cmd = cmdutil.cmd	
    cmd('ovs-vsctl add-br br-int')
    cmd('ovs-vsctl add-br br-tun')
    cmd('ovs-ofctl del-flows br-tun')
    cmd('ovs-vsctl add-port br-int patch-int -- set interface patch-int type=patch options:peer=patch-tun')
    cmd('ovs-vsctl add-port br-tun patch-tun -- set interface patch-tun type=patch options:peer=patch-int')
    # OpenFlow Controller
    if 'controller' in model:
        cmd('ovs-vsctl set-controller br-tun tcp:'+ model['controller'])


