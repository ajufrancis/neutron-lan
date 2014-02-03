#!/usr/bin/python

"""
RPC over SSH
============

This script provides a very simple RPC mechanism over SSH for remote
configuration. rpc_client.py supports [--add], [--get], [--set] and [--delete]
operations with YAML data as an argument. rpc_client.py convert YAML data to
python dictionary data and calls rpc_server.py via SSH. 

rpc_server.py implements add_xxxx(...), get_xxxx(...), set_(...)
and delete_xxxx(...) methods.

   -----------
  /YAML data/
 -----------
      |
   pyyaml(YAML=>dict)
      |
      V               ----------
   rpc_client.py --- /dict data/ over ssh ---> rpc_server.py
                    -----------                               

Usage: python rpc_server.py DICT_ARGS

YAML data example:

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


An example of RPC using salt-ssh:
salt-ssh 'openwrt1' -r "~/rpc_client.py \"{\'add_bridges\':True,\'add_vxlan\':{\'local_ip\':\'192.168.57.101\',\'remote_ips\':[\'192.168.57.102\',\'192.168.57.103\']}}\""

And DICT_ARGS is like the following python dictionary data:
"""
sample_dict_args = {
'add_bridges': True,
'add_vxlan':{
	'local_ip': '192.168.57.101',
	'remote_ips': ['192.168.57.102', '192.168.57.103']
	},
'add_subnets': [{
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

def add_bridges(args):
	print args 
def add_vxlan(args):
	print args
def add_subnets(args):
	print args

# RPC routing
def _route_rpc(kwargs):
	#print kwargs
	for rpc in kwargs.keys():
		func = globals()[rpc]
		args = kwargs[rpc]
		func(args)
                                                                                        
if __name__ == "__main__":

	import sys
      
      	#print sys.argv[1]
	_route_rpc(eval(sys.argv[1]))
	#_route_rpc(sample_dict_args)
	

