# 2014/3/17
# vxlan.py
#

import cmdutil
from ovsdb import Row, get_vxlan_ports
from oputil import Model

def add(model):
    
    cmd = cmdutil.check_cmd	
    cmdp = cmdutil.check_cmdp	
    m = Model('add', model)

    for remote_ip in _remote_ips:
        inf = 'vxlan_' + remote_ip.split('.')[3]
        __n__['logger'].info('Adding a VXLAN tunnel: ' + inf)
        cmdp('ovs-vsctl add-port br-tun', inf, '-- set interface', inf, 'type=vxlan options:in_key=flow', 'options:local_ip='+_local_ip, 'options:out_key=flow', 'options:remote_ip='+remote_ip)

    vxlan_ports = get_vxlan_ports()
    for vxlan_port in vxlan_ports:
        cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=1,in_port='+vxlan_port+',actions=resubmit(,2)')
 
    # VSDB transaction
    m.finalize()

