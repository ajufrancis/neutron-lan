# 2014/3/3
# gateway.py
#
# Quagga manipulation module 
#

from cmdutil import output_cmd, output_cmd2

def add_gateway(hardware, model):
	
    rip = model['rip']
    network = model['network']

    if rip == 'enabled':
        print '>>> Adding a gateway router: rip'

    args = """
    configure terminal
    interface {0}
    link-detect
    exit
    router rip
    version 2
    redistribute connected
    network {0}
    exit
    exit
    write
    exit
    """.format(network)

    cmd_args = ['vtysh'] 
    for line in args.split('\n')[1:-1]:
        cmd_args.append('-c')
        cmd_args.append(line.lstrip())

    try:
        print output_cmd2(cmd_args)
    # Fails if zebrad and ripd have not been started yet.
    except:
        print output_cmd('/etc/init.d/quagga start')
        print output_cmd2(cmd_args)

    print output_cmd('/etc/init.d/quagga restart')


# Unit test
if __name__=='__main__':
    hardware = 'testhw'
    model = {'rip': 'enabled', 'network': 'eth2'}
    add_gateway(hardware, model)

