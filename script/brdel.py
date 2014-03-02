from cmdutil import output_cmd, cmd

bridges = {}
brname = ''
o = output_cmd('brctl show').split('\n')
for l in o:
    ll = l.split()
    if len(ll) == 7:
        pass
    elif len(ll) == 4:
        brname = ll[0]
        interface = ll[3]
        bridges[brname] = [interface] 
    elif len(ll) == 1:
        interface = ll[0]
        bridges[brname].append(interface) 
print bridges
for brname in bridges.keys():
    for interface in bridges[brname]:
        cmd('ip link set dev', interface, 'down')
        cmd('brctl delif', brname, interface)
    cmd('ip link set dev', brname, 'down')
    cmd('brctl delbr', brname)
print bridges
