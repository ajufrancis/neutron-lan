# 2014/3/31
# config.py
#

from ovsdb import Row

def getrow(module):
    
    r = Row(module)
    print r.getrow()

if __name__=='__main__':

    print getrow(sys.argv[1])

