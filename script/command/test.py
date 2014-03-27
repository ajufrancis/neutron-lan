# 2014/3/27
# test.py
#

from cmdutil import output_cmd

def ping(host):
    
    print output_cmd('ping -c4', host)

def echo(*args):
    
    print ' '.join(list(args))

