Initial config for BHR-4GRV
===========================

Assigning a static IP address to 'wan' port
-------------------------------------------

/etc/config/network

    config interface 'wan'
        option ifname 'eth0.2'
        option proto 'static'
        option ipaddr '192.168.57.101'
        option netmask '255.255.255.0'

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


