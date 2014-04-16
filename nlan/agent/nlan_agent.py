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
import cStringIO

out = cStringIO.StringIO()

def _init(envfile = 'nlan_env.conf'):

    # Environment setting
    with open(envfile, 'r') as envfile:
        __builtins__.__n__ = eval(envfile.read())

    logger = logging.getLogger("nlan_agent")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(out)
    handler.setLevel(logging.DEBUG)
    header = "[%(levelname)s] module:%(module)s,function:%(funcName)s,router: {}".format(__n__['router'])
    formatter = logging.Formatter(header+"\n%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
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
            __n__['logger'].info('function:{0}.{1}, model:{2}'.format(func, operation, str(model)))
            result = eval(call)(model)
            if result:
                print result
    else:        
        # Calls a command module
        s = data[0].split('.')
        func = '.'.join(s[:-1])
        method = s[-1]
        __import__(func)
        module = sys.modules[func]
        call = 'module.' + method
        args = tuple(data[1:])
        __n__['logger'].info('function:{0}.{1}, args:{2}'.format(func, method, str(args)))
        result = eval(call)(*args)
        if result:
            print result

    log = out.getvalue()
    if log != '':
        print log
    out.close()


if __name__ == "__main__":

    import sys

    parser = OptionParser()
    parser.add_option("-a", "--add", help="add NLAN states", action="store_true", default=False)
    parser.add_option("-g", "--get", help="get NLAN states", action="store_true", default=False)
    parser.add_option("-u", "--update", help="update NLAN stateus", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="delete NLAN states", action="store_true", default=False)
    parser.add_option("-I", "--info", help="set log level to INFO", action="store_true", default=False)
    parser.add_option("-D", "--debug", help="set log level to DEBUG", action="store_true", default=False)
    parser.add_option("-f", "--envfile", help="NLAN Agent environment file", action="store", type="string", dest="filename")

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
	
    data = None 
    if operation:
        data = sys.stdin.read().replace('"','') 
    else:
        data = args

    __n__['logger'].info('NLAN Agent initialization completed')

    _route(operation=operation, data=data)

