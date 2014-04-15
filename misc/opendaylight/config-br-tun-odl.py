#
# config-br-tun.py: 'ovs-ofctl add-flow' script for OpenWRT to set up br-tun as VXLAN GW.
# Usage example: python config-br-tun.py "[[1,1,'10.0.1.1'],[2,2,'10.0.3.1']]".
# [1,1,'10.0.1.1'] means vid=1, vni=1 and defaultgw=10.0.1.1.
#
# Note: flow entries on openvswitch are non-persistent, so you must run this script
#       everytime you reboot the system.
#
# 2014/1/28

import re
import cmdutil

def main(vid_vni_defaultgw):

	output_cmd = cmdutil.output_cmd
	
	patch_tun = ''
	vxlan_ports = []

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
	add_flows(patch_tun, vxlan_ports, vid_vni_defaultgw)
	
	
		
def add_flows(patch_tun, vxlan_ports, vid_vni_defaultgw):

	cmd = cmdutil.check_cmd
	
	cmd('ovs-ofctl del-flows br-tun')

if __name__ == "__main__":
	import sys
	#print sys.argv[1]
	vid_vni_defaultgw = eval(sys.argv[1])
	main(vid_vni_defaultgw)
	
