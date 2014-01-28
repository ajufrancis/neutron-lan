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
            option proto 'static'
    #       option ipaddr '192.168.1.1'
    #       option netmask '255.255.255.0'
    #       option ip6assign '60'
     
    config interface 'lan2'
            option ifname 'eth0.3'
            option proto 'static'

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

Disabling IPv6
--------------

I configured br-int and br-tun (w/ VXLAN) on my routers, and everything worked perfect. Next day I turned on my routers and they did not accept neither ping nor ssh. I suspected that IPv6 plug and play caused some loop problem, since I observed a similar problem on OpenWRT/x86/VirtualBox.

Regarding br-int and br-tun, refer to [Inital Config for OpenWRT](https://github.com/alexanderplatz1999/neutron-lan/blob/master/config/config_openwrt1.sh).

IPv6 have been disabled for the time being:

/etc/sysctl.conf

    net.ipv6.conf.all.disable_ipv6 = 1
    net.ipv6.conf.default.disable_ipv6 = 1
    net.ipv6.conf.lo.disable_ipv6 = 1

$ sysctl -p

Installing additional packages
------------------------------

Preparation: use scp to copy openvswitch packages (kmod-* and openvswitch-*) from your openwrt build machine (in my case, Debian Linux VM on VirtualBox) to OpenWRT routers. Then type the following commands: 

    route add default gw 192.168.57.1
    /etc/resolve.conf  nameserver 192.168.57.1
    opkg update
    opkg install ip
    opkg install tcpdump
    opkg install python-mini
    opkg install kmod-openvswitch_3.10.24\+2.0.0-1_ar71xx.ipk
    opkg install openvswitch-common_2.0.0-1_ar71xx.ipk
    opkg install openvswitch-controller_2.0.0-1_ar71xx.ipk
    opkg install openvswitch-switch_2.0.0-1_ar71xx.ipk
    mkdir -p /cgroup
    mount none -t cgroup /cgroup
    opkg install git
    git clone git://github.com/alexanderplatz1999/neutron-lan


After having done all the stuff...
----------------------------------

    root@OpenWrt:~# df
    Filesystem           1K-blocks      Used Available Use% Mounted on
    rootfs                   28544      8668     19876  30% /
    /dev/root                 2816      2816         0 100% /rom
    tmpfs                    30588       548     30040   2% /tmp
    /dev/mtdblock8           28544      8668     19876  30% /overlay
    overlayfs:/overlay       28544      8668     19876  30% /
    tmpfs                      512         0       512   0% /dev
  
