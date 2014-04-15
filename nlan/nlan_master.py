#!/usr/bin/env python

"""
2014/3/12
2014/3/27

Usage example:
$ python nlan-master.py [yamlfile1] [yamlfile2] ...
$ python nlan-master.py init.run
$ python nlan-master.py test.ping 192.168.1.10

"""

import traceback
import cmdutil
import yamldiff
import os, sys
from optparse import OptionParser
import nlan_ssh

def exec_nlan_ssh(mode, option, args, loglevel, git):

    if option != None:
        nlan_ssh.main(operation=option, doc=None)
    else:
        if args[0].endswith('.yaml'):
            # State files
            for v in args:
                cmd_list = yamldiff.crud_diff(v)
                if len(cmd_list) != 0:
                    try:
                        nlan_ssh.main(operation='--batch', cmd_list=cmd_list, loglevel=loglevel) 
                        if git:
                            cmdutil.check_cmd('git add', v)
                            cmdutil.check_cmd('git commit -m updated')
                    except:
                        traceback.print_exc()
        else:
            # Execution module
            nlan_ssh.main(doc=args, loglevel=loglevel)

if __name__=='__main__':

    parser = OptionParser()
    parser.add_option("-p", "--printcmd", help="Print commands to be executed", action="store_true", default=False)
    parser.add_option("-c", "--scp", help="copy neutron-lan scripts to remote routers", action="store_true", default=False)
    parser.add_option("-m", "--scpmod", help="copy neutron-lan modules to remote routers", action="store_true", default=False)
    parser.add_option("-a", "--add", help="add elements", action="store_true", default=False)
    parser.add_option("-g", "--get", help="get elements", action="store_true", default=False)
    parser.add_option("-u", "--update", help="update elements", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="delete elements", action="store_true", default=False)
    parser.add_option("-I", "--info", help="set loglevel to INFO", action="store_true", default=False)
    parser.add_option("-D", "--debug", help="set loglevel to DEBUG", action="store_true", default=False)
    parser.add_option("-G", "--git", help="Git archive", action="store_true", default=False)

    (options, args) = parser.parse_args()

    mode = 'exec'
    option = None 
    git = False
    if options.printcmd:
        mode = 'print'
    elif options.scp:
        option = '--scp'
    elif options.scpmod:
        option = '--scpmod'
    elif options.add:
        option = '--add'
    elif options.update:
        option = '--update'
    elif options.get:
        option = '--get'
    elif options.delete:
        option = '--delete'
    elif options.git:
        git = True 

    loglevel = '' 
    if options.info:
        loglevel = '--info'
    elif options.debug:
        loglevel = '--debug'

    exec_nlan_ssh(mode, option, args, loglevel, git)
