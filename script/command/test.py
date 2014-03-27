# 2014/3/27
# test.py
#

from cmdutil import output_cmd

def ping(platform, host):
    
    print output_cmd('ping -c4', host)

def echo(platform, *args):
    
    print ' '.join(list(args))

