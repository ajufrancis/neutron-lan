#!/usr/bin/python

"""
2014/3/12

This script generates CRUD operations referring to YAML files
and a local git repo, then execute nlan-ssh.py with the CRUD operations.

Currently, --add and --delete are supported. --get and --set will be
supported in future.

Usage example:
$ python nlan-master.py [yamlfile1] [yamlfile2] ...

"""

import cmdutil
import yamldiff
import os, sys

NLAN_DIR = '/root/neutron-lan/script'
NLAN_SSH = os.path.join(NLAN_DIR, 'nlan-ssh.py')

def exec_nlan_ssh(argv):

    for v in argv:
        cmd_list = yamldiff.crud_diff(v)
        for l in cmd_list:
            command = ['python', NLAN_SSH]
            command.extend(l)
            print cmdutil.output_cmd2(command)

if __name__=='__main__':

    exec_nlan_ssh(sys.argv[1:])
