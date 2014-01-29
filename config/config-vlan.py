#
# config-vlan.py: vlan-related configuration script for OpenWRT.
# Usage example: python config-vlan.py 1 10.0.1.1/24 10.0.1.101/24
# In case of non_persistent==True, this script only configure the non-persitent part. 
#
# 2014/1/29

import re
import cmdutil

def main(vid, ip_dvr, ip_vhost, reboot=False):

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
	if reboot == False :
		cmd('ovs-vsctl add-port br-int', int_br, 'tag='+vid, '-- set interface', int_br, 'type=internal')	
		cmd('ovs-vsctl add-port br-int', int_dvr, 'tag='+vid, '-- set interface', int_dvr, 'type=internal')
	cmd('brctl addif', br, eth0_vid)
	cmd('brctl addif', br, veth_ns)
	cmd('brctl addif', br, int_br)
	cmd('ip addr add dev', int_dvr, ip_vhost)
	cmd('ip link set dev', veth_ns, 'promisc on')
	cmd('ip link set dev', veth_ns, 'up')
	#cmd('ip netns exec', ns, 'ip link set dev eth0 promisc on')
	cmd('ip netns exec', ns, 'ip link set dev eth0 up')
	cmd('ip link set dev', int_br, 'promisc on')
	cmd('ip link set dev', int_br, 'up')
	#cmd('ip link set dev', int_dvr, 'promisc on')
	cmd('ip link set dev', int_dvr, 'up')
	cmd('ip link set dev', br, 'up')
		
if __name__ == "__main__":

	import sys
	
	reboot = False
	if len(sys.argv) == 5 and (sys.argv[4]=='reboot'):
		reboot = True	

	main(vid=sys.argv[1], ip_dvr=sys.argv[2], ip_vhost=sys.argv[3], reboot=reboot)

	
