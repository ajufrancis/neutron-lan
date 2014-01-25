Initial config for BHR-4GRV
===========================

I've got three [BHR-4GRV](http://buffalo.jp/product/wired-lan/router/bhr-4grv/). I have been trying to setup netron-lan over these routers at home.

The internal network I am trying to create is as follows:

                 (        )
                (  VXLAN   )
                 ( eth0.2 )      
    . . . . . . . [br-tun] . . . . . . . .
    .                |                   .
    .  (vhosts)---[br-int]---(Router)    .
    .              |    |                .
    .          eth0.1 eth0.3             .
    .              |    |       BHR-4GRV .
    .           [ SW ][ SW ]             .
    . . . . . .  |  |  |  |  . . . . . . .
                 p2 p3 p4 p5


Assigning a static IP address to 'wan' port
-------------------------------------------

/etc/config/network

    config interface 'wan'
        option ifname 'eth0.2'
        option proto 'static'
        option ipaddr '192.168.57.101'
        option netmask '255.255.255.0'

(ipaddr) openwrt1: 192.168.57.101, openwrt1: 192.168.57.102, openwrt1: 192.168.57.103

$ /etc/init.d/network restart

Allowing SSH access to 'wan' port
---------------------------------

/etc/config/firewall

    config zone
            option name             wan
            list   network          'wan'
    #       list   network          'wan6'
    #       option input            REJECT
            option input            ACCEPT
            option output           ACCEPT
    #       option forward          REJECT
            option forward          ACCEPT
    #       option masq             1
    #       option mtu_fix          1

    # Allow ssh access from wan
    config rule
            option src              wan
            option dest_port        22
            option target           ACCEPT
            option proto            tcp

$ /etc/init.d/firewall restart

Adding another VLAN to LAN-side ports
-------------------------------------

/etc/config/network

    config interface 'lan'
            option ifname 'eth0.1'
    #       option type 'bridge'
    #       option proto 'static'
    #       option ipaddr '192.168.1.1'
    #       option netmask '255.255.255.0'
    #       option ip6assign '60'
     
    config interface 'lan2'
            option ifname 'eth0.3'
    #       option proto 'static'
    #       option ipaddr '192.168.2.1'
    #       option netmask '255.255.255.0'
            
    config switch
            option name 'switch0'
            option reset '1'
            option enable_vlan '1'
            
    config switch_vlan
            option device 'switch0'
            option vlan '1'
            option ports '0t 2 3'
            
    config switch_vlan
            option device 'switch0'
            option vlan '2'
            option ports '0t 1'
            
    config switch_vlan
            option device 'switch0'
            option vlan '3'
            option ports '0t 4 5'

$ /etc/init.d/network restart

            
/etc/config/firewall

    config zone
            option name             lan2
            list   network          'lan2'
            option input            ACCEPT
            option output           ACCEPT
            option forward          ACCEPT

$ /etc/init.d/firewall restart



