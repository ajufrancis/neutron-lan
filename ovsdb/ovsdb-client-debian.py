"""
2014/3/13

"""

import socket, json

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect('/var/run/openvswitch/db.sock')

id = 0
uuid = ""

seq = [
{"method":"list_dbs", "params":[], "id": id}, 
{"method":"transact", "params":['Open_vSwitch',{"op":"select","table":"NLAN","where":[]}], "id": id},
{"method":"transact", 
"params":[
    "Open_vSwitch",
    {
        "op": "insert",
        "table": "NLAN_Subnet",
        "row":  {
            "vid": 101,
            "vni": 1001,
            "ip_dvr": "10.0.0.1/24",
            "ports": ["set", ["eth0", "veth-test"]]
                },
        "uuid-name": "vni1001"
    },{
        "op": "mutate",
        "table": "NLAN",
        "where": [],
        "mutations": [
            [
                "subnets",
                "insert",
                [
                    "set",
                    [
                        [
                            "named-uuid",
                            "vni1001"
                        ]
                    ]
                ]
            ]
        ]
    }
    ],
"id": id},
{"method":"transact", "params":['Open_vSwitch',{"op":"select","table":"Bridge","where":[["_uuid","==",["uuid", uuid]]],"columns":["flow_entries"]}], "id": id}
]

id = 0
print "list_dbs"
s.send(json.dumps(seq[id]))
print s.recv(4096) 

print ""
id = 1
print "transct select NLAN"
s.send(json.dumps(seq[id]))
print s.recv(4096) 

print""
id = 2
print "transact insert NLAN_Subnet"
s.send(json.dumps(seq[id]))
print s.recv(4096) 
