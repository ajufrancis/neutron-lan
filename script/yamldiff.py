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

DEL_DUPLICATES = True 

# TODO: auto-generate this data from a OVSDB schema
INDEXES = {'subnets': 'vni'}

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

# Returns lya.AttrDict object 
def _get_base(filename):
    return(lya.AttrDict.from_yaml(filename))

# Returns lya.AttrDict object
# If the git file is vacant or non-existent, default YAML data is used 
def _get_base_git(filename):
    default = "vacant: true"
    try:
        data = output_cmd('git show HEAD:' + filename)
        if data == '':
            data = default 
    except:
        data = default 
    od = yaml.load(StringIO(data), lya.OrderedDictYAMLLoader)
    return(lya.AttrDict(od))

# This function generates a uci-get-like path=value list from a YAML file.
# If uci_style == True, this func outputs pathes in @...[] format.
# Returns a list of path=value.
def _yaml_load(base, uci_style=False):

    flatten = lya.AttrDict.flatten(base)
    values = []
    for l in flatten:
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
                                index = '@' + key + ':' + str(value)    
                            else:
                                index = str(count)
                            for key in dic:
                                if uci_style:
                                    pl = path+'.@'+m+'['+index+'].'+key+'='+str(dic[key])
                                else:
                                    pl = path+'.'+m+'['+index+'].'+key+'='+str(dic[key])

                                values.append(pl)
                        else: 
                            if uci_style:
                                pl = path+'.@'+m+'['+str(count)+']='+str(elm)
                            else:
                                pl = path+'.'+m+'['+str(count)+']='+str(elm)
                            values.append(pl)
                        count += 1
                else:
                    path += '.'+m+'='+str(l[1])
                    values.append(path)
    
    return sorted(values)

#
# Returns diff in the unified format.
#
def _diff(list1, list2):
    return unified_diff(list1, list2, 'before', 'after')


# Outputs CRUD operations list for nlan-ssh.py
# making diff between two YAML files.
# base1: lya.AttrDict (before)
# base2: lya.AttrDict (after)
# crud_list: a list of [node, operation, model]
def _crud_diff(base1, base2):

    list1 = _yaml_load(base1)
    list2 = _yaml_load(base2)
    
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
    if DEL_DUPLICATES:
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
        list2.append([line[0], line[2] , line[1], line[3]])
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
        if l[3].startswith('['):
            value = eval(l[3])
        else:
            value = l[3]
        key_value = {key: value}
        if idx == None:
            dic = {router: {ope: {module: key_value}}}
        else:
            idx_key_value = {idx: key_value}
            dic = {router: {ope: {module: idx_key_value}}}
        dict_merge(crud_dict, dic)

    # Generates final output
    crud_list = []
    for key in crud_dict.keys():
        dic = crud_dict[key]
        for key2 in dic.keys():
            dic2 = dic[key2]
            crud_list.append([key, key2, str(dic2)]) 
    return sorted(crud_list, reverse=True)


# Generate CRUD operations working with a local git repo
def crud_diff(filename):

    base1 = _get_base_git(filename)
    base2 = _get_base(filename)
    return _crud_diff(base1, base2)

#
# Unit test
#
if __name__=='__main__':

    import sys

    # From a git repo 
    base1 = _get_base_git(sys.argv[1])
    # From a local file 
    base2 = _get_base(sys.argv[1])

    print '----- test: yaml_load: before  -----'
    list1 = _yaml_load(base1)
    for l in list1:
        print l

    print '----- test: yaml_load: after -----'
    list2 = _yaml_load(base2)
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
