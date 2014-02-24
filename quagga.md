Working with Quagga
===================

How can I controll my Netgear router (WGU624) from my SDN controller?
The router seems to support RIPv1 and RIPv2 for the LAN ports, 
so I install Quagga on OpenWRT1 to make it exchange routing info with the Netgear router.

        The Internet
             |
             |
      [Netgear router] as Internet GW
             ^
             |
            RIP to advertise routing info
             |
      [ OpenWRT1     ] <===== the controller manipulates Quagga on the router.

<pre>
root@OpenWrt:/etc# opkg install quagga-ripd
Installing quagga-ripd (0.99.22.3-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/quagga-ripd_0.99.22.3-1_ar71xx.ipk.
Installing quagga (0.99.22.3-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/quagga_0.99.22.3-1_ar71xx.ipk.
Installing quagga-libzebra (0.99.22.3-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/quagga-libzebra_0.99.22.3-1_ar71xx.ipk.
Configuring quagga.
Configuring quagga-libzebra.
Configuring quagga-ripd.

root@OpenWrt:/etc# opkg install quagga-vtysh
Installing quagga-vtysh (0.99.22.3-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/quagga-vtysh_0.99.22.3-1_ar71xx.ipk.
Installing libreadline (6.2-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/libreadline_6.2-1_ar71xx.ipk.
Installing libncurses (5.9-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/libncurses_5.9-1_ar71xx.ipk.
Installing terminfo (5.9-1) to root...
Downloading http://downloads.openwrt.org/snapshots/trunk/ar71xx/packages/terminfo_5.9-1_ar71xx.ipk.
Configuring terminfo.
Configuring libreadline.
Configuring libncurses.
Configuring quagga-vtysh.
</pre>

I have intalled the quagga-ripd and quagga-btysh packages on OpenWRT1. Then I try to use vtysh:

<pre>
root@OpenWrt:~# /etc/init.d/quagga start
quagga.init: Starting ripd ... done.
root@OpenWrt:~# vtysh

Hello, this is Quagga (version 0.99.22.3).
Copyright 1996-2005 Kunihiro Ishiguro, et al.

OpenWrt# configure terminal
OpenWrt(config)# router rip
OpenWrt(config-router)#
</pre>



