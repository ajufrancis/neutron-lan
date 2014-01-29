#
# config-br-tun.py: 'ovs-ofctl add-flow' script for OpenWRT to set up br-tun as VXLAN GW.
# Usage example: python config-br-tun.py [[1,1],[2,2]].
# The first argument is a list of vid vni pairs:
# [1,1] means vid 1 and vni 1, [1,2] means vid 1 and vni 2
#
# Note: flow entries on openvswitch are non-persistent, so you must run this script
#       everytime you reboot the system.
#
# 2014/1/28

import re
import cmdutil

def main(vid_vni_pairs):

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
	for pair in vid_vni_pairs:
		pair[0] = str(pair[0])
		pair[1] = str(pair[1])
	#print patch_tun
	#print vxlan_ports
	#print vid_vni_pairs
	add_flows(patch_tun, vxlan_ports, vid_vni_pairs)
	
	
		
def add_flows(patch_tun, vxlan_ports, vid_vni_pairs):

	cmd = cmdutil.check_cmd
	
	cmd('ovs-ofctl del-flows br-tun')
	cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=1,in_port='+patch_tun+',actions=resubmit(,1)')
	for vxlan_port in vxlan_ports:
		cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=1,in_port='+vxlan_port+',actions=resubmit(,2)')
	cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=0,actions=drop')	
	cmd('ovs-ofctl add-flow br-tun', 'table=1,priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00,actions=resubmit(,21)')
	cmd('ovs-ofctl add-flow br-tun', 'table=1,priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00,actions=resubmit(,20)')
	for pair in vid_vni_pairs:
		vid = pair[0]
		vni = pair[1]
		cmd('ovs-ofctl add-flow br-tun', 'table=2,priority=1,tun_id='+vni+',actions=mod_vlan_vid:'+vid+',resubmit(,10)')
	cmd('ovs-ofctl add-flow br-tun', 'table=2,priority=0,actions=drop')
	cmd('ovs-ofctl add-flow br-tun', 'table=3,priority=0,actions=drop')
	cmd('ovs-ofctl add-flow br-tun', 'table=10,priority=1,actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:'+patch_tun)
	cmd('ovs-ofctl add-flow br-tun', 'table=20,priority=0,actions=resubmit(,21)')
	output_ports = ''
	for vxlan_port in vxlan_ports:
		output_ports = output_ports+',output:'+vxlan_port
	for pair in vid_vni_pairs:
		vid = pair[0]
		vni = pair[1]
		cmd('ovs-ofctl add-flow br-tun', 'table=21,priority=1,dl_vlan='+vid+',actions=strip_vlan,set_tunnel:'+vni+output_ports)
	cmd('ovs-ofctl add-flow br-tun', 'table=21,priority=0,actions=drop')
		

if __name__ == "__main__":
	import sys
	vid_vni_pairs = eval(sys.argv[1])
	main(vid_vni_pairs)
	
