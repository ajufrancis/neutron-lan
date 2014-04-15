if [ "$1" != "reboot" ]; then
	# Add br-int and br-tun
	ovs-vsctl add-br br-int
	ovs-vsctl add-br br-tun
	
	# br-tun: add vxlan ports
	ovs-vsctl add-port br-tun vxlan101 -- set interface vxlan101 type=vxlan options:local_ip=192.168.57.102 options:remote_ip=192.168.57.101
	ovs-vsctl add-port br-tun vxlan103 -- set interface vxlan103 type=vxlan options:local_ip=192.168.57.102 options:remote_ip=192.168.57.103

	# Add patch interface between br-int and br-tun
	ovs-vsctl add-port br-int patch-int -- set interface patch-int type=patch options:peer=patch-tun
	ovs-vsctl add-port br-tun patch-tun -- set interface patch-tun type=patch options:peer=patch-int
	
	ovs-vsctl set-controller br-tun tcp:192.168.57.128:6633
fi

# VLAN-related config.
if [ "$1" == "reboot" ]; then
	python config-vlan-odl.py 1 10.0.1.2/24 10.0.1.102/24 reboot
else
	python config-vlan-odl.py 1 10.0.1.2/24 10.0.1.102/24
fi

# Add OF flow entries proactiely to br-tun to make it work as VXLAN GW. 
# vid:1<=>vni:100
python ./config-br-tun-odl.py "[[1,100,'10.0.1.2']]"

