# 2014/3/27
# system.py
#

from cmdutil import output_cmd

def reboot(platform):
    
    print output_cmd('reboot')

def halt(platform):
    
    print output_cmd('halt') 

