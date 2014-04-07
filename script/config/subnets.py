# 2014/3/17
# subnets.py
#

import cmdutil
import re
from ovsdb import Row, OvsdbRow, search, get_vxlan_ports 
from oputil import Model

# Add subnet
def _add_subnets(vni, vid, ip_dvr, ip_vhost, ports, default_gw):
	
    cmd = cmdutil.cmd
    output_cmd = cmdutil.output_cmd

    row = Row('subnets', ('vni', vni))
  
    vid2 = None
    if vid:
        vid2= str(vid)
    else:
        vid2 = row['vid']

    ns = "ns"+vid2
    br = "br"+vid2
    veth_ns = "veth-ns"+vid2
    temp_ns = "temp-ns"+vid2
    int_br = "int-br"+vid2
    int_dvr = "int-dvr"+vid2
    svid = str(vid2)

    #>>> Adding VLAN and a linux bridge
    if vid:
        cmd('ip netns add' , ns)
        cmd('brctl addbr', br)
        cmd('ip link add', veth_ns, 'type veth peer name', temp_ns)
        cmd('ip link set dev', temp_ns, 'netns', ns)
        cmd('ip netns exec', ns, 'ip link set dev', temp_ns, 'name eth0')
        cmd('ovs-vsctl add-port br-int', int_br, 'tag='+svid, '-- set interface', int_br, 'type=internal')
        cmd('ovs-vsctl add-port br-int', int_dvr, 'tag='+svid, '-- set interface', int_dvr, 'type=internal')
        cmd('brctl addif', br, veth_ns)
        cmd('brctl addif', br, int_br)
        cmd('ip link set dev', veth_ns, 'promisc on')
        cmd('ip link set dev', veth_ns, 'up')
        #cmd('ip netns exec', ns, 'ip link set dev eth0 promisc on')
        cmd('ip netns exec', ns, 'ip link set dev eth0 up')
        cmd('ip link set dev', int_br, 'promisc on')
        cmd('ip link set dev', int_br, 'up')
        #cmd('ip link set dev', int_dvr, 'promisc on')
        cmd('ip link set dev', int_dvr, 'up')
        cmd('ip link set dev', br, 'up')

    #>>> Adding vHost
    if ip_vhost:
        cmd('ip netns exec', ns, 'ip addr add dev eth0', ip_vhost)

    #>>> Adding DVR gateway address
    if ip_dvr:
        cmd('ip addr add dev', int_dvr, ip_dvr)
        # Distributed Virtual Router
        cmd('ip netns exec', ns, 'ip route add default via', ip_dvr.split('/')[0], 'dev eth0')

    #>>> Adding physical ports to the Linux bridge
    if ports:
        for port in ports:
            cmd('brctl addif', br, port)

    #>>> Default GW for the subnet
    if default_gw:
        o = output_cmd('route').splitlines()
        for l in o:
            if l.startswith('default'):
                cmd('ip route del default')
        cmd('ip route add default via', default_gw)
	

# Adds flow entries 
def _add_flow_entries(vid, vni, ip_dvr, peers):

    vid = str(vid)
    vni = str(vni)

    if len(search('Controller', ['target'])) == 0:

        cmd = cmdutil.check_cmd

        cmd('ovs-ofctl add-flow br-tun', 'table=2,priority=1,tun_id='+vni+',actions=mod_vlan_vid:'+vid+',resubmit(,10)')
        
        # Drops ARP with target ip = default gw
        defaultgw = ip_dvr.split('/')[0]
        cmd('ovs-ofctl add-flow br-tun', 'table=19,priority=1,dl_type=0x0806,dl_vlan='+vid+',nw_dst='+defaultgw+',actions=drop')

        # Broadcast tree for each vni
        output_ports = ''
        vxlan_ports = get_vxlan_ports(peers)
        for vxlan_port in vxlan_ports:
            output_ports = output_ports+',output:'+vxlan_port
        cmd('ovs-ofctl add-flow br-tun', 'table=21,priority=1,dl_vlan='+vid+',actions=strip_vlan,set_tunnel:'+vni+output_ports)
        

# Mandatory parameters
# (1) vid, ip_dvr, ip_vhost, default_gw 
# (2) ports
def _crud(crud, model):

    cmd = cmdutil.cmd	
    for key in model.keys():
        # key[0] == 'vni'
        vni = key[1] 
        m = Model(model[key])
        vid, ip_dvr, ip_vhost, ports, default_gw, peers = m.getparam('vid', 'ip_dvr', 'ip_vhost', 'ports', 'default_gw', 'peers')
        print '>>> Adding a subnet(vlan): ' + str(vid)
        globals()['_'+crud+'_subnets'](vni=vni, vid=vid, ip_dvr=ip_dvr, ip_vhost=ip_vhost, ports=ports, default_gw=default_gw)
        globals()['_'+crud+'_flow_entries'](vid, vni, ip_dvr, peers)

    # OVSDB transaction
    for key in model.keys():
        r = Row('subnets', key)
        r.crud(crud, model[key])

def add(model):

    #paramset = ('vni', 'vid', 'ip_dvr', 'ip_vhost')

    _crud('add', model)

def delete(model):

    #paramset = ('vni', 'vid', 'ip_dvr', 'ip_vhost')

    _crud('delete', model)

def update(model):

    #paramset = ()

    _crud('update', model)

