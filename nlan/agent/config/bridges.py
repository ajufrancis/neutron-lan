# 2014/3/17
# bridges.py
#

import cmdutil
from ovsdb import Row, OvsdbRow

def add(model):

    __n__['logger'].info('Adding bridges: br-int and br-tun')

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
        cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=0,actions=drop')
        cmd('ovs-ofctl add-flow br-tun', 'table=1,priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00,actions=resubmit(,19)')
        cmd('ovs-ofctl add-flow br-tun', 'table=1,priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00,actions=resubmit(,20)')
        # Obtains ofport for 'patch-tun' port
        r = OvsdbRow('Interface', ('name', 'patch-tun'))
        patch_tun = str(r['ofport'])
        cmd('ovs-ofctl add-flow br-tun', 'table=2,priority=0,actions=drop')
        cmd('ovs-ofctl add-flow br-tun', 'table=3,priority=0,actions=drop')
        cmd('ovs-ofctl add-flow br-tun', 'table=10,priority=1,actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:'+patch_tun)
        cmd('ovs-ofctl add-flow br-tun', 'table=19,priority=0,actions=resubmit(,21)')
        cmd('ovs-ofctl add-flow br-tun', 'table=20,priority=0,actions=resubmit(,21)')
        cmd('ovs-ofctl add-flow br-tun', 'table=21,priority=0,actions=drop')

    # OVSDB transaction
    r = Row('bridges')
    r.setrow(model)


