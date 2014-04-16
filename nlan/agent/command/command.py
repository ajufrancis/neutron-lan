# 2014/4/16
# command.py
#

import os

def list():
    d = os.path.join(__n__['agent_dir'], 'command')
    l = os.listdir(d)
    for f in l:
        if f.endswith('.py'):
            with open(os.path.join(d, f), 'r') as ff:
                print "... file: {} ...".format(f)
                source = ff.read().rstrip('\n')
                lines = source.split('\n')
                for line in lines:
                    if line.startswith('def '):
                        line = line.rstrip(':').split(' ',1)[1]
                        print "- {}".format(line)
            print ''
