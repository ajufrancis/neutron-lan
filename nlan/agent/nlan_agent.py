#!/usr/bin/env python

import os, sys, time, copy
from optparse import OptionParser
from collections import OrderedDict
import logging
import cStringIO
from cmdutil import CmdError
from errors import ModelError
import traceback

ENVFILE = '/opt/nlan/nlan_env.conf'

#out = cStringIO.StringIO()
out = sys.stdout

def setlogger(d):
    logger = logging.getLogger("nlan_agent")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(out)
    handler.setLevel(logging.DEBUG)
    header = "[%(levelname)s] module:%(module)s,function:%(funcName)s,router:{}".format(__n__['router'])
    formatter = logging.Formatter(header+"\n%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    d['logger'] = logger

def _init(envfile = ENVFILE):

    # Environment setting
    with open(envfile, 'r') as envfile:
        import __builtin__
        __builtin__.__dict__['__n__'] = eval(envfile.read())

    setlogger(__n__)

# Progress of deployment
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
    return progress

# Routing a request to a module
def _route(operation, data):
    
    if operation:
        # Calls config modules 
        from oputil import Model
        if __n__['init'] != 'start':
            data = eval(data)
        _data = copy.deepcopy(data)
        results = []
        error = None 
        module = None
        _index = None
        try:
            for module in data.keys():
                _mod = __import__('config.'+module, globals(), locals(), [operation], -1)
                call = _mod.__dict__[operation]
                model = data[module]
                if module in __n__['indexes']:
                    for _model in model:
                        _index = _model['_index']
                        del _model['_index']
                        __n__['logger'].info('function:{0}.{1}, index:{3}, model:{2}'.format(module, operation, str(_model), str(_index)))
                        m = Model(operation, module, _model, _index)
                        # Routes a requested model to a config module
                        result = call(m)
                        if result:
                            results.append(result)
                else:
                    __n__['logger'].info('function:{0}.{1}, model:{2}'.format(module, operation, str(model)))
                    m = Model(operation, module, model)
                    # Routes a requested model to a config module 
                    result = call(m)
                    if result:
                        results.append(result)
        except CmdError as e:
            error = OrderedDict()
            error['exception'] = 'CmdError'
            error['message'] = e.message
            error['traceback'] = traceback.format_exc() 
            error['command'] = e.command
            error['stdout'] = e.out
            error['exit'] = e.returncode 
            error['operation'] = operation
            error['progress'] = _progress(_data, module, _index)
        except ModelError as e:
            error = OrderedDict()
            error['exception'] = 'ModelError'
            error['message'] = e.message
            error['traceback'] = traceback.format_exc() 
            error['exit'] = 1
            error['operation'] = operation
            error['progress'] = _progress(_data, module, _index)
        except Exception as e:
            error = OrderedDict()
            error['exception'] = type(e).__name__ 
            error['message'] = 'See the traceback message'
            error['traceback'] = traceback.format_exc() 
            error['exit'] = 1
            error['operation'] = operation
            error['progress'] = _progress(_data, module, _index)
        finally:
            if len(results) > 0:
                # STDOUT
                for o in results:
                    print o
            if error:
                print >>sys.stderr, str(error)
                sys.exit(error['exit'])
            else:
                if __n__['init'] != 'start':
                    completed = OrderedDict()
                    completed['message'] = 'Execution completed'
                    completed['exit'] = 0
                    print >>sys.stderr, str(completed)
                    sys.exit(0)
    else:        
        # Calls a command module
        s = data[0].split('.')
        command = '.'.join(s[:-1])
        func = s[-1]
        error = None 
        result = None
        try:
            _mod = __import__('command.'+command, globals(), locals(), [func], -1)
            call = _mod.__dict__[func]
            args = tuple(data[1:])
            __n__['logger'].info('function:{0}.{1}, args:{2}'.format(command, func, str(args)))
            result = call(*args)
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
                print result 
            if error:
                print >>sys.stderr, str(error)
                sys.exit(error['exit'])
            else:
                completed = OrderedDict()
                completed['message'] = 'Execution completed'
                completed['exit'] = 0
                print >>sys.stderr, str(completed)
                sys.exit(0)



def _linux_init():

    import ovsdb 
    state = ovsdb.get_current_state()

    for module in __n__['state_order']:

        model = None

        if module in __n__['indexes'] and module in state:
            ind_key = __n__['indexes'][module]
            for d in state[module]: # dict in the list
                d['_index'] = [ind_key, d[ind_key]] # Adds _index
            model = {module: state[module]}
        elif module in state:
            model = {module: state[module]}

        print model

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

    if options.init_action:
        __n__['init'] = options.init_action
        __n__['logger'].info('NLAN Agent initialization completed\n{}'.format(__n__))
        _linux_init()
    else:
        __n__['init'] = False
        __n__['logger'].info('NLAN Agent initialization completed\n{}'.format(__n__))

        _route(operation=operation, data=data)

