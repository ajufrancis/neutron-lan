
The neutron-lan architecture assumes that all the routers are sort of linux-based mini server machines (such as
OpenWRT) and all the routing tables or flow tables on the routers are automatically configured by the lan-controller
via common southboud APIs. Every router supports linux routing, linux bridge, openvswitch, iptables,
network namespaces, veth, tap etc and all the capabilites are manages by using common CLIs and common southbouhd APIs.

The lan controller needs to communicate with the wan controller via NaaS APIs to create a VPLS network among
head quarters, branch offices and private/public cloud networks.

   [lan-controller] --- NaaS APIs ---> [wan-controller]
           |          (REST APIs)              |
           V                                   V
   (             )                    (               )      
  (  neutron-lan  )                  (       VPLS      )
   (             )                     (              )


Or another model is that a service provider hosts the lan controller on behalf or the user.

           +-----------[lan-controller][wan-controller]
           |                                   |
           V                                   V
     neutron-lan                              VPLS

Since BHR-4GRV does not support VLAN trunk on WAN port, it is not possible to use VPLS as a WAN backbone network.
