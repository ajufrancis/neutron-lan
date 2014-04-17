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
import ovsdb 

ENVFILE = '/opt/nlan/nlan_env.conf'

#out = cStringIO.StringIO()
out = sys.stdout

def _init(envfile = ENVFILE):

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
        if __n__['init'] != 'start':
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



def _linux_init():

    state = ovsdb.get_current_state()

    for module in __n__['state_order']:

        model = None

        if module in __n__['indexes'] and module in state:
            ind_key = __n__['indexes'][module]
            substate = state[module]
            if isinstance(substate, dict):
                model = {module: {(ind_key, substate[ind_key]):substate}} 
            elif isinstance(substate, list):
                temp = {} 
                for l in substate:
                    temp[(ind_key, l[ind_key])]=l
                model = {module: temp}

        elif module in state:
            model = {module: state[module]}

        if model:
            __n__['logger'].debug("Linux init, model: " + str(model))
            _route('add', model) 


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
    parser.add_option("-i", "--init", help="Linux init script", action="store", type="string", dest="init_action")

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

    if options.init_action:
        __n__['init'] = options.init_action
        _linux_init()
    else:
        __n__['init'] = False
        _route(operation=operation, data=data)

    #log = out.getvalue()
    #if log != '':
    #print log
    #out.close()
