# 2014/3/17
# vxlan.py
#

import cmdutil
from ovsdb import Row, get_vxlan_ports

def add(model):
    
    cmd = cmdutil.cmd	
    local_ip = model['local_ip']
    remote_ips = model['remote_ips']

    for remote_ip in remote_ips:
        inf = 'vxlan_' + remote_ip.split('.')[3]
        print '>>> Adding a VXLAN tunnel: ' + inf
        cmd('ovs-vsctl add-port br-tun', inf, '-- set interface', inf, 'type=vxlan options:in_key=flow', 'options:local_ip='+local_ip, 'options:out_key=flow', 'options:remote_ip='+remote_ip)

    vxlan_ports = get_vxlan_ports()
    for vxlan_port in vxlan_ports:
        cmd('ovs-ofctl add-flow br-tun', 'table=0,priority=1,in_port='+vxlan_port+',actions=resubmit(,2)')
 
    # VSDB transaction
    r = Row('vxlan')
    r.setrow(model)

