Extending the scope to WAN
==========================

"LAN-WAN seamless" basic concept
--------------------------------

The neutron-lan architecture assumes that all the routers are sort of linux-based mini server machines (such as OpenWRT) and all the routing tables or flow tables on the routers are automatically configured by the lan-controller via common southboud APIs. Every router supports basic network funcions such as linux routing, linux bridge, openvswitch, iptables, dnsmasq, tc, network namespaces, veth, tap etc, and all the network functions are manages by using common CLIs and common southbouhd APIs.

On the other hand, the architecture outsources a WAN backbone network to some service provider(s). To set up a WAN backbone, (a) the lan-controller issues a request to NaaS API server to create a MPLS-based VPN network, (b) the lan-controller sets up GRE over IPsec tunnels (or VXLAN tunnels with some new authentfication/encryption support) among access routers (linux-based machines), or (c) the neutron-lan uses a legacy routing protocol such as OSPF or BGP to exchange routing info with the CPE or with the PE router (or just static routing).


Network functions and serivce chaining
--------------------------------------

The access routers may support optional network functions such as IDS/IPS(e.g., snort). Such additional functions may reside in network namespaces (netns) or linux containers (LXC), or may be "physical" appliances. Service chaining between network functions are realized with either linux-internal net working links such as veth, or physical links (802.1q).

     Service chaining examples:
     
     [bridge]--veth--[snort]--veth--[bridge]
      
                  netns
                  . . . . . . . .
                  .             .
     [bridge]--veth--[dnsmasq]  .
                  . . . . . . . .
      
                  Physical appliance
     [bridge]--802.1q--[IDS/IPS]--802.1q--[bridge]


To divert a specific traffic, either linux policy-based routing or openflow-based traffic steering with openvswitch is exploited.

             +-----------> Diverted traffic
             |
     ------(PBR)--------->
      
              +----------> Diverted traffic
              |
     ---(openvswitch)---->


Working with MPLS-based VPN
---------------------------

The lan controller needs to communicate with the wan controller via NaaS APIs to create a WAN backbone network among
head quarters, branch offices and private/public cloud networks.

     [lan-controller] --- NaaS APIs ---> [wan-controller]
             |          (REST APIs)              |
             |                                   |
             | Southbound APIs                   | Southbound APIs
             V                                   V
      (             )   VLAN trunk       (               )      
     (  neutron-lan  )==================(  MPLS-based VPN )
      (             )                     (              )


Or another model is that a service provider hosts the lan controller on behalf or the user.

             +-----------[lan-controller][wan-controller]
             |                                   |
             |                                   |
             | Southbound APIs                   | Southbound APIs
             V                                   V
      (             )   VLAN trunk       (               )      
     (  neutron-lan  )==================(  MPLS-based VPN )
      (             )                     (              )

Since my routers (BHR-4GRV) does not support VLAN trunk on WAN port, it is not possible to work with VPLS. I will need to buy other linux machines (either x86 cpu or arm cpu) and use them as access routers supporting VLAN trunk.

      [lan-controller]-------------------------------+
       |       | NaaS APIs                           |
       |       +------>[wan-controller]              |
       |                       |                     |
       |                       V                     |
       |     VLAN trunk   (        )  VLAN trunk     |
       |     +---------- (   VPLS   )----------+     |
       |     |            (        )           |     |
       |     |                                 |     |
       V     | Access Router     Access Router |     V
     . . . . | . . . .                 . . . . | . . . .
     .    [br-eth]   .                 .    [br-eth]   .
     .       |       .                 .       |       .
     .    (Router)   .                 .    (Router)   .
     .       |       .                 .       |       .
     .    [br-int]   .                 .    [br-int]   .
     .       |       .                 .       |       .
     . . .[br-tun] . .                 . . .[br-tun] . .
         (        )                        (        )
        (  VLAN    )                      (  VXLAN   )
         (        )                        (        )

