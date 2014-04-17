# 2014/3/31
# config.py
#

from ovsdb import Row
import cmdutil
import os

def getrow(module):
    
    r = Row(module)
    print r.getrow()

if __name__=='__main__':

    print getrow(sys.argv[1])

# Update OVSDB Schema with NLAN-related addition
def update_schema():

    cmd = cmdutil.cmd
    platform = __n__['platform']
    schema = os.path.join(__n__['agent_dir'], __n__['schema'])
    stop = None
    start = None

    if platform == 'openwrt':
        cmd('/etc/init.d/openvswitch stop')
        cmd('ovsdb-tool convert /etc/openvswitch/conf.db', schema)
        cmd('cp /etc/openvswitch/conf.db /etc/openvswitch/conf.db.old')
        cmd('/etc/init.d/openvswitch start')
    elif platform == 'debian' or platform == 'raspbian':
        cmd('service openvswitch-switch stop')
        cmd('cp', schema, '/usr/share/openvswitch/vswitch.ovsschema')
        cmd('service openvswitch-switch start')

