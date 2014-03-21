#!/usr/bin/python

"""
This "nlan-agent.py" works as a remote agent, accepting requests from
"nlan-ssh.py" and invoking modules depending on the input data.

Local Test
$ python nlan-agent.py --add <<EOF
> {'bridges': 'up', 'vxlan': {'remote_ips': ['192.168.57.102', '192.168.57.103'], 'local_ip': '192.168.57.101'}, 'subnets': [{'ip_dvr': '10.0.1.1/24', 'ip_vhost': '10.0.1.101/24', 'vid': '1', 'vni': '101'}, {'ip_dvr': '10.0.3.1/24', 'ip_vhost': '10.0.3.101/24', 'vid': '3', 'vni': '103'}]}
> EOF
"""
import os, sys, time
from optparse import OptionParser

NLAN_AGENT_DIR = '/tmp'

# Obtain a module list from nlan-modlist.txt
with open(os.path.join(NLAN_AGENT_DIR, 'nlan-modlist.txt'), 'r') as modfile:
    modlist = modfile.read()
    modlist = eval(modlist)

# Insert system pathes for the modules
dirs = os.listdir(NLAN_AGENT_DIR)
for f in dirs:
        ff = os.path.join(NLAN_AGENT_DIR, f)
        if os.path.isdir(ff) and f in modlist:
            sys.path.insert(0, ff)

# Import a command module "init"
import init

# Routing a request to a module
def _route(platform, operation, kwargs):
   
    # Call a command module "init"
    if operation == 'init':
        print '+++ init:' 
        init.run(platform)
    else:
        # Call config modules 
        for func in kwargs.keys():
            __import__(func)
            module = sys.modules[func]
            call = 'module.' + operation
            args = kwargs[func]
            print '+++ ' + func + '.' + operation + ': ' + str(args) 
            eval(call)(platform, args)

            
if __name__ == "__main__":

    import sys

    parser = OptionParser()
    parser.add_option("-a", "--add", help="Add elements", action="store_true", default=False)
    parser.add_option("-g", "--get", help="Get elements", action="store_true", default=False)
    parser.add_option("-u", "--update", help="Set elements", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="Delete elements", action="store_true", default=False)
    parser.add_option("-p", "--platform", help="Platform(e.g., bhr_4grv or raspberry_pi_b)", action="store", default=False)
    parser.add_option("-i", "--init", help="Initalization", action="store_true", default=False)

    (options, args) = parser.parse_args()

    operation = ''
      
    if options.add:
        operation = 'add'
    elif options.get:
        operation = 'get'
    elif options.update:
        operetaion = 'update'
    elif options.delete:
	operation = 'delete'	
    elif options.init:
        operation = 'init'
	
    platform = options.platform
    dict_args = {}

    print 'operation: ' + operation
    print 'platform: ' + platform 
    if operation == 'init':
        pass
    else:
        data = sys.stdin.read().replace('"','') 
        dict_args = eval(data)

    _route(platform=platform, operation=operation, kwargs=dict_args)
	

