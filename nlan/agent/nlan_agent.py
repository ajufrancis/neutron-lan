#!/usr/bin/env python

import os, sys, time, copy
from optparse import OptionParser
from collections import OrderedDict
import logging
import cStringIO
import traceback

from cmdutil import CmdError
from errors import ModelError
import argsmodel 

ENVFILE = '/opt/nlan/nlan_env.conf'

def _init(envfile=ENVFILE, loglevel=logging.WARNING):

    # Environment setting
    with open(envfile, 'r') as envfile:
        import __builtin__
        __builtin__.__dict__['__n__'] = eval(envfile.read())

    # Logger setting
    logger = logging.getLogger("nlan_agent")
    logger.setLevel(loglevel)
    handler = logging.StreamHandler(sys.stdout)
    #handler2 = logging.FileHandler('/tmp/nlan_agent.log')
    handler.setLevel(loglevel)
    #handler2.setLevel(loglevel)
    header = None
    header = "[%(levelname)s] %(asctime)s module:%(module)s,function:%(funcName)s,router:{}".format(__n__['router'])
    formatter = logging.Formatter(header+"\n%(message)s")
    handler.setFormatter(formatter)
    #handler2.setFormatter(formatter)
    logger.addHandler(handler)
    #logger.addHandler(handler2)
    __n__['logger'] = logger


# Progress of CRUD requests 
def _progress(data, func, _index):
    progress = OrderedDict()
    modules = data.keys()
    hereafter = False
    for mod in modules:
        if mod in __n__['indexes']:
            progress[mod] = {}
            for l in data[mod]:
                idx = l['_index']
                if hereafter:
                    progress[mod][tuple(idx)] = False
                elif mod == func and idx == _index:
                    progress[mod][tuple(idx)] = False
                    hereafter = True
                else:
                    progress[mod][tuple(idx)] = True
        else:
            if hereafter:
                progress[mod] = False
            elif mod == func:
                progress[mod] = False
                hereafter = True 
            else:
                progress[mod] = True

    result = []
    for k,v in progress.iteritems():
        result.append((k,v))

    return result 

# Routing a request to a module
def _route(operation, data):
    
    exit = 0

    if operation in ('add', 'update', 'delete', 'get'): 
        # Calls config modules 
        from oputil import Model
        if __n__['init'] != 'start':
            if isinstance(data, str) and (data.startswith('OrderedDict') or data.startswith('{')):
                data = eval(data)
        _data = copy.deepcopy(data)
        results = None 
        error = None 
        module = None
        _index = None
        try:
            for module, model in data.iteritems():
                if operation == 'get': # CRUD get operation
                    import ovsdb
                    __n__['logger'].info('function:{0}.{1}, model:{2}'.format(module, operation, str(model)))
                    results = ovsdb.get_state(module, model)  
                else: # CRUD add/update/delete operation
                    _mod = __import__('config.'+module, globals(), locals(), [operation], -1)
                    call = _mod.__dict__[operation]
                    if module in __n__['indexes']:
                        for _model in model:
                            _index = _model['_index']
                            del _model['_index']
                            __n__['logger'].info('function:{0}.{1}, index:{3}, model:{2}'.format(module, operation, str(_model), str(_index)))
                            m = Model(operation, module, _model, _index)
                            # Routes a requested model to a config module
                            call(m)
                    else:
                        __n__['logger'].info('function:{0}.{1}, model:{2}'.format(module, operation, str(model)))
                        m = Model(operation, module, model)
                        # Routes a requested model to a config module 
                        call(m)
        except CmdError as e:
            error = OrderedDict()
            error['exception'] = 'CmdError'
            error['message'] = e.message
            error['traceback'] = traceback.format_exc() 
            error['command'] = e.command
            error['stdout'] = e.out
            error['exit'] = e.returncode 
            error['operation'] = operation
            if operation != 'get':
                error['progress'] = _progress(_data, module, _index)
            __n__['logger'].debug(str(error))
        except ModelError as e:
            error = OrderedDict()
            error['exception'] = 'ModelError'
            error['message'] = e.message
            error['traceback'] = traceback.format_exc() 
            error['exit'] = 1
            error['operation'] = operation
            if operation != 'get':
                error['progress'] = _progress(_data, module, _index)
            __n__['logger'].debug(str(error))
        except Exception as e:
            error = OrderedDict()
            error['exception'] = type(e).__name__ 
            error['message'] = 'See the traceback message'
            error['traceback'] = traceback.format_exc() 
            error['exit'] = 1
            error['operation'] = operation
            if operation != 'get':
                error['progress'] = _progress(_data, module, _index)
            __n__['logger'].debug(str(error))
        finally:
            if results:
                # STDOUT
                print results
            if error:
                print >>sys.stderr, str(error)
                exit = sys.exit(error['exit'])
            else:
                if __n__['init'] != 'start':
                    completed = OrderedDict()
                    completed['message'] = 'Execution completed'
                    completed['exit'] = 0
                    print >>sys.stderr, str(completed)
    elif operation in ('rpc_dict', 'rpc_args'):        
        # Calls a rpc module
        rpc = None
        func = None
        args = None
        kwargs = {} 
        error = None 
        result = None
        if operation == 'rpc_args':
            s = data[0].split('.')
            rpc = '.'.join(s[:-1])
            func = s[-1]
            args = tuple(data[1:])
        elif operation == 'rpc_dict':
            try:
                d = eval(data)
                if isinstance(d, OrderedDict):
                    rpc = d['module']
                    func = d['func']
                    args = d['args']
                    kwargs = d['kwargs']
                else:
                    raise Exception
            except:
                raise Exception("Illegal RPC request: {}".format(data))
        try:
            _mod = __import__('rpc.'+rpc, globals(), locals(), [func], -1)
            call = _mod.__dict__[func]
            __n__['logger'].info('function:{0}.{1}, args:{2}, kwargs:{3}'.format(rpc, func, str(args), str(kwargs)))
            result = call(*args, **kwargs)
        except CmdError as e:
            error = OrderedDict()
            error['exception'] = 'CmdError'
            error['message'] = e.message
            error['command'] = e.command
            error['stdout'] = e.out
            error['exit'] = e.returncode 
        except Exception as e:
            error = OrderedDict()
            error['exception'] = 'Exception'
            error['message'] = 'See the traceback message'
            error['exit'] = 1
            error['traceback'] = traceback.format_exc() 
        finally:
            if result:
                # STDOUT
                print str(result)
            if error:
                print >>sys.stderr, str(error)
                exit= sys.exit(error['exit'])
            else:
                completed = OrderedDict()
                completed['message'] = 'Execution completed'
                completed['exit'] = 0
                print >>sys.stderr, str(completed)
    else:
        raise Exception("Unsupported NLAN operation, {}".format(operation))

    return exit


def _linux_init():

    import ovsdb 
    state = ovsdb.get_current_state()
    
    exit = 0

    for module in __n__['state_order']:

        model = None

        if module in __n__['indexes'] and module in state:
            ind_key = __n__['indexes'][module]
            for d in state[module]: # dict in the list
                d['_index'] = [ind_key, d[ind_key]] # Adds _index
            model = {module: state[module]}
        elif module in state:
            model = {module: state[module]}

        if model:
            __n__['logger'].debug("Linux init, model: " + str(model))
            exit = _route('add', model) 

    return exit


if __name__ == "__main__":

    import sys

    logo = """
       _  ____   ___   _  __
      / |/ / /  / _ | / |/ /
     /    / /__/ __ |/    /
    /_/|_/____/_/ |_/_/|_/ AGENT

    """

    usage = logo + "usage: %prog [options] [arg]..."
    
    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--add", help="(CRUD) add NLAN states", action="store_true", default=False)
    parser.add_option("-g", "--get", help="(CRUD) get NLAN states", action="store_true", default=False)
    parser.add_option("-u", "--update", help="(CRUD) update NLAN stateus", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="(CRUD) delete NLAN states", action="store_true", default=False)
    parser.add_option("-s", "--schema", help="(CRUD) print schema", action="store_true", default=False)
    parser.add_option("-r", "--rpc", help="RPC w/ args from stdin", action="store_true", default=False)
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
    elif options.rpc:
        operation = 'rpc_dict'

    loglevel = logging.WARNING
    if options.info:
        loglevel = logging.INFO
    elif options.debug:
        loglevel = logging.DEBUG

    if options.filename:
        _init(options.filename, loglevel=loglevel)
    else:
        _init(loglevel=loglevel)

    if options.schema:
        if len(args) == 1:
            print argsmodel.schema_help(args[0])
        else:
            print argsmodel.schema_help(None)
        sys.exit(0)
	
    data = None 
    if operation and len(args) == 0:
        # Obtains data from nlan.py via SSH
        data = sys.stdin.read().replace('"','') 
    elif operation and len(args) > 0:
        # Obtains data from command arguments
        data = argsmodel.parse_args(operation, args[0], *args[1:])
    else: # RPC w/ command arguments
        data = args
        operation = 'rpc_args'

    __n__['logger'].info('NLAN Agent initialization completed')
    __n__['logger'].debug('__n__: {}'.format(__n__))

    exit = 0
    if options.init_action:
        __n__['init'] = options.init_action
        exit = _linux_init()
    else:
        __n__['init'] = False
        exit = _route(operation=operation, data=data)
    __n__['logger'].info('NLAN Agent execution completed')
    sys.exit(exit)

