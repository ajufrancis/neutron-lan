# 2014/04/03
#
import re
from yamldiff import *

# Placeholders: <remote_ips> and <peers>
def fillout(template):

    ips = {}
    vnis = {}
    for l in template:
        if re.search('vxlan.local_ip', l):
            router = get_node(l)
            ips[router] = get_value(l)
        if re.search('vid=', l):
            vni = get_index_value(l)
            print router,vni 
            if vni not in vnis:
                vnis[vni] = []
            vnis[vni].append(router)

    remote_ips = {}
    peers = {}

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

    #print remote_ips, peers 

    tl = Template(template)
    tl.add_values('remote_ips', remote_ips, False)
    tl.add_values('peers', peers, True)

    return tl.fillout()

