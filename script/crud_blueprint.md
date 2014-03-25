nlan CRUD operations blueprint
------------------------------
2014/3/25

yamldiff.py outputs CRUD operations like this:
['rpi1', '--update', "{'vxlan': {'remote_ips': ['192.168.1.101', '192.168.1.102']}}"]
['openwrt3', '--update', "{'subnets': {'@vni:103': {'ports': ['eth0.3', 'veth0.3']}}}"]
['openwrt2', '--delete', "{'subnets': {'@vni:101': {'ip_dvr': '10.0.1.1/24', 'ip_vhost': '10.0.1.102/24', 'vid': '1', 'vni': '101', 'ports': ['eth0.1']}}}"]
['openwrt2', '--add', "{'subnets': {'@vni:111': {'ip_dvr': '10.0.1.1/24', 'ip_vhost': '10.0.1.102/24', 'vid': '1', 'vni': '111', 'ports': ['eth0.1']}}}"]
['openwrt1', '--delete', "{'bridges': {'controller': '192.168.1.1:6633'}}"]

nlan-master.py sends the CRUD operations to nlan-agent.py by executing nlan-ssh.py for each CRUD operation:
<pre>
$ python nlan-ssh.py rpi1 --update "{'vxlan': {'remote_ips': ['192.168.1.101', '192.168.1.102']}}"
$ python nlan-ssh.py openwrt3 --update "{'subnets': {'@vni:103': {'ports': ['eth0.3', 'veth0.3']}}}"
$ python nlan-ssh.py, openwrt2 --delete "{'subnets': {'@vni:101': {'ip_dvr': '10.0.1.1/24', 'ip_vhost': '10.0.1.102/24', 'vid': '1', 'vni': '101', 'ports': ['eth0.1']}}}"
$ python nlan-ssh.py, openwrt2 --add "{'subnets': {'@vni:111': {'ip_dvr': '10.0.1.1/24', 'ip_vhost': '10.0.1.102/24', 'vid': '1', 'vni': '111', 'ports': ['eth0.1']}}}"
$ python nlan-ssh.py, openwrt1 --update "{'subnets': {'@vni:103': {'ports': ['eth0.3', 'veth0.3']}, '@vni:101': {'ports': ['eth0.1', 'veth0.1']}}}"
$ python nlan-ssh.py, openwrt1 --delete "{'bridges': {'controller': '192.168.1.1:6633'}}"
</pre>

The keys starting with '@' represent indexes of input parameters. For example, "@vni:103" represents a list of input parameters that belong to vni 103.

