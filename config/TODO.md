0. UCI

uci is short for Unified Configuration Interface. uci is a very useful
tool to configure OpenWRT basic system setting. It is a bit like SNMP
MIB manipulation.

I'm going to develop agents that uses uci for basic system setting on the
OpenWRT router.


1. Integration with uci for dnsmasq config

    DHCP client ---[br1]---[br-int]---[br-tun]---VXLAN
                              | int-vdr1
                              |
                  dnsmasq (DNS/DHCP server)

neutron-lan needs to interact with uci to manage dnsmasq by using a script
like this:

     def config_dnsmasq(interface, ifname, ipaddr, netmask):
     
	     import cmdutil
     
	     cmd=cmdutil.check_cmd
     	     network_dvr='network.'+interface
     
	     cmd('uci set', network_dvr+'=interface')
	     cmd('uci set', network_dvr+'.ifname='+ifname)
	     cmd('uci set', network_dvr+'.proto=static')
	     cmd('uci set', network_dvr+'.ipaddr='+ipaddr)
	     cmd('uci set', network_dvr+'.netmask='+netmask)
     
	     cmd('uci set dhcp.lan.interface='+interface)
     
	     cmd('uci commit')
     
	     cmd('/etc/init.d/dnsmasq restart')
     
I need to figure out how to run multiple dnsmasq instances in parallel, since
I'm going to configure multiple VLANs on my routers.


2. Integration with uci for internal physical sw configuration.

Although my routers are cheap, they are not so stupid ones. The internal
physical sw chip is programmable. It is interesting that the sw chip works
like "br-int".

      programmable
      physical sw           CPU(MIPS)
        +---+                 +---+
     ---|   |                 |   |
     ---|   |                 |   |
     ---|   |----VLAN trunk---|   |
     ---|   |                 |   |
     ---|   |                 |   |
        +---+                 +---+
                                :
                                :
                              WiFi <= My router do not have WiFi...


neutron-lan needs to modify values of the following UCI pathes: 
* network.switch
* network.switch_vlan

; then
/etc/init.d/network restart

