Modeling and RPC
================

YAML for modeling neutron-lan
=============================

I have learned from SaltStack that YAML is a very simple modeling language.

This is a model that represents neutron-lan:

<pre>
bridges: True
vxlan:
	local_ip: '192.168.57.101'
	remote_ips:
		- '192.168.57.102'
		- '192.168.57.103'
subnets:
	- vid: '1'
	  vni: '101'
	  ip_dvr: '10.0.1.1/24'
	  ip_vhost: '10.0.1.101/24'
	- vid: '3'
	  vni: '103'
	  ip_dvr: '10.0.3.1/24'
	  ip_vhost: '10.0.3.101/24'
</pre>

RPC over SSH for OpenWRT
========================

I'm going to develop a tool to convert YAML data into a Python dictionary object, then issues
a RPC request over SSH to OpenWRT routers.

<pre>
   -----------
  /YAML data/
 -----------
      |
   pyyaml(YAML=>dict)
      |
      V               ----------
   rpc_client.py --- /dict data/ over ssh ---> rpc_server.py
                    -----------
             get, add, set, delete operations
                    
</pre>

The Python dict object will be like this:

<pre>
sample_dict_args = {
'bridges': True,
'vxlan':{
	'local_ip': '192.168.57.101',
	'remote_ips': ['192.168.57.102', '192.168.57.103']
	},
'subnets': [{
	'vid': '1',
	'vni': '101',
	'ip_dvr': '10.0.1.1/24',
	'ip_vhost': '10.0.1.101/24'
	},{
	'vid': '3',
	'vni': '103',
	'ip_dvr': '10.0.3.1/24',
	'ip_vhost': '10.0.3.101/24'
	}]
}
</pre>

If the rpc operation is "add" then rpc_server.py routes rpc calls to the following local methods:
<pre>
def add_bridges(args):
  ...
def add_vxlan(args):
  ...
def add_subnets(args):
  ...
</pre>
