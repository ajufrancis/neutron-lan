# 2014/5/14
#

import collections

# For unit testing
if __name__ == '__main__':
    import __builtin__
    with open('nlan_env.conf', 'r') as f:
        __builtin__.__dict__['__n__'] = eval(f.read())

# Converts command arguments into a model
def parse_args(module, *args):

    schema = __n__['types'][module]
    
    def _type(key):
        
        if 'value' in schema[key]: # dict
            type_ = schema[key]['value']['type']
            if type_ == 'string':
                return (dict, str)
            elif type_ == 'integer':
                return (dict, int)
            else:
                return None
        else:
            type_ = schema[key]['key']['type']
            t = None
            if type_ == 'string':
                t = str 
            elif type_ == 'integer':
                t = int
            if 'max' in schema[key]:
                max_ = schema[key]['max']
                if max_ == 'unlimited' or int(max_) > 1: # list
                    return (list, t)
                else:
                    return (None, t)
            else:
                return (None, t)

    model = collections.OrderedDict() 
    submodel = {} 
    index = None
    for s in args:
        ss = s.split('=')
        k = ss[0]
        v = ss[1]
        if k == '_index':
            pair = v.split(',')
            key = pair[0]
            value = pair[1]
            index = [key, _type(key)[1](value)]
        else:
            t = _type(k)
            
            if t[0] == None:
                value = t[1](v)
                submodel[k] = value
            elif t[0] == dict:
                value = {}
                for item in v.split(','):
                    pair = item.split(':')
                    value[pair[0]] = t[1](pair[1])
                submodel[k] = value
            elif t[0] == list:
                value = []
                for item in v.split(','):
                    value.append(t[1](item))
                submodel[k] = value

    if index:
        submodel['_index'] = index
        model[module] = [submodel]
    else:
        model[module] = submodel

    return model

if __name__=='__main__':

    args = ('_index=vni,101', 'vni=101', 'vid=1', 'peers=192.168.0.1,192.168.0.2', 'ip_dvr=addr:10.0.1.1/24,mode:dvr')

    print parse_args('subnets', *args)

    args = ('ovs_bridges=enabled',)

    print parse_args('bridges', *args)

