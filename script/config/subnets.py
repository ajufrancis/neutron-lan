# 2014/3/17
# subnets.py
#

import cmdutil
import re
from ovsdb import Row

# Add a subnet
def _add_subnets(vid, ip_dvr, ip_vhost, ports=None, default_gw=None):
	
    import re

    cmd = cmdutil.cmd
    output_cmd = cmdutil.output_cmd

    ns = "ns"+vid
    br = "br"+vid
    veth_ns = "veth-ns"+vid
    temp_ns = "temp-ns"+vid
    int_br = "int-br"+vid
    int_dvr = "int-dvr"+vid

    cmd('ip netns add' , ns)
    cmd('brctl addbr', br)
    cmd('ip link add', veth_ns, 'type veth peer name', temp_ns)
    cmd('ip link set dev', temp_ns, 'netns', ns)
    cmd('ip netns exec', ns, 'ip link set dev', temp_ns, 'name eth0')
    cmd('ip netns exec', ns, 'ip addr add dev eth0', ip_vhost)
    cmd('ovs-vsctl add-port br-int', int_br, 'tag='+vid, '-- set interface', int_br, 'type=internal')
    cmd('ovs-vsctl add-port br-int', int_dvr, 'tag='+vid, '-- set interface', int_dvr, 'type=internal')
    cmd('brctl addif', br, veth_ns)
    cmd('brctl addif', br, int_br)
    cmd('ip addr add dev', int_dvr, ip_dvr)
    cmd('ip link set dev', veth_ns, 'promisc on')
    cmd('ip link set dev', veth_ns, 'up')
    #cmd('ip netns exec', ns, 'ip link set dev eth0 promisc on')
    cmd('ip netns exec', ns, 'ip link set dev eth0 up')
    cmd('ip link set dev', int_br, 'promisc on')
    cmd('ip link set dev', int_br, 'up')
    #cmd('ip link set dev', int_dvr, 'promisc on')
    cmd('ip link set dev', int_dvr, 'up')
    cmd('ip link set dev', br, 'up')

    # Distributed Virtual Router
    cmd('ip netns exec', ns, 'ip route add default via', ip_dvr.split('/')[0], 'dev eth0')

    # Adding physical ports to the Linux bridge
    if ports != None:
        for port in ports:
            cmd('brctl addif', br, port)

    # Default GW for the subnet
    if default_gw != None:
        o = output_cmd('route -n').splitlines()
        for l in o:
            if l.startswith('default'):
                cmd('ip route del default')
        cmd('ip route add default via', default_gw)

	

# Adds flow entries 
def _add_flow_entries(vid_vni_defaultgw):

    output_cmd = cmdutil.output_cmd

    patch_tun = ''
    vxlan_ports = []

    controller = False
    try:
        if output_cmd('ovs-vsctl get-controller br-tun') != '':
            controller = True
    except:
        raise Exception("ovs-vsctl get-controller br-tun")

    if not controller:
        print '>>> Adding flows: br-tun'

        output = output_cmd('ovs-ofctl show br-tun')
        output = output.split('\n')
        for line in output:
            m = re.search(r"^\s[0-9]+\(patch-tun", line)
            if m:
                patch_tun = m.group().split("(")[0].strip()
                break
        for line in output:
            vxlan = re.search(r"\s[0-9]+\(vxlan", line)
            if vxlan:
                vxlan_port = vxlan.group().split("(")[0].strip()
                vxlan_ports.append(vxlan_port)
                vxlan = None

        for combo in vid_vni_defaultgw:
            combo[0] = str(combo[0])
            combo[1] = str(combo[1])
        #print patch_tun
        #print vxlan_ports
        #print vid_vni_defaultgw

        cmd = cmdutil.check_cmd

        cmd('ovs-ofctl del-flows br-tun')
        cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=1,in_port='+patch_tun+',actions=resubmit(,1)')
        for vxlan_port in vxlan_ports:
            cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=1,in_port='+vxlan_port+',actions=resubmit(,2)')
        cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=0,actions=drop')
        #cmd('ovs-ofctl add-flow br-tun', 'table=1,priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00,actions=resubmit(,21)')
        cmd('ovs-ofctl add-flow br-tun', 'table=1,priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00,actions=resubmit(,19)')
        cmd('ovs-ofctl add-flow br-tun', 'table=1,priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00,actions=resubmit(,20)')
        for combo in vid_vni_defaultgw:
            vid = combo[0]
            vni = combo[1]
            defaultgw = combo[2]
            cmd('ovs-ofctl add-flow br-tun', 'table=2,priority=1,tun_id='+vni+',actions=mod_vlan_vid:'+vid+',resubmit(,10)')
        cmd('ovs-ofctl add-flow br-tun', 'table=2,priority=0,actions=drop')
        cmd('ovs-ofctl add-flow br-tun', 'table=3,priority=0,actions=drop')
        cmd('ovs-ofctl add-flow br-tun', 'table=10,priority=1,actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:'+patch_tun)
        # Drops ARP with target ip = default gw
        for combo in vid_vni_defaultgw:
            vid = combo[0]
            defaultgw = combo[2].split('/')[0]
            cmd('ovs-ofctl add-flow br-tun', 'table=19,priority=1,dl_type=0x0806,dl_vlan='+vid+',nw_dst='+defaultgw+',actions=drop')
        cmd('ovs-ofctl add-flow br-tun', 'table=19,priority=0,actions=resubmit(,21)')
        cmd('ovs-ofctl add-flow br-tun', 'table=20,priority=0,actions=resubmit(,21)')
        output_ports = ''
        for vxlan_port in vxlan_ports:
            output_ports = output_ports+',output:'+vxlan_port
        for combo in vid_vni_defaultgw:
            vid = combo[0]
            vni = combo[1]
            cmd('ovs-ofctl add-flow br-tun', 'table=21,priority=1,dl_vlan='+vid+',actions=strip_vlan,set_tunnel:'+vni+output_ports)
        cmd('ovs-ofctl add-flow br-tun', 'table=21,priority=0,actions=drop')


def add(model):

    cmd = cmdutil.cmd	
    vid_vni_defaultgw=[]
    for key in model.keys():
        # key[0] == 'vni'
        vni = key[1] 
        subnet = model[key]
        vid = subnet['vid']
        vni = subnet['vni']
        ip_dvr = subnet['ip_dvr']
        ports = None
        if 'ports' in subnet:
            ports = subnet['ports']
        default_gw = None
        if 'default_gw' in subnet:
            default_gw = subnet['default_gw']
        ip_vhost = subnet['ip_vhost']
        print '>>> Adding a subnet(vlan): ' + str(vid)
        _add_subnets(vid=str(vid), ip_dvr=ip_dvr, ip_vhost=ip_vhost, ports=ports, default_gw=default_gw)
        vid_vni_defaultgw.append([str(vid), str(vni), ip_dvr])

    _add_flow_entries(vid_vni_defaultgw)

    # OVSDB transaction
    for key in model.keys():
        r = Row('subnets', key)
        r.setrow(model[key])

