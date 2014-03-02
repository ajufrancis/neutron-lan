# 2014/2/10
# dvsdvr.py
#

import cmdutil
import re

# Initialize the configuration
def init(hardware):

    cmd = cmdutil.cmd
    output_cmd = cmdutil.output_cmd

    # Delete all the ovs bridges
    cmd('ovs-vsctl --if-exists del-br br-tun')
    cmd('ovs-vsctl --if-exists del-br br-int')
    l = output_cmd('ip netns list')
    l = l.split('\n')
    for ns in l[:-1]:
        cmd('ip netns del', ns)

    # Delete all the linux bridges
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
            bridges[brname] = [interface]
        elif len(ll) == 1:
            interface = ll[0]
            bridges[brname].append(interface)
    for brname in bridges.keys():
        for interface in bridges[brname]:
            cmd('ip link set dev', interface, 'down')
            cmd('brctl delif', brname, 'down')
        cmd('ip link set dev', brname, 'down')
        cmd('brctl delbr', brnmae)
        

# Add a subnet
def _add_subnets(hardware, vid, ip_dvr, ip_vhost):
	
    import re

    cmd = cmdutil.cmd

    ns = "ns"+vid
    br = "br"+vid
    veth_ns = "veth-ns"+vid
    temp_ns = "temp-ns"+vid
    int_br = "int-br"+vid
    int_dvr = "int-dvr"+vid
    eth0_vid = "eth0."+vid

    cmd('ip netns add' , ns)
    cmd('brctl addbr', br)
    cmd('ip link add', veth_ns, 'type veth peer name', temp_ns)
    cmd('ip link set dev', temp_ns, 'netns', ns)
    cmd('ip netns exec', ns, 'ip link set dev', temp_ns, 'name eth0')
    cmd('ip netns exec', ns, 'ip addr add dev eth0', ip_vhost)
    cmd('ovs-vsctl add-port br-int', int_br, 'tag='+vid, '-- set interface', int_br, 'type=internal')
    cmd('ovs-vsctl add-port br-int', int_dvr, 'tag='+vid, '-- set interface', int_dvr, 'type=internal')
    if hardware == 'bhr_4grv':
        cmd('brctl addif', br, eth0_vid)
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
	
# Adds br-tun
def _add_br_tun(vid_vni_defaultgw):

    output_cmd = cmdutil.output_cmd

    patch_tun = ''
    vxlan_ports = []
    
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



def add_bridges(hardware, model):

    print '>>> Adding bridges: br-int and br-tun'
    cmd = cmdutil.cmd	
    cmd('ovs-vsctl add-br br-int')
    cmd('ovs-vsctl add-br br-tun')
    cmd('ovs-vsctl add-port br-int patch-int -- set interface patch-int type=patch options:peer=patch-tun')
    cmd('ovs-vsctl add-port br-tun patch-tun -- set interface patch-tun type=patch options:peer=patch-int')


def add_vxlan(hardware, model):
	
    cmd = cmdutil.cmd	
    local_ip = model['local_ip']
    remote_ips = model['remote_ips']

    for remote_ip in remote_ips:
        inf = 'vxlan_' + remote_ip.split('.')[3]
        print '>>> Adding a VXLAN tunnel: ' + inf
        cmd('ovs-vsctl add-port br-tun', inf, '-- set interface', inf, 'type=vxlan options:in_key=flow', 'options:local_ip='+local_ip, 'options:out_key=flow', 'options:remote_ip='+remote_ip)


def add_subnets(hardware, model):
	
    cmd = cmdutil.cmd	
    vid_vni_defaultgw=[]
    for subnet in model: 
        vid = subnet['vid']
        vni = subnet['vni']
        ip_dvr = subnet['ip_dvr']
        ip_vhost = subnet['ip_vhost']
        print '>>> Adding a subnet(vlan): ' + vid
        _add_subnets(hardware=hardware, vid=vid, ip_dvr=ip_dvr, ip_vhost=ip_vhost)
        vid_vni_defaultgw.append([vid, vni, ip_dvr])

    _add_br_tun(vid_vni_defaultgw)


