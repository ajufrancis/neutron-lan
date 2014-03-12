# 2014/2/20
# 2014/3/12
#
# Utilities to generate diff betwen two YAML files:
# one is a local YAML file, and the other is one in a local git repo.

import yaml, lya, datadiff, re, sys
from collections import OrderedDict
from difflib import unified_diff
from cStringIO import StringIO
from cmdutil import output_cmd

DEL_DUPLICATES = True 

def _get_base(filename):
    return(lya.AttrDict.from_yaml(filename))

def _get_base_git(filename):
    data = output_cmd('git show HEAD:' + filename)
    od = yaml.load(StringIO(data), lya.OrderedDictYAMLLoader)
    return(lya.AttrDict(od))

# This function generates a uci-get-like path=value list from a YAML file.
# If uci_style == True, this func outputs pathes in @...[] format.
# Returns a lya.AttrDict instance and a list of path=value.
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
                elif type(l[1]) is list:
                    count = 0
                    for elm in l[1]:
                        if type(elm) is OrderedDict:
                            dic = dict(elm)
                            for key in dic:
                                if uci_style:
                                    pl = path+'.@'+m+'['+str(count)+'].'+key+'='+str(dic[key])
                                else:
                                    pl = path+'.'+m+'['+str(count)+'].'+key+'='+str(dic[key])

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
# crud_list: a list of [operation, node, path, value]
def _crud_diff(base1, base2):

    crud_list = []

    list1 = _yaml_load(base1)
    list2 = _yaml_load(base2)
    
    lines = _diff(list1=list1, list2=list2)
    add_delete = []
    lya_pathes = []

    for line in lines:
        if re.search('^[\+-][^+-]',line):
            add_delete.append(line)

    for line in add_delete:
        path = line[1:].split('=')[0]
        if line[0:1] == '+':
            lya_path = 'base2.' + path
            try:
                eval(lya_path)
                lya_pathes.append(lya_path)
            except:
                lya_pathes.append('.'.join(lya_path.split('.')[:-1]))
        else:
            lya_path = 'base1.' + path
            try:
                eval(lya_path)
                lya_pathes.append(lya_path)
            except:
                lya_pathes.append('.'.join(lya_path.split('.')[:-1]))

    lya_pathes = list(set(lya_pathes))

    for lya_path in lya_pathes:
        value = ''
        if type(eval(lya_path)) is OrderedDict:
            value = str(dict(eval(lya_path)))
        else:
            value = eval(lya_path)
        op = lya_path.split('.')[0]
        operation = ''
        if op == 'base1':
            operation = '--delete'
        else:
            operation = '--add'
        node = lya_path.split('.')[1]
        path = '.'.join(lya_path.split('.')[2:])
 
        crud_list.append([node, operation, path, value])

    # Regular expression: "\[[0-9]+\]" ==> ''
    for line in crud_list:
        if re.search(r"\[[0-9]+\]", line[2]):
            line[2] = re.sub(r"\[[0-9]+\]", "", line[2])
            line[3] = '[' + line[3] + ']'

    # Delete duplicates in crud_list
    if DEL_DUPLICATES:
        values = [] 
        duplicates = [] 
        crud_list2 = []
        for line in crud_list:
            values.append(line[3])
        for line in crud_list:
            value = line[3]
            values.remove(value) 
            if value in values:
                duplicates.append(value)
        for line in crud_list:
            if line[3] not in duplicates: 
                crud_list2.append(line)
        return sorted(crud_list2, reverse=True)
    else:
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
    list1 = _yaml_load(base1, uci_style=True)
    for l in list1:
        print l

    print '----- test: yaml_load: after -----'
    list2 = _yaml_load(base2, uci_style=True)
    for l in list2:
        print l
 
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
        #print l[0], l[1], l[2], l[3]
        print l

