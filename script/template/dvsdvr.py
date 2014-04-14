# 2014/04/03
#
import re
from yamldiff import *
from oputil import get_roster
from env import STATE_ORDER

# Placeholders: <remote_ips> and <peers>
def fillout(template):

    ips = {}
    vnis = {}
    chain = {}

    roster = get_roster()

    #print template

    for l in template:
        if re.search('vxlan.local_ip', l):
            router = get_node(l)
            #ips[router] = get_value(l)
            ips[router] = roster[router]['host']
        if re.search('vid=', l):
            router = get_node(l)
            vni = get_index_value(l)
            #print router,vni 
            if vni not in vnis:
                vnis[vni] = []
            vnis[vni].append(router)
        if re.search('chain=', l):
            router = get_node(l)
            chain[router] = get_value(l)

    # Placeholders
    local_ip = {}
    remote_ips = {}
    peers = {}
    sfports = {}

    for router in ips.keys():
        remote_ips[router] = []
        peers[router] = {}
        for r in ips.keys():
            if r != router:
                remote_ips[router].append(ips[r])
        for vni in vnis.keys():
            l = list(vnis[vni])
            if router in l:
                l.remove(router)
                for r in l:
                    l[l.index(r)] = ips[r]
                peers[router][vni] = l

    for router in chain.keys():
        sfports[router] = {}
        for path in chain[router]:
            p = path.split('.')
            peer_router = p[0]
            vni = int(p[1])
            sfports[router][vni] = [path] 

    #print remote_ips, peers, sfports

    tl = Template(template)
    tl.add_values('local_ip', ips, False)
    tl.add_values('remote_ips', remote_ips, False)
    tl.add_values('peers', peers, True)
    tl.add_values('sfports', sfports, True)

    return tl.fillout()

