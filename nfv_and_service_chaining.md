At first, I am going to try this configuration:

<pre>

               The Internet
                    |
                    | PPPoE
                    |
              [Internet GW]
                    |  ^
                    |  |
                    | RIP
   [S F ]           |  |
    |  |   1002     |  V
 [RPI1    ]----[OpenWRT1]
     |\            /|
     | 1001     103 |     VLAN 1 -- VNI 101
     |    \   101   |     VLAN 3 -- VNI 103
   1001     \/     103
     |     /  \    101    VNI 1001 as a path between SF and OpenWRT2 and 3.
     |   /      \   |     VNI 1002 as a path between SF and OpenWRT1.
     | /   101    \ | 
 [OpenWRT2]----[OpenWRT3]
  | |  | | 103  | |  | |
 Port  Port    Port  Port
 VLAN1 VLAN3   VLAN1 VLAN3

                                       [Service Function] L2 bump in the wire
                                             |    |
                                      VLAN 1 |    | VLAN 2
                                          [  br-int  ]
                                               |
                                               | VLAN 1,2
                                               |
[Host]-- VLAN 1 --[OpenWRT2]-- VNI 1001 --[  br-tun  ]-- VNI 1002 --[OpenWRT1]---[Internet GW]

</pre>

In the ETSI NFV terminology, SF (Service Function) corresponds to VNF(Virtual Network Function).

OpenWRT1 works as a gateway between the Internet and neutron-lan. 
OpenWRT1 uses RIP to advertise networks 10.0.1.0/24 and 10.0.3.0/24 to the Internet GW.

A service function such as firewall or IPS is inserted between the Internet and VLAN 1 (but not VLAN 3) in the L2-bump-in-the-wire mode.

In my experimental setup, any service functions run in Linux Containers (LXC) on a Raspberry Pi Type B machine:

<pre>

          Raspberry Pi
          . . . . . . . . . . . 
          .  [Liux Container] .
          .    |          |   .
          .   veth       veth .
          .    |          |   .
          .  [    br-int    ] .
          .         |         .
          .     VLAN trunk    .
          .         |         . 
          . .[    br-tun    ] .
            (                )
           (    V X L A N     )
            (                )
            

</pre>

