# 2014/3/27
# test.py
#

from cmdutil import output_cmd

# Returns a ping result
def ping(host):
    
    return output_cmd('ping -c4', host)

# Returns args
def echo(*args):
    
    return ' '.join(list(args))
