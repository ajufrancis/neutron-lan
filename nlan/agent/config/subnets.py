# 2014/3/17
# 2014/4/14  Service Chaining ('dvr', 'hub' and 'spoke_dvr' mode)
# 2014/4/24  get_all()
# subnets.py
#

import cmdutil
import re
from ovsdb import Row, OvsdbRow, search, get_vxlan_ports 
from oputil import Model

# Add subnet
def _add_subnets():
	
    cmd = cmdutil.check_cmd
    output_cmd = cmdutil.output_cmd
    cmdp = cmdutil.check_cmdp

    svid = str(_vid_)
    ns = "ns"+svid
    br = "br"+svid
    veth_ns = "veth-ns"+svid
    temp_ns = "temp-ns"+svid
    int_br = "int-br"+svid
    int_dvr = "int-dvr"+svid

    #>>> Adding VLAN and a linux bridge
    if _vid:
        cmd('ip netns add' , ns)
        cmd('brctl addbr', br)
        cmd('ip link add', veth_ns, 'type veth peer name', temp_ns)
        cmd('ip link set dev', temp_ns, 'netns', ns)
        cmd('ip netns exec', ns, 'ip link set dev', temp_ns, 'name eth0')
        cmdp('ovs-vsctl add-port br-int', int_br, 'tag='+svid, '-- set interface', int_br, 'type=internal')
        cmdp('ovs-vsctl add-port br-int', int_dvr, 'tag='+svid, '-- set interface', int_dvr, 'type=internal')
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
    if _ip_vhost:
        cmd('ip netns exec', ns, 'ip addr add dev eth0', _ip_vhost)

    #>>> Adding DVR gateway address
    if _ip_dvr:
        cmd('ip addr add dev', int_dvr, _ip_dvr)
        # Distributed Virtual Router
        cmd('ip netns exec', ns, 'ip route add default via', _ip_dvr.split('/')[0], 'dev eth0')

    #>>> Adding physical ports to the Linux bridge
    if _ports:
        for port in _ports:
            cmd('brctl addif', br, port)

    #>>> Default GW for the subnet
    if _default_gw:
        o = output_cmd('route').splitlines()
        for l in o:
            if l.startswith('default'):
                cmd('ip route del default')
        cmd('ip route add default via', _default_gw)
	

# Adds flow entries 
# 1) mode == 'dvr' or default
#  Remote node
#     ^
#     | Dropped (one way)
#     |
#  ARP w/ TPA = ip_dvr
# [br-tun]
#
# 2) mode == 'spoke_dvr'
# [br-int]
#     ^ Dropped (one way)
#     | 
#     | int-dvr
#  ARP (opcode=2) w/ SPA = ip_dvr
#  opcode 1: ARP Request
#  opcode 2: ARP Reply
# 
#  In this mode, all the packets pertaining to the other subnets (excluding
#  global IP addresses) are also redirected to the 'local' ip_dvr for
#  distributed virtual routing.
#
# 3) mode == 'hub' or 'spoke'
# No flow entries added
#
def _add_flow_entries():
    
    svid = str(_vid_)
    int_dvr = "int-dvr"+svid
    int_br = "int-br"+svid
    svni = str(_vni_)

    # serarch Open_vSwitch table
    if len(search('Controller', ['target'])) == 0:

        cmd = cmdutil.check_cmd

        cmd('ovs-ofctl add-flow br-tun', 'table=2,priority=1,tun_id='+svni+',actions=mod_vlan_vid:'+svid+',resubmit(,10)')
        
        #print ip_dvr, mode
        if _ip_dvr and (_mode == 'dvr' or not _mode):
            defaultgw = _ip_dvr.split('/')[0]
            cmd('ovs-ofctl add-flow br-tun', 'table=19,priority=1,dl_type=0x0806,dl_vlan='+svid+',nw_dst='+defaultgw+',actions=drop')
        # Redirects a packet to int_dvr port if nw_dst is a private ip address
        elif _ip_dvr and _mode == 'spoke_dvr':
            defaultgw = _ip_dvr.split('/')[0]
            mask = _ip_dvr.split('/')[1]
            address = defaultgw.split('.')
            shift = 32 - int(mask)
            net = (int(address[0])*256**3+int(address[1])*256**2+int(address[2])*256+int(address[3]))>>shift<<shift
            a = str(net>>24)
            b1 = net>>16
            b2 = net>>24<<8
            b = str(b1 - b2)
            c1 = net>>8
            c2 = net>>16<<8
            c = str(c1 - c2)
            d1 = net
            d2 = net>>8<<8
            d = str(d1 - d2)
            nw_dst = '.'.join([a,b,c,d])+'/'+mask
            #print nw_dst

            output = cmdutil.output_cmd('ip link show dev', int_dvr).split('\n')[1]
            dl_type='0x0800'
            dl_dst = output.split()[1]
            nw_dst10 = '10.0.0.0/8'
            nw_dst172 = '172.16.0.0/12'
            nw_dst192 = '192.168.0.0/16'
            
            r = OvsdbRow('Interface', ('name', int_dvr))
            outport = str(r['ofport'])
            r = OvsdbRow('Interface', ('name', int_br))
            inport = str(r['ofport'])

            cmd('ovs-ofctl add-flow br-int', 'table=0,priority=2,in_port='+inport+',dl_type='+dl_type+',nw_dst='+nw_dst+',actions=normal')
            cmd('ovs-ofctl add-flow br-int', 'table=0,priority=1,in_port='+inport+',dl_type='+dl_type+',nw_dst='+nw_dst10+',actions=resubmit(,1)')
            cmd('ovs-ofctl add-flow br-int', 'table=0,priority=1,in_port='+inport+',dl_type='+dl_type+',nw_dst='+nw_dst172+',actions=resubmit(,1)')
            cmd('ovs-ofctl add-flow br-int', 'table=0,priority=1,in_port='+inport+',dl_type='+dl_type+',nw_dst='+nw_dst192+',actions=resubmit(,1)')
            # ARP, opcode = 2, TPA = defaultgw
            cmd('ovs-ofctl add-flow br-int', 'table=0,priority=1,in_port='+outport+',dl_type=0x0806,nw_src='+defaultgw+',nw_proto=2,actions=drop')
            cmd('ovs-ofctl add-flow br-int', 'table=1,priority=0,actions=set_field:'+dl_dst+'->dl_dst,output:'+outport)
        elif _ip_dvr and _mode == 'hub' or 'spoke':
            pass
        else:
            pass 

        # Broadcast tree for each vni
        output_ports = ''
        vxlan_ports = get_vxlan_ports(_peers)
        for vxlan_port in vxlan_ports:
            output_ports = output_ports+',output:'+vxlan_port
        cmd('ovs-ofctl add-flow br-tun', 'table=21,priority=1,dl_vlan='+svid+',actions=strip_vlan,set_tunnel:'+svni+output_ports)
        

def _crud(crud, model, index):

    cmd = cmdutil.cmd	
    vni = index[1] 

    m = Model(crud, model, index)

    __n__['logger'].info('Adding a subnet(vlan): ' + str(_vid))
    globals()['_'+crud+'_subnets']()
    globals()['_'+crud+'_flow_entries']()

    # OVSDB transaction
    m.finalize()

def add(model, index):

    _crud('add', model, index)

def delete(model, index):

    _crud('delete', model, index)

def update(model, index):

    _crud('update', model, index)

