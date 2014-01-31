Software-Defined Networking for neutron-lan
===========================================

neutron-lan-agent and neutron-lan-controller
--------------------------------------------

      +-----------------------------------------------------------+
      |                     html5 browser                         |
      +-----------------------------------------------------------+
                                  | http
                                  V
      +------------------------ wsgi -----------------------------+
      |      neutron-lan-controller (python scripts w/ sqlite2)   |
      |                 Service Abstraction Layer                 |
      +-----------------------------------------------------------+
                                  |
                                  | ssh
                                  V
      +-----------------------------------------------------------+++
      |         neutron-lan-agent (sh and python scripts)         |||
      +-----------------------------------------------------------+++
         |*1     |*2        |*3         |*4       |*5       |*6
         V       V          V           V         V         V
      [links] [bridge] [openvswitch] [routing] [dnsmasq] [iptables]
                                               DNS/DHCP  Firewall/NAT
     *1: iproute2, uci
     *2: brctl
     *3: ovs-vsctl(ovsdb), ovs-ofctl(openflow)
     *4: iproute2
     *5: dnsmasq, uci
     *6: iptables


Details of DVS and DVR
----------------------

neutron-lan is quite different from ordinaly LANs in a sense that:
- Different VLANs can belong to the same VXLAN
- VXLAN may span WAN as well as LAN
- Routing are performed at DVR closest to the host sending packets.

<pre>
Location A                                  Location C
               
VLAN 1 --+---[GW]--+-- VNI 100 -----[GW]---+-- VLAN 23
         |         |                       | 
       [DVR A]     |                     [DVR B]
         |         |                       |
VLAN 3 --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27 
                   |          |
                   |          |
                 [GW]       [GW]
                   |          |
                   +--[DVR C]-+ 
                   |          |
                 VLAN 14    VLAN 15
        
                    Location B
</pre>

Note that VLAN IDs are locally significant, not globally. That is important
from a SDN's point of view.

     
           (Host A)          (Host C)
            Loc. A   Loc. B   Loc. C
            VLAN 1   VLAN 14  VLAN 23
               |       |        |
        +------+       |        |
        |      |       |        |
        |   ---+-------+--------+--- VNI 100
        | 
     [DVR A]                 (Host C')
        |   Loc. A   Loc. B   Loc. C
        |   VLAN 3   VLAN 15  VLAN 27    
        |      |       |        |
        +------+       |        |
               |       |        |
            ---+-------+--------+--- VNI 103
 
Host A on Loc. A VLAN 1 can communicate with Host C on Loc. C VLAN 23
via VXLAN VNI 100.
 
Host A on Loc. A VLAN 1 can communicate with Host C' on Loc. V VLAN 27
via DVR A that has interfaces to both VNI 100 and VNI 103.
 
The controller is responsible for the mapping between VLANs and VNI.

I'm going to study if Proxy ARP is useful for this architecture:
[Virtual Subnet](http://tools.ietf.org/html/draft-xu-l3vpn-virtual-subnet-03).


Logical view of DVS/DVR
-----------------------

     ///Slice of DVS/DVR///

       Location A
       (port-lan) 0..4
            |
            | 10.0.1.1/24
     . . . .|. . . . . .
     .    (router)       .
     .                   . Location C
     .  DVS/DVR  (router)--(port-wan)-------(Internet GW)
     .               |   .
     .               +-----(port-lan)
     .     (router)      .  10.0.1.3/24
      . . . .|. . . . . . 
             | 10.0.1.2/24
             |
        (port-lan) 0..4
        Location B

Legend:
* DVS: Distributed Virtual Switch
* DVR: Distributed Virtual Router
* router: OpenWRT router
* port-lan: LAN port on OpenWRT router
* port-wan: WAN port on OpenWRT router
* Internet GW: In my environment, it corresponds to Home Gateway

Toplogy:
* There are three types of routing topology: dvr(distributed virtual router), centralized(like neutron network node) and ospf that uses legacy routing protocol "ospf".
* L2 topology for "dvr": full mesh or partial mesh VXLAN tunnels with VNI slices.
* L2 topology for "centralized": hub-and-spoke VXLAN tunnels with VNI slices.
* L2 topology for "ospf": arbitrary topologies.


Single DVR IP address for every router
--------------------------------------

Assigning different default GW addresses to distributed routers for same subnet
is not a good strategy. That makes the configuration complicated.

By inserting additional flow entries into br-tun,
all the ARP requests for default GW traversing br-tun can be dropped,
and all the routers can have same IP address as default GW.

This is something openvswitch is very good at: stateless GW processing.

<pre>

     ///Slice of DVS/DVR///
     
       Location A
       (port-lan) 0..4
            |
            | 10.0.1.1/24
     . . . .|. . . . . .
     .    (router)       .
     .                   . Location C
     .  DVS/DVR  (router)--(port-wan)-------(Internet GW)
     .               |   .
     .               +-----(port-lan)
     .     (router)      .  10.0.1.1/24
      . . . .|. . . . . . 
             | 10.0.1.1/24
             |
        (port-lan) 0..4
        Location B

///Before///

Every OpenWRT routers consume different IP addresses for default GW:
Location A: 10.0.1.1/24
Location B: 10.0.1.2/24
Location C: 10.0.1.3/24

///After///

Every OpenWRT routers consume a single IP address for default GW:
Location A: 10.0.1.1/24
Location B: 10.0.1.1/24

///Inserting flow entries into br-tun///

dl_type=0x0806 corresponds to ARP, and in this case nw_dst matches target ip
address in the ARP packet.

  ARP         ARP             (     )
  --->[br-int]-->[br-tun]-X->( VXLAN )
     ARP |          ||        (     )
         V          VV
     10.0.1.1/24   Drops the ARP with target ip = 10.0.1.1
    [default gw]

table 1
+--------------------------------------------+
| matches BC/MC                              | => resubmit(,19)
+--------------------------------------------+
| matches unicast                            | => resubmit(,20)
+--------------------------------------------+

table 19 <== This table will be inserted between table 1 and table 21
+--------------------------------------------+
| dl_type=0x0806, dl_vlan=1, nw_dst=10.0.1.1 | => resubmit(,21)
+--------------------------------------------+
| dl_type-0x0806, nw=dst=10.0.3.1/24         | => resubmit(,21)
+--------------------------------------------+

table 21
+--------------------------------------------+
| BC/MC output flow entries                  |
|              :                             |
+--------------------------------------------+

</pre>

Here is the ovs-ofctl dump-flows after inserting the table 19. You can see that two flow entries of table 19 dropped one ARP packet. Note that the table 20 contains stateful flow entries dynamically created by openvswitch.

<pre>
NXST_FLOW reply (xid=0x4):
 cookie=0x0, duration=875.859s, table=0, n_packets=196, n_bytes=16704, idle_age=97, priority=1,in_port=3 actions=resubmit(,1)
 cookie=0x0, duration=875.852s, table=0, n_packets=170, n_bytes=15824, idle_age=99, priority=1,in_port=1 actions=resubmit(,2)
 cookie=0x0, duration=875.844s, table=0, n_packets=80, n_bytes=7376, idle_age=97, priority=1,in_port=2 actions=resubmit(,2)
 cookie=0x0, duration=875.835s, table=0, n_packets=2, n_bytes=180, idle_age=866, priority=0 actions=drop
 cookie=0x0, duration=875.824s, table=1, n_packets=57, n_bytes=3754, idle_age=102, priority=0,dl_dst=01:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,19)
 cookie=0x0, duration=875.817s, table=1, n_packets=139, n_bytes=12950, idle_age=97, priority=0,dl_dst=00:00:00:00:00:00/01:00:00:00:00:00 actions=resubmit(,20)
 cookie=0x0, duration=875.799s, table=2, n_packets=94, n_bytes=8548, idle_age=112, priority=1,tun_id=0x67 actions=mod_vlan_vid:3,resubmit(,10)
 cookie=0x0, duration=875.808s, table=2, n_packets=120, n_bytes=11064, idle_age=97, priority=1,tun_id=0x64 actions=mod_vlan_vid:1,resubmit(,10)
 cookie=0x0, duration=875.792s, table=2, n_packets=36, n_bytes=3588, idle_age=150, priority=0 actions=drop
 cookie=0x0, duration=875.783s, table=3, n_packets=0, n_bytes=0, idle_age=875, priority=0 actions=drop
 cookie=0x0, duration=875.776s, table=10, n_packets=214, n_bytes=19612, idle_age=97, priority=1 actions=learn(table=20,hard_timeout=300,priority=1,NXM_OF_VLAN_TCI[0..11],NXM_OF_ETH_DST[]=NXM_OF_ETH_SRC[],load:0->NXM_OF_VLAN_TCI[],load:NXM_NX_TUN_ID[]->NXM_NX_TUN_ID[],output:NXM_OF_IN_PORT[]),output:3
 cookie=0x0, duration=875.765s, table=19, n_packets=1, n_bytes=42, idle_age=609, priority=1,arp,dl_vlan=1,arp_tpa=10.0.1.1 actions=drop
 cookie=0x0, duration=875.755s, table=19, n_packets=1, n_bytes=42, idle_age=557, priority=1,arp,dl_vlan=3,arp_tpa=10.0.3.1 actions=drop
 cookie=0x0, duration=875.748s, table=19, n_packets=55, n_bytes=3670, idle_age=102, priority=0 actions=resubmit(,21)
 cookie=0x0, duration=875.735s, table=20, n_packets=1, n_bytes=98, idle_age=117, priority=0 actions=resubmit(,21)
 cookie=0x0, duration=117.94s, table=20, n_packets=1, n_bytes=42, hard_timeout=300, idle_age=112, hard_age=112, priority=1,vlan_tci=0x0003/0x0fff,dl_dst=c2:31:fa:b9:43:fe actions=load:0->NXM_OF_VLAN_TCI[],load:0x67->NXM_NX_TUN_ID[],output:1
 cookie=0x0, duration=149.668s, table=20, n_packets=0, n_bytes=0, hard_timeout=300, idle_age=149, hard_age=140, priority=1,vlan_tci=0x0003/0x0fff,dl_dst=72:7e:16:23:72:d3 actions=load:0->NXM_OF_VLAN_TCI[],load:0x67->NXM_NX_TUN_ID[],output:2
 cookie=0x0, duration=149.685s, table=20, n_packets=0, n_bytes=0, hard_timeout=300, idle_age=149, hard_age=140, priority=1,vlan_tci=0x0001/0x0fff,dl_dst=9e:e0:f6:63:01:ae actions=load:0->NXM_OF_VLAN_TCI[],load:0x64->NXM_NX_TUN_ID[],output:2
 cookie=0x0, duration=149.075s, table=20, n_packets=2, n_bytes=140, hard_timeout=300, idle_age=97, hard_age=97, priority=1,vlan_tci=0x0001/0x0fff,dl_dst=2a:f1:6f:b3:95:d7 actions=load:0->NXM_OF_VLAN_TCI[],load:0x64->NXM_NX_TUN_ID[],output:2
 cookie=0x0, duration=149.645s, table=20, n_packets=0, n_bytes=0, hard_timeout=300, idle_age=149, hard_age=141, priority=1,vlan_tci=0x0003/0x0fff,dl_dst=c6:87:c4:85:76:4b actions=load:0->NXM_OF_VLAN_TCI[],load:0x67->NXM_NX_TUN_ID[],output:2
 cookie=0x0, duration=149.605s, table=20, n_packets=0, n_bytes=0, hard_timeout=300, idle_age=149, hard_age=141, priority=1,vlan_tci=0x0001/0x0fff,dl_dst=2a:c9:c0:7a:2d:0e actions=load:0->NXM_OF_VLAN_TCI[],load:0x64->NXM_NX_TUN_ID[],output:2
 cookie=0x0, duration=149.654s, table=20, n_packets=3, n_bytes=238, hard_timeout=300, idle_age=115, hard_age=115, priority=1,vlan_tci=0x0003/0x0fff,dl_dst=56:d9:17:68:f4:e7 actions=load:0->NXM_OF_VLAN_TCI[],load:0x67->NXM_NX_TUN_ID[],output:2
 cookie=0x0, duration=731.487s, table=20, n_packets=93, n_bytes=8722, hard_timeout=300, idle_age=99, hard_age=98, priority=1,vlan_tci=0x0001/0x0fff,dl_dst=3a:fc:a0:ef:ff:d4 actions=load:0->NXM_OF_VLAN_TCI[],load:0x64->NXM_NX_TUN_ID[],output:1
 cookie=0x0, duration=875.717s, table=21, n_packets=17, n_bytes=1454, idle_age=117, priority=1,dl_vlan=3 actions=strip_vlan,set_tunnel:0x67,output:1,output:2
 cookie=0x0, duration=875.727s, table=21, n_packets=37, n_bytes=2094, idle_age=102, priority=1,dl_vlan=1 actions=strip_vlan,set_tunnel:0x64,output:1,output:2
 cookie=0x0, duration=875.708s, table=21, n_packets=2, n_bytes=220, idle_age=867, priority=0 actions=drop
 </pre>
  
  
Integration with UCI for dnsmasq config
---------------------------------------

uci is short for Unified Configuration Interface. uci is a very useful
tool to configure OpenWRT basic system setting. It is a bit like SNMP
MIB manipulation.

I'm going to develop agents that uses uci for basic system setting on the
OpenWRT router.


Integration with uci for dnsmasq config

<pre>
    DHCP client ---[br1]---[br-int]---[br-tun]---VXLAN
                              | int-vdr1
                              |
                  dnsmasq (DNS/DHCP server)
</pre>

neutron-lan needs to interact with uci to manage dnsmasq by using a script
like this:

<pre>
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
</pre>    

Integration with uci for internal physical sw configuration
-----------------------------------------------------------

Although my routers are cheap, they are not so stupid ones. The internal
physical sw chip is programmable. It is interesting that the sw chip works
like "br-int".

<pre>
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
</pre>

CLI v0.1
--------
<pre>
--- Router object ---
nlan router-alias-set [--ip-addr ADDRESS] ALIAS
nlan router-ssh-set [--box ALIAS] [--user USER] [--password PASSWORD]
nlan router-list

--- Dvs object ---
nlan dvs-vni-create VNI
nlan dvs-pw-create [--router1 ALIAS] [--port1 PORT] [--router2 ALIAS] [--port2 PORT]
nlan dvs-network-add [--vni VNI] NETWORK
nlan dvs-dhcp-add [--vni VNI] OPTIONS
nlan dvs-auth-set ...

--- PortLan object ---
nlan port-lan-set [--router ALIAS] [--port PORT] [--vlan VID] [--vni VNI]
nlan port-tcp-mss-set MSS

--- Router object ---
nlan router-lan-set [--router ALIAS] [--type {dvr, centralized, ospf}] VNILIST
nlan router-wan-set [--router ALIAS] [--protocol {rip, ospf}]

</pre>
