#!/usr/bin/python

"""
2014/3/12
2014/3/27

Usage example:
$ python nlan-master.py [yamlfile1] [yamlfile2] ...
$ python nlan-master.py init.run
$ python nlan-master.py test.ping 192.168.1.10

"""

import cmdutil
import yamldiff
import os, sys
from optparse import OptionParser

NLAN_DIR = '/root/neutron-lan/script'
NLAN_SSH = os.path.join(NLAN_DIR, 'nlan-ssh.py')

def exec_nlan_ssh(mode, option, args, git):

    if option != None:
        if option == '--scp':
            listdir = os.listdir(NLAN_DIR)
            files = ' '.join(listdir)
            print cmdutil.output_cmd('python', NLAN_SSH, '*', option, files)
        else:
            print cmdutil.output_cmd('python', NLAN_SSH, '*', option)
    else:
        if args[0].endswith('.yaml'):
            # State files
            for v in args:
                cmd_list = yamldiff.crud_diff(v)
                if len(cmd_list) != 0:
                    for l in cmd_list:
                        command = ['python', NLAN_SSH]
                        command.extend(l)
                        print cmdutil.check_cmd2(command)
                        
                    if git:
                        cmdutil.check_cmd('git add', v)
                        cmdutil.check_cmd('git commit -m updated')
        else:
            # Execution module
            l = ['python', NLAN_SSH, '*']
            l.extend(args)
            args = tuple(l)
            print cmdutil.output_cmd(*args)  

if __name__=='__main__':

    parser = OptionParser()
    parser.add_option("-p", "--printcmd", help="Print commands to be executed", action="store_true", default=False)
    parser.add_option("-c", "--scp", help="copy neutron-lan scripts to remote routers", action="store_true", default=False)
    parser.add_option("-m", "--scpmod", help="copy neutron-lan modules to remote routers", action="store_true", default=False)
    parser.add_option("-a", "--add", help="add elements", action="store_true", default=False)
    parser.add_option("-g", "--get", help="get elements", action="store_true", default=False)
    parser.add_option("-u", "--update", help="update elements", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="delete elements", action="store_true", default=False)
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

    exec_nlan_ssh(mode, option, args, git)
