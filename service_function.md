First experiment
----------------

Raspberry Pi is used as Service Function serving DHCP server and IDS capabilities for neutron-lan.

I. DHCP Server 
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

For the time being, DVR A, B and C have direct access too Internet GW (in my case, home gateway).


II. Internet GW

In this configuration, DVR feature is disabled and Raspberry Pi works as a Internet GW.

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


III. IDS in sensor mode

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
         |                       |         |
       [*** *]                   +---+   [DVR C]--- Internet
         |                           |     |
VLAN 3 --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27
                   |          |
                   |          |
                 [GW]       [GW]
                   |          |
                   +--[*** *]-+
                   |          |
                 VLAN 14    VLAN 15

                    Location B

In this configuration, VNI 1001 and VNI 1002 will be used as lables to
identify mirroring ports at Location C. I would need another labels to
identify which traffic goes to which Serivice Function if there were
multiple Service Functions on the Raspberry Pi. 

