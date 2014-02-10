# 2014/2/10
# dvsdvr.py
#

import cmdutil

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
		inf = 'vxlan_'+remote_ip
		print '>>> Adding a VXLAN tunnel: ' + inf
		cmd('ovs-vsctl add-port br-tun', inf, '-- set interface', inf, 'type=vxlan options:in_key=flow', 'options:local_ip='+local_ip, 'options:out_key=flow', 'options:remote_ip='+remote_ip)


def add_subnets(hardware, model):
	
	cmd = cmdutil.cmd	
	for subnet in model: 
		vid = subnet['vid']
		ip_dvr = subnet['ip_dvr']
		ip_vhost = subnet['ip_vhost']
		print '>>> Adding a subnet(vlan): ' + vid
		_add_subnets(hardware, vid, ip_dvr, ip_vhost)


"""
if [ "$1" != "reboot" ]; then
	# Add br-int and br-tun
	ovs-vsctl add-br br-int
	ovs-vsctl add-br br-tun
	
	# br-tun: add vxlan ports
	ovs-vsctl add-port br-tun vxlan102 -- set interface vxlan102 type=vxlan options:in_key=flow options:local_ip=192.168.1.101 options:out_key=flow  options:remote_ip=192.168.1.102
	ovs-vsctl add-port br-tun vxlan103 -- set interface vxlan103 type=vxlan options:in_key=flow options:local_ip=192.168.1.101 options:out_key=flow  options:remote_ip=192.168.1.103
	ovs-vsctl add-port br-tun vxlan104 -- set interface vxlan104 type=vxlan options:in_key=flow options:local_ip=192.168.1.101 options:out_key=flow  options:remote_ip=192.168.1.104

	# Add patch interface between br-int and br-tun
	ovs-vsctl add-port br-int patch-int -- set interface patch-int type=patch options:peer=patch-tun
	ovs-vsctl add-port br-tun patch-tun -- set interface patch-tun type=patch options:peer=patch-int
fi

# VLAN-related config.
if [ "$1" == "reboot" ]; then
	python config-vlan.py $model 1 10.0.1.1/24 10.0.1.101/24 reboot
	python config-vlan.py $model 3 10.0.3.1/24 10.0.3.101/24 reboot 
else
	python config-vlan.py $model 1 10.0.1.1/24 10.0.1.101/24
	python config-vlan.py $model 3 10.0.3.1/24 10.0.3.101/24
fi

# Add OF flow entries proactiely to br-tun to make it work as VXLAN GW. 
# vid:1<=>vni:100, vid:3<=>vni:103
python ./config-br-tun.py "[[1,100,'10.0.1.1'],[3,103,'10.0.3.1']]"
"""
