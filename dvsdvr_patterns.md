Location A                                  Location C

VLAN 1 --+---[GW]--+-- VNI 100 -----[GW]---+-- VLAN 23
         |         |                       |
       [DVR A]     |                     [DVR C]
         |         |                       |
VLAN 3 --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27
                   |          |
                   |          |
                 [GW]       [GW]
                   |          |
                   +--[DVR B]-+
                   |          |
                 VLAN 14    VLAN 15

                    Location B


Location A                                  Location C

VLAN 1 --+---[GW]--+-- VNI 100 -----[GW]---+-- VLAN 23
         |         |                       |
       [DVR A]     |                     [DVR C]
         |         |                       |
     X --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27
                   |          |
                   |          |
                 [GW]       [GW]
                   |          |
                   +--[DVR B]-+
                   |          |
                   X        VLAN 15

                    Location B


Location A                                  Location C

VLAN 1 --+---[GW]--+-- VNI 100 -----[GW]---+-- VLAN 23
         |         |                       |                 (        )
       [DVR A]-[GW]------+--VNI 1--------[DVR C]--[FW/NAT]--( Internet )
         |         |     |                 |                 (        )
VLAN 3 --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27
                   |     |    |
                   |     |    |
                 [GW]  [GW] [GW]
                   |     |    |
                   +--[DVR B]-+
                   |          |
                 VLAN 14    VLAN 15

                    Location B


Location A                                  Location C

VLAN 1 --+---[GW]--+-- VNI 100 -----[GW]---+-- VLAN 23
         |         |                       |
       [DVR A]     |                     [DVR C]
         | |       |                       | |
VLAN 3 --+---[GW]--- VNI 103 -+-----[GW]---+-- VLAN 27
           |       |          |              |
       [FW/NAT]    |          |          [FW/NAT]
           |     [GW]       [GW]             |
           |       |          |              |
           V       +--[DVR B]-+              V
       Internet    |          |          Internet
                 VLAN 14    VLAN 15

                    Location B
