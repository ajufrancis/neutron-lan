"""
2014/3/17

"""

import os, socket, json
import random

DIST = 'debian'

dumps = None
loads = None
sock = None

if DIST == 'debian':
    dumps = json.dumps
    loads = json.loads
    sock = '/var/run/openvswitch/db.sock'
elif DIST == 'openwrt':
    dumps = json.JsonWriter().write  
    loads = json.JsonReader().read
    sock = '/var/run/db.sock'

def get_rpc_insert(table, row, parent_table, parent_row):

    # OpenWRT's python-mini does not include the UUID package.
    uuid_name = str(random.random())
    i = str(random.randint(0,9999))

    return {
    "method":"transact", 
    "params":[
        parent_table,
        {
            "op": "insert",
            "table": table,
            "row": row, 
            "uuid-name": uuid_name
        },{
            "op": "mutate",
            "table": table,
            "where": [],
            "mutations": [
                [
                    parent_row,
                    "insert",
                    [
                        "set",
                        [
                            [
                                "named-uuid",
                                uuid_name
                            ]
                        ]
                    ]
                ]
            ]
        }
        ],
    "id": i 
    }


def insert(table, row, parent_table, parent_row):

    return send(get_rpc_insert(table, row, parent_table, parent_row)
     
"""
def select(table, where, row):
    pass

def update(table, where, row):
    pass

def delete(table, where, row, parent_table, parent_row):
    pass
"""

def send(rpc):

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(sock)

    s.send(dumps(rpc))
    return s.recv(4096)


if __name__=='__main__':

    row = {
    "vid": 101,
    "vni": 1001,
    "ip_dvr": "10.0.0.1/24",
    "ports": ["set", ["eth0", "veth-test"]]
    }
    
    print get_rpc_insert('NLAN_Subnet', row, 'NLAN', 'subnets')
    

