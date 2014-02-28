# 2014/2/20
#
# Utilities to produce diff from two YAML files.
#

import yaml, lya
from collections import OrderedDict
import re
from difflib import unified_diff
import datadiff

# This function generates a uci-get-like path=value list from a YAML file.
# If uci_style == True, this func outputs pathes in @...[] format.
# Returns a lya.AttrDict instance and a list of path=value.
def yaml_load(filename, uci_style=False):

    base = lya.AttrDict.from_yaml(filename)
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

    return (base, values)


#
# Returns diff in the unified format.
#
def diff(list1, list2):
    return unified_diff(list1, list2, 'before', 'after')


# Outputs CRUD operations list for nlan-ssh.py making diff between two YAML files.
# filename1: YAML file (before)
# filename2: YAML file (after)
# crud_list: a list of [operation, node, path, value]
def crud_diff(filename1, filename2):

    crud_list = []

    base1, list1 = yaml_load(filename1)
    base2, list2 = yaml_load(filename2)
    
    lines = diff(list1=list1, list2=list2)
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
 
        crud_list.append([operation, node, path, value])

    return crud_list

#
# Unit test
#
if __name__=='__main__':

    import sys

    print '----- test: yaml_load: before  -----'
    base1, list1 = yaml_load(sys.argv[1], uci_style=True)
    for l in list1:
        print l

    print '----- test: yaml_load: after -----'
    base2, list2 = yaml_load(sys.argv[2], uci_style=True)
    for l in list2:
        print l
 
    print '----- test: yaml_load: before  -----'
    base1, list1 = yaml_load(sys.argv[1])
    for l in list1:
        print l

    print '----- test: yaml_load: after -----'
    base2, list2 = yaml_load(sys.argv[2])
    for l in list2:
        print l
        
    print '----- test: diff -----'
    v = diff(list1, list2)
    for l in v:
        print l

   
    print '----- test: crud_diff -----'
    crud_list = crud_diff(sys.argv[1], sys.argv[2])

    for l in crud_list:
        print l[0], l[1], l[2], l[3]

