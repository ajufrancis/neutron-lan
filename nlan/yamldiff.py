# 2014/2/20
# 2014/3/12
# 2014/3/24-25
#
# Utilities to generate diff betwen two YAML files:
# one is a local YAML file, and the other is one in a local git repo.

import yaml, lya, datadiff, re, sys
from collections import OrderedDict
from difflib import unified_diff
from cStringIO import StringIO
from cmdutil import output_cmd
from copy import deepcopy
from env import INDEXES 

# Simple object serializer for int, list, str and OrderedObject
def dumps(value):

    if isinstance(value, int):
        s = 'int:'+str(value)
    elif isinstance(value, list):
        s = 'list:'+str(value)
    elif isinstance(value, str):
        s = 'str:'+str(value)
    elif isinstance(value, OrderedDict):
        s = 'OrderedDict:'+str(value)
    else:
        raise Exception("Type error: " + str(type(value)))

    return s 

# Simple object de-serializer for int, list, str and OrderedObject
def loads(string):

    s = string.split(':',1)
    t = s[0]
    v = s[1]   
    #print t, v
    if t == 'int':
        v = int(v)
    elif t == 'list' or t == 'OrderedDict':
        v = eval(v)
    elif t == 'str':
        pass
    else:
        raise Exception("Type error: " + str(type(string)))

    return v

def get_index(string):
    t = string.split(']')[0].split(':',1)
    idx = t[0]
    value = loads(t[1])
    return (idx, value)

def get_index_value(string):
    return loads(string.split(']')[0].split(':',1)[1])

def get_node(string):
    return string.split('.',1)[0]

def get_path(string):
    return string.split('=')[0].split('.',1)[1]

def get_node_path(string):
    return string.split('=')[0]

def get_value(string):
    return loads(string.split('=')[1])


# This class is used by template modules
class Template:

    def __init__(self, slist):
        self.slist = slist
        self.values_list = []

    def add_values(self, placeholder, values, index=False):
        self.values_list.append({'placeholder':placeholder, 'values':values, 'index':index})

    def fillout(self):
        for l in self.slist:
            node = get_node(l)
            for v in self.values_list:
                searchstring = '<' + v['placeholder'] + '>'
                if re.search(searchstring, l):
                    value = None
                    oldvalue = get_value(l)
                    if v['index']:
                        index = get_index_value(l)
                        value = v['values'][node][index]
                    else:
                        value = v['values'][node]
                    newvalue = re.sub(searchstring, str(value), oldvalue)
                    if isinstance(value, str):
                        newvalue = '"'+newvalue+'"'
                    ll = get_node_path(l) + '=' + dumps(eval(newvalue)) 
                    self.slist[self.slist.index(l)] = ll

        return self.slist


def get_template_module(firstline):
    if re.match(r"#!", firstline):
        return re.sub(r"^#!", "", firstline).rstrip()

#
# Merge two Python dictionaries
# Reference: http://blog.impressiver.com/post/31434674390/deep-merge-multiple-python-dicts
#
def dict_merge(target, *args):
    # Merge multiple dicts
    if len(args) > 1:
        for obj in args:
            dict_merge(target, obj)
        return target
    # Recursively merge dicts and set non-dict values
    obj = args[0]
    if not isinstance(obj, dict):
        return obj
    for k, v in obj.iteritems():
        if k in target and isinstance(target[k], dict):
            dict_merge(target[k], v)
        else:
            target[k] = deepcopy(v)
    return target


# This function is a YAML serializer generating a list of 
# "node.path=value" from a YAML file.
# Returns a list of path=value.
def _yaml_load(filename, git=False):

    od = None
    template_module = None

    if not git:
        with open(filename, 'r') as f:
            od = yaml.load(f, lya.OrderedDictYAMLLoader)
            f.seek(0)
            template_module = get_template_module(f.readline())
    else:
        default = "vacant: true"
        try:
            data = output_cmd('git show HEAD:' + filename)
            if data == '':
                data = default 
            else:
                template_module = get_template_module(StringIO(data).readline())
        except:
            data = default 
        od = yaml.load(data, lya.OrderedDictYAMLLoader)

    #print od
    base = lya.AttrDict(od)

    flatten = lya.AttrDict.flatten(base)
    
    values = []
    state_order = [] 
    for l in flatten:
        try:
            path = l[0][1]
            if path not in state_order:
                state_order.append(path)
        except:
            pass
        path = '' 
        length = len(l[0])
        for i in range(length): 
            m = l[0][i]
            if path == '':
                path = m
            else:
                if i != length-1:
                    path += '.'+m
                elif len(l[0]) == 2 and type(l[1]) is list:
                    count = 0
                    for elm in l[1]:
                        if type(elm) is OrderedDict:
                            dic = dict(elm)
                            index = None 
                            try:
                                key = INDEXES[m]
                            except:
                                pass
                            if key != None:
                                value = dic[key]
                                index = key + ':' + dumps(value)    
                            else:
                                index = str(count)
                            for key in dic:
                                pl = path+'.'+m+'['+index+'].'+key+'='+dumps(dic[key])

                                values.append(pl)
                        else: 
                            pl = path+'.'+m+'['+str(count)+']='+dumps(elm)
                            values.append(pl)
                            
                        count += 1
                else:
                    path += '.'+m+'='+dumps(l[1])
                    values.append(path)
    
    if template_module:
        __import__(template_module)
        module = sys.modules[template_module]
        values = module.fillout(values)
        state_order = module.STATE_ORDER

    return (sorted(values), state_order)

#
# Returns diff in the unified format.
#
def _diff(list1, list2):
    return unified_diff(list1, list2, 'before', 'after')


# Outputs CRUD operations list for nlan-ssh.py
# making diff between two YAML files.
# crud_list: a list of [node, operation, model]
def crud_diff(filename):

    # Before
    (list1, state_order1) = _yaml_load(filename, git=True)
    # After
    (list2, state_order2) = _yaml_load(filename)
    
    lines = _diff(list1=list1, list2=list2)
    add_delete = []

    for line in lines:
        if re.search('^[\+-][^+-]',line):
            add_delete.append(line)

    temp_list = []

    # '+' => '--add", '-' => '--delete'
    for line in add_delete:
        if line[0:1] == '+':
            operation = '--add' 
        else:
            operation = '--delete'

        idx = line.split('=')[0]
        value = line.split('=')[1]
        path = '.'.join(idx.split('.')[1:])
        if not re.search(':', path):
            path = path.split('[')[0]
        node = idx.split('.')[0][1:]

        temp_list.append([node, operation, path, value])

    # Delete duplicates
    values = [] 
    duplicates = [] 
    temp_list2 = []
    for line in temp_list:
        values.append(line[2]+'='+line[3])
    for line in temp_list:
        value = line[2]+'='+line[3]
        values.remove(value) 
        if value in values:
            duplicates.append(value)
    for line in temp_list:
        if line[3] not in duplicates: 
            temp_list2.append(line)

    # Finds "update" operations
    temp_list = sorted(temp_list2, reverse=True)
    list2 = []
    for line in temp_list:
        list2.append([line[0], line[2] , line[1], loads(line[3])])
    list2 = sorted(list2, reverse=True)
    list3 = list2
    for i in range(len(list2)-1):
        if list2[i][0] == list2[i+1][0] and list2[i][1] == list2[i+1][1]:
            list3[i][2] = '--none'
            list3[i+1][2] = '--update'
    crud_list = []
    for i in range(len(list3)):
        l = list3[i]
        if l[2] == '--none':
            pass
        else:
            crud_list.append([l[0], l[2], l[1], l[3]])

    # list => model (dict) conversion
    crud_dict = {}
    for l in crud_list:
        router = l[0]
        ope = l[1]
        if re.search('\[', l[2]): 
            module = l[2].split('[')[0]
            idx = (l[2].split('[')[1]).split(']')[0]
        else:
            module = l[2].split('.')[0]
            idx = None
        index = ''
        key = l[2].split('.')[1]
        value = l[3]
        key_value = {key: value}
        if idx == None:
            dic = {router: {ope: {module: key_value}}}
        else:
            i = idx.split(':',1)
            idx = (i[0], loads(i[1]))
            idx_key_value = {idx: key_value}
            dic = {router: {ope: {module: idx_key_value}}}
        dict_merge(crud_dict, dic)

    # Generates final output
    crud_list = []
    state_order1r = state_order1[::-1]
    for key in crud_dict.keys():
        dic = crud_dict[key]
        for key2 in dic.keys():
            dic2 = dic[key2]
            ordered_dict = OrderedDict()
            if key2 == '--add' or key2 == '--update':
                for k in state_order2:
                    try:
                        ordered_dict[k] = dic2[k]
                    except:
                        pass
            elif key2 == '--delete':
                for k in state_order1r:
                    try:
                        ordered_dict[k] = dic2[k]
                    except:
                        pass
            else:
                raise Exception("bad operation key")
            crud_list.append([key, key2, str(ordered_dict)])
    return sorted(crud_list, reverse=True)


#
# Unit test
#
if __name__=='__main__':

    import sys

    print '----- test: get_template_module -----'
    firstline = '#!test1.test2'
    print get_template_module(firstline)
    firstline = '##!test1.test2'
    print get_template_module(firstline)

    print '----- test: yaml_load: before  -----'
    (list1, state_order1) = _yaml_load(sys.argv[1], git=True)
    for l in list1:
        print l

    print '----- test: yaml_load: after -----'
    (list2, state_order2) = _yaml_load(sys.argv[1])
    for l in list2:
        print l
        
    print '----- test: diff -----'
    v = _diff(list1, list2)
    for l in v:
        print l
   
    print '----- test: crud_diff -----'
    crud_list = crud_diff(sys.argv[1])
    for l in crud_list:
        print l
