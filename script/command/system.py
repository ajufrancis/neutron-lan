# 2014/3/27
# system.py
#

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

    print scripts

    return output_cmd(scripts[script][platform], command)

# Returns nlan environment
def env():
    
    return __n__
