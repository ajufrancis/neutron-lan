# 2014/3/27
# system.py
#

import os
from cmdutil import output_cmd

def reboot():
    
    return output_cmd('reboot')

def halt():
    
    return output_cmd('halt') 

def service(*args):
    
    scripts = {'networking':{'openwrt': '/etc/init.d/network','raspbian': 'service networking'}}

    script = args[0]
    command = args[1]
    platform = __n__['platform']

    return output_cmd(scripts[script][platform], command)

def rc(args=None):

    platform = __n__['platform']
    etc_dir = __n__['etc_dir']

    init_script = None 
    command = {} 
    chmod = 'chmod 755 /etc/init.d/nlan'
    if platform == 'debian':
        init_script = os.path.join(etc_dir, 'nlan_debian')
        command['enable'] = ['cp {} /etc/init.d/nlan'.format(init_script), chmod, 'update-rc.d nlan defaults']
        command['update'] = ['cp {} /etc/init.d/nlan'.format(init_script)]
        command['disable'] = ['rm /etc/init.d/nlan', 'update-rc.d nlan remove']
        command['status'] = ['ls /etc/rc2.d/']
    elif platform == 'openwrt':
        init_script = os.path.join(etc_dir, 'nlan_openwrt')
        command['enable'] = ['cp {} /etc/init.d/nlan'.format(init_script), chmod, '/etc/init.d/nlan enable']
        command['update'] = ['cp {} /etc/init.d/nlan'.format(init_script)]
        command['disable'] = ['/etc/init.d/nlan disable', 'rm /etc/init.d/nlan']
        command['status'] = ['ls /etc/rc.d/']

    if args in command:
        try:
            for l in command[args]:
                print output_cmd(l)
        except Exception as e:
            # TODO: openwrt's init script returns exit code 1 even if the operation is successful.
            print e 
    else:
        return "Usage:\nsystem.rc (enable|update|disable|status)"
        

