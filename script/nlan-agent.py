#!/usr/bin/python

"""
Local Test
$ python nlan-agent.py --add <<EOF
> {'bridges': 'up', 'vxlan': {'remote_ips': ['192.168.57.102', '192.168.57.103'], 'local_ip': '192.168.57.101'}, 'subnets': [{'ip_dvr': '10.0.1.1/24', 'ip_vhost': '10.0.1.101/24', 'vid': '1', 'vni': '101'}, {'ip_dvr': '10.0.3.1/24', 'ip_vhost': '10.0.3.101/24', 'vid': '3', 'vni': '103'}]}
> EOF
"""
import time
from optparse import OptionParser

import dvsdvr

def init(hardware):
    dvsdvr.init(hardware)

def add_bridges(hardware, args):
    print 'add_bridges: ' + str(args) 
    dvsdvr.add_bridges(hardware, args)
	
def add_vxlan(hardware, args):
    print 'add_vxlan: ' + str(args)
    dvsdvr.add_vxlan(hardware, args)
	
def add_subnets(hardware, args):
    print 'add_subnets: ' + str(args)
    dvsdvr.add_subnets(hardware, args)

# Routing a request
def _route(hardware, operation, kwargs):
    
    if operation == 'init':
        init(hardware)
    else:
        for request in kwargs.keys():
            func = globals()[operation+'_'+request]
            args = kwargs[request]
            func(hardware, args)
                                                                                        
if __name__ == "__main__":

    import sys

    parser = OptionParser()
    parser.add_option("-a", "--add", help="Add an element", action="store_true", default=False)
    parser.add_option("-g", "--get", help="Get an element", action="store_true", default=False)
    parser.add_option("-s", "--set", help="Set an element", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="Delete an element", action="store_true", default=False)
    parser.add_option("-t", "--type", help="Hardware type(e.g., bhr_4grv or raspberry_pi_b", action="store", default=False)
    parser.add_option("-i", "--init", help="Initalization", action="store_true", default=False)

    (options, args) = parser.parse_args()

    operation = ''
      
    if options.add:
        operation = 'add'
    elif options.get:
        operation = 'get'
    elif options.set:
        operetaion = 'set'
    elif options.delete:
	operation = 'delete'	
    elif options.init:
        operation = 'init'
	
    hardware = options.type
    dict_args = {}

    print 'operation: ' + operation
    print 'hardware: ' + hardware 
    if operaion == 'init':
        pass
    else:
        data = sys.stdin.read().replace('"','') 
        dict_args = eval(data)

    _route(hardware=hardware, operation=operation, kwargs=dict_args)
	

