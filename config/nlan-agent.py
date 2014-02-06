#!/usr/bin/python

"""
Local Test
$ python nlan-agent.py --add <<EOF
> {'bridges': 'up', 'vxlan': {'remote_ips': ['192.168.57.102', '192.168.57.103'], 'local_ip': '192.168.57.101'}, 'subnets': [{'ip_dvr': '10.0.1.1/24', 'ip_vhost': '10.0.1.101/24', 'vid': '1', 'vni': '101'}, {'ip_dvr': '10.0.3.1/24', 'ip_vhost': '10.0.3.101/24', 'vid': '3', 'vni': '103'}]}
> EOF
"""
import time

def add_bridges(args):
	print 'add_bridges: ' + str(args) 
	
def add_vxlan(args):
	print 'add_vxlan: ' + str(args)
	
def add_subnets(args):
	print 'add_subnets: ' + str(args)

# Routing a request
def _route(operation, kwargs):
	operation = operation.strip('-')
	for request in kwargs.keys():
		func = globals()[operation+'_'+request]
		args = kwargs[request]
		func(args)
                                                                                        
if __name__ == "__main__":

	import sys
      
      	operation = sys.argv[1]
      	print 'operation: ' + operation
      	data = sys.stdin.read().replace('"','') 
      	dict_args = eval(data)
	_route(operation, dict_args)
	

