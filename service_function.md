Raspberry Pi is used as Service Function serving DHCP server and IDS/IPS capabilities for neutron-lan.

I. DHCP Server 
--------------
<pre>
                 +----------------+
                 |Service Function| DHCP Server 
                 +----------------+                   
                 int-sf1    int-sf3
                    |          |
                  [GW]       [GW]
Location A          |          |              Location C
                    |          |
VLAN 1 --+---[GW]--++- VNI 100 -----[GW]---+-- VLAN 23
         |         |           |           |
       [DVR A]     |           |         [DVR C]
         |         |           |           |
VLAN 3 --+---[GW]--- VNI 103 -++----[GW]---+-- VLAN 27
                   |          |
                   |          |
                 [GW]       [GW]
                   |          |
                   +--[DVR B]-+
                   |          |
                 VLAN 14    VLAN 15

                    Location B
</pre>

For the time being, DVR A, B and C have direct access too Internet GW (in my case, home gateway).


II. Internet GW
---------------
In this configuration, DVR feature is disabled and Raspberry Pi works as a Internet GW.
<pre>
                     Internet
                         |
                 +----------------+
                 |Service Function| Internet GW 
                 +----------------+ NAPT, dnsmasq(DHCP), Snort(IPS inline-mode)
                 int-sf1    int-sf3
                    |          |
                  [GW]       [GW]
Location A          |          |              Location C
                    |          |
VLAN 1 --+---[GW]--++- VNI 100 -----[GW]---+-- VLAN 23
         |         |           |           |
       [*** *]     |           |         [*** *]
         |         |           |           |
VLAN 3 --+---[GW]--- VNI 103 -++----[GW]---+-- VLAN 27
                   |          |
                   |          |
                 [GW]       [GW]
                   |          |
                   +--[*** *]-+
                   |          |
                 VLAN 14    VLAN 15

                    Location B 
</pre>

III. IDS in sensor mode
-----------------------
<pre>
                 +----------------+
                 |Service Function| Snort(IDS sensor-mode)
                 +----------------+
                 int-sf1    int-sf3
                    |          |
                  [GW]       [GW]
                    |          |
                 VNI 103    VNI 100
                    |          |
Location A          |          +-----+   Location C
                    +------------+   |
VLAN 1 --+---[GW]--+-- VNI 100 --|--[GW]---+-- VLAN 23
         |         |             |         |
       [*** *]     |             +---+   [DVR C]--- Internet
         |         |                 |     |
VLAN 3 --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27
                   |          |
                   |          |
                 [GW]       [GW]
                   |          |
                   +--[*** *]-+
                   |          |
                 VLAN 14    VLAN 15

                    Location B
</pre>


IV. Firewall/IPS in L2-bump-in-the-wire mode
--------------------------------------------
<pre>
                 +----------------+
                 |Service Function| Snort(inline IPS mode)
                 +----------------+
                 int-sf1    int-sf2
                    |          |
                  [GW]       [GW]
                    |          |
                 VNI 1001    VNI 1002
                    |          |
Location A     +----+--+       +-----+   Location C
               |       |             |
VLAN 1 --+---[GW]--+---| VNI 100 ---[GW]---+-- VLAN 23
         |         |   |                   |      RIP
       [*** *]     |   |                 [DVR C]--------[Internet GW]
         |         |   |                   |     
VLAN 3 --+---[GW]------|--VNI 103---[GW]---+-- VLAN 27
                   |   |      |
                   |   |      |
                  [GW]-+     [GW]
                   |          |
                   +--[*** *]-+
                   |          |
                 VLAN 14    VLAN 15

                    Location B
</pre>
