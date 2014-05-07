# 2014/05/07
#
#
import sys, traceback, copy
from collections import OrderedDict
import yaml
import dictdiffer
import nlan, cmdutil, env

bar = '//////////////////////////////////////////////////////////////////////////////'

def _args_od(args, reverse=False):
    od = OrderedDict()
    state_order = copy.copy(env.STATE_ORDER)
    if reverse:
        state_order.reverse()
    for module in state_order:
        if module in args:
            od[module] = args[module]
    return od


if __name__ == '__main__':
    
    with open(sys.argv[1], 'r') as f:
        scenario = yaml.load(f.read())
        for l in scenario:
            if 'test' in l:
                rp = "TEST: {}".format(l['test'])
                print bar[:5], rp, bar[5+len(rp):]
            if 'command' in l:
                cmdutil.check_cmd(l['command'])
            if 'nlan' in l:
                ll = l['nlan']
                options = None
                args = None
                router = '_ALL' 
                if 'options' in ll:
                    options = ll['options']
                if 'args' in ll:
                    v = ll['args']
                    if isinstance(v, dict):
                        if options == '--delete':
                            args = _args_od(v, reverse=True)
                        else:
                            args = _args_od(v)
                        args = str(args)
                    else:
                        args = v.split()
                if 'router' in ll:
                    router = ll['router']
                result = nlan.main(router=router, operation=options, doc=args)
                #for l in result:
                #    for key, value in l.iteritems():
                #        print '{}: {}'.format(key, value)
                if 'assert' in ll:
                    if ll['assert']:
                        args1 = dict(eval(result[0]['stdout'][0]))
                        args2 = dict(_args_od(ll['assert']))
                        try:
                            assert len(list(dictdiffer.diff(args1, args2))) == 0
                            print '****************'
                            print '*** SUCCESS! ***'
                            print '****************'
                        except Exception as e:
                            print 'XXXXXXXXXXXXXXXX'
                            print 'XXX FAILURE! XXX'
                            print 'XXXXXXXXXXXXXXXX'
                            print traceback.format_exc()
                    else:
                        if result[0]['stdout']:
                            print 'XXXXXXXXXXXXXXXX'
                            print 'XXX FAILURE! XXX'
                            print 'XXXXXXXXXXXXXXXX'
                            print result[0]['stdout']
                        else:
                            print '****************'
                            print '*** SUCCESS! ***'
                            print '****************'


                    
