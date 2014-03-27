#!/usr/bin/python

"""
This "nlan-agent.py" works as a remote agent, accepting requests from
"nlan-ssh.py" and invoking modules depending on the input data.

Local Test
$ python nlan-agent.py --update <<EOF
"OrderedDict([('subnets', {'@vni:101': {'vid': '5'}})])"
> EOF
$ python nlan-agent.py --update "OrderedDict([('subnets', {'@vni:101': {'vid': '5'}})])"
$ python nlan-agent.py --update "{'subnets': {'@vni:101': {'vid': 5}}}"
"""
import os, sys, time
from optparse import OptionParser
from collections import OrderedDict

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

# Routing a request to a module
def _route(platform, operation, data):
   
    if operation == '':
        # Calls a command module
        s = data[0].split('.')
        func = s[0]
        method = s[1]
        __import__(func)
        module = sys.modules[func]
        call = 'module.' + method
        l = [platform]
        l.extend(data[1:])
        args = tuple(l)
        print '+++ ' + func + '.' + method + str(args) 
        eval(call)(*args)
    else:
        # Calls config modules 
        data = eval(data)
        for func in data.keys():
            __import__(func)
            module = sys.modules[func]
            call = 'module.' + operation
            model = data[func]
            print '+++ ' + func + '.' + operation + ': ' + str(model) 
            eval(call)(platform, model)

            
if __name__ == "__main__":

    import sys

    parser = OptionParser()
    parser.add_option("-a", "--add", help="Add elements", action="store_true", default=False)
    parser.add_option("-g", "--get", help="Get elements", action="store_true", default=False)
    parser.add_option("-u", "--update", help="Set elements", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="Delete elements", action="store_true", default=False)
    parser.add_option("-p", "--platform", help="Platform(e.g., bhr_4grv or raspberry_pi_b)", action="store", default=False)

    (options, args) = parser.parse_args()

    operation = ''
      
    if options.add:
        operation = 'add'
    elif options.get:
        operation = 'get'
    elif options.update:
        operation = 'update'
    elif options.delete:
	operation = 'delete'	
	
    platform = options.platform
    dict_args = {}

    print 'operation: ' + operation
    print 'platform: ' + platform 
    data = ''
    if operation == '':
        data = args
    else:
        data = sys.stdin.read().replace('"','') 

    _route(platform=platform, operation=operation, data=data)
	

