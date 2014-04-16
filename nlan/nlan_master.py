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
                    except:
                        traceback.print_exc()
                        sys.exit(1)
                if git:
                    cmdutil.check_cmd('git add', v)
                    cmdutil.check_cmd('git commit -m updated')
        else:
            # Command module
            nlan_ssh.main(doc=args, loglevel=loglevel)

if __name__=='__main__':

    usage = "usage: %prog [options] [arg]..."
    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--scp", help="copy scripts to remote routers", action="store_true", default=False)
    parser.add_option("-m", "--scpmod", help="copy NLAN Agent and NLAN modules to remote routers", action="store_true", default=False)
    parser.add_option("-I", "--info", help="set log level to INFO", action="store_true", default=False)
    parser.add_option("-D", "--debug", help="set log level to DEBUG", action="store_true", default=False)
    parser.add_option("-G", "--git", help="use Git archive", action="store_true", default=False)

    (options, args) = parser.parse_args()

    mode = 'exec'
    option = None 
    git = False
    if options.scp:
        option = '--scp'
    elif options.scpmod:
        option = '--scpmod'
    elif options.git:
        git = True 

    loglevel = '' 
    if options.info:
        loglevel = '--info'
    elif options.debug:
        loglevel = '--debug'

    exec_nlan_ssh(mode, option, args, loglevel, git)
