# 2014/3/17
# bridges.py
#

import cmdutil
from ovsdb import Row, OvsdbRow

def add(model):

    print '>>> Adding bridges: br-int and br-tun'
    cmd = cmdutil.cmd	
    cmd('ovs-vsctl add-br br-int')
    cmd('ovs-vsctl add-br br-tun')
    cmd('ovs-ofctl del-flows br-tun')
    cmd('ovs-vsctl add-port br-int patch-int -- set interface patch-int type=patch options:peer=patch-tun')
    cmd('ovs-vsctl add-port br-tun patch-tun -- set interface patch-tun type=patch options:peer=patch-int')

    if 'controller' in model:
        # OpenFlow Controller
        cmd('ovs-vsctl set-controller br-tun tcp:'+ model['controller'])
    else:
        # Flow entries
        r = OvsdbRow('Interface', ('name', 'patch-tun'))
        patch_tun = str(r['ofport'])
        cmd('ovs-ofctl del-flows br-tun')
        cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=1,in_port='+patch_tun+',actions=resubmit(,1)')

    # OVSDB transaction
    r = Row('bridges')
    r.setrow(model)


