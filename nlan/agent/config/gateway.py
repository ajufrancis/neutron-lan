# 2014/3/3
# 2014/3/17
# gateway.py
#
# Quagga manipulation module 
#

from cmdutil import output_cmd, output_cmd2
from ovsdb import Row

def add(model):

    rip = model['rip']
    network = model['network']

    if rip == 'enabled':
        __n__['logger'].info('Adding a gateway router: rip')

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
        output_cmd2(cmd_args)
    # Fails if zebrad and ripd have not been started yet.
    except:
        output_cmd('/etc/init.d/quagga start')
        output_cmd2(cmd_args)

        output_cmd('/etc/init.d/quagga restart')

    # OVSDB transaction
    r = Row('gateway')
    r.setrow(model)


# Unit test
if __name__=='__main__':
    model = {'rip': 'enabled', 'network': 'eth2'}
    add(model)

