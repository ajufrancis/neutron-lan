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

# kwargs test 
def kwargs_test(a=None,b=None,c=None,d=None):

    return (type(a), str(a), type(b), str(b), type(c), str(c), type(d), str(d))
    
