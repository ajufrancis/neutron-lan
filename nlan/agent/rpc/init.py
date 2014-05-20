# 2014/3/17
# init.py
#

from cmdutil import *
from ovsdb import Row

# Initialize the configuration
def run():

    # Stop all running Linux containers 
    try:
        lxc_ls = output_cmd('lxc-ls').rstrip('\n').split('\n')
        for container in lxc_ls:
            cmd('lxc-stop -n', container)
    except:
        pass

    # Delete all the ovs bridges
    cmd('ovs-vsctl --if-exists del-br br-tun')
    cmd('ovs-vsctl --if-exists del-br br-int')

    # Delete linux bridges (br*)
    """
    $ brctl show
    bridge name     bridge id               STP enabled     interfaces
    br0             8000.5a3e95b90f2d       no              aaa00
                                                            aaa01
    br1             8000.16877c5f2ca9       no              bbb00
                                                            bbb01
    """
    bridges = {}
    brname = ''
    o = output_cmd('brctl show').split('\n')
    for l in o:
        ll = l.split()
        if len(ll) == 7:
            pass
        elif len(ll) == 4:
            brname = ll[0]
            interface = ll[3]
            if brname.startswith('br'):
                bridges[brname] = [interface]
        elif len(ll) == 3:
            brname = ll[0]
            if brname.startswith('br'):
                bridges[brname] = [] 
        elif len(ll) == 1:
            interface = ll[0]
            if brname.startswith('br'):
                bridges[brname].append(interface)

    for brname in bridges.keys():
        for interface in bridges[brname]:
            cmd('ip link set dev', interface, 'down')
            cmd('brctl delif', brname, interface)
            cmd('ip link set dev', interface, 'up')
        cmd('ip link set dev', brname, 'down')
        cmd('brctl delbr', brname)

    # Delete all the netns
    l = output_cmd('ip netns list')
    l = l.split('\n')
    for ns in l[:-1]:
        cmd('ip netns del', ns)
    
    # OVSDB transaction
    Row.clear()


