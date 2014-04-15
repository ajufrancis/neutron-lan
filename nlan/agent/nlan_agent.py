#!/usr/bin/env python

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
import logging

def _init(envfile = 'nlan-env.conf'):

    # Environment setting
    with open(envfile, 'r') as envfile:
        __builtins__.__n__ = eval(envfile.read())

    # Logger
    logger = logging.getLogger("nlan_agent")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    sep = "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
    formatter = logging.Formatter(sep+"\n%(levelname)s %(asctime)s %(funcName)s %(lineno)d, router: "+__n__['router']+"\n%(message)s\n"+sep)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    __n__['logger'] = logger

    # Insert system pathes for the modules
    for f in __n__['mod_dir']:
        ff = os.path.join(__n__['agent_dir'], f)
        sys.path.insert(0, ff)


# Routing a request to a module
def _route(operation, data):
    
    if operation:
        # Calls config modules 
        data = eval(data)
        for func in data.keys():
            __import__(func)
            module = sys.modules[func]
            call = 'module.' + operation
            model = data[func]
            print '+++ ' + func + '.' + operation + ': ' + str(model) 
            print eval(call)(model)
    else:        
        # Calls a command module
        s = data[0].split('.')
        func = '.'.join(s[:-1])
        method = s[-1]
        __import__(func)
        module = sys.modules[func]
        call = 'module.' + method
        args = tuple(data[1:])
        print '+++ ' + func + '.' + method + str(args) 
        print eval(call)(*args)
            


if __name__ == "__main__":

    import sys

    parser = OptionParser()
    parser.add_option("-a", "--add", help="Add elements", action="store_true", default=False)
    parser.add_option("-g", "--get", help="Get elements", action="store_true", default=False)
    parser.add_option("-u", "--update", help="Set elements", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="Delete elements", action="store_true", default=False)
    parser.add_option("-I", "--info", help="set loglevel to INFO", action="store_true", default=False)
    parser.add_option("-D", "--debug", help="set loglevel to DEBUG", action="store_true", default=False)
    parser.add_option("-f", "--envfile", help="Environment file", action="store", type="string", dest="filename")

    (options, args) = parser.parse_args()

    operation = None 
      
    if options.add:
        operation = 'add'
    elif options.get:
        operation = 'get'
    elif options.update:
        operation = 'update'
    elif options.delete:
	operation = 'delete'	

    if options.filename:
        _init(options.filename)
    else:
        _init()

    loglevel = logging.WARNING
    if options.info:
        loglevel = logging.INFO
    elif options.debug:
        loglevel = logging.DEBUG
    __n__['logger'].setLevel(loglevel)
	
    if operation:
        print 'operation: ' + operation
    print 'platform: ' + __n__['platform'] 

    data = None 
    if operation:
        data = sys.stdin.read().replace('"','') 
    else:
        print args
        data = args

    __n__['logger'].info('NLAN Agent initialization completed')

    _route(operation=operation, data=data)

