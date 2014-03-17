Use of OVSDB in neutron-lan
---------------------------

OVSDB is used for storing local config parameters, so that the config survives after rebooting the system.


OVSDB table relationship for neutron-lan
----------------------------------------

The OVSDB schema basically follows the YAML-based modeling of neutron-lan:

<pre>
NLAN
  | 
  +-- bridges -- NLAN_Bridges
  |   
  +-- gateway*-- NLAN_Gateway
  |
  +-- vxlan* -- NLAN_VXLAN
  |
  +-- subnets* -- NLAN_Subnet
</pre>

Note that "NLAN" is a root-set table, so "isRoot" in the schema definion is set to "true".

OVSDB neutron-lan schema
------------------------

<pre>
   "NLAN": {
     "columns": {
       "bridges": {
         "type": {"key": {"type": "uuid",
                          "refTable": "NLAN_Bridges"},
                  "min": 0, "max": 1}},
       "gateway": {
         "type": {"key": {"type": "uuid",
                          "refTable": "NLAN_Gateway"},
                  "min": 0, "max": 1}},
       "vxlan": {
         "type": {"key": {"type": "uuid",
                          "refTable": "NLAN_VXLAN"},
                  "min": 0, "max": 1}},
       "subnets": {
         "type": {"key": {"type": "uuid",
                          "refTable": "NLAN_Subnet"},
                  "min": 0, "max": "unlimited"}}},   
     "isRoot": true,
     "maxRows": 1},
   "NLAN_Bridges": {
     "columns": {
       "ovs_bridges": {
         "type": "string"},
       "controller": {
         "type": "string"}},
     "maxRows": 1},
   "NLAN_Gateway": {
     "columns": {
       "rip": {
         "type": "string"},
       "network": {
         "type": "string"}},
     "maxRows": 1},
   "NLAN_VXLAN": {
     "columns": {
       "local_ip": {
         "type": "string"},
       "remote_ips": {
         "type": {"key": {"type": "string"},
                  "min": 0, "max": "unlimited"}}},
     "maxRows": 1},
   "NLAN_Subnet": {
     "columns": {
       "vid": {
         "type": "integer"},
       "vni": {
         "type": "integer"},
       "ip_dvr": {
         "type": "string"},
       "ip_vhost": {
         "type": "string"},
       "ports": {
         "type": {"key": {"type": "string"},
                  "min": 0, "max": "unlimited"}}},
     "indexes": [["vni"]]},
</pre>

OVSDB client
------------

I have written a python script [ovsdb-test-script.py](https://github.com/alexanderplatz1999/neutron-lan/blob/master/ovsdb/ovsdb-test-client.py) to test the new OVSDB schema.


id=0, insert rows into "NLAN" table:
<pre>
rpc = {
"method":"transact",
"params":[
    "Open_vSwitch",
    {
        "op": "insert",
        "table": "NLAN",
        "row":  {
            }
    }
    ],
"id": 0
}
</pre> 

id = 1, insert "NLAN_Subnet" rows:
<pre>
rpc = {
"method":"transact",
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
"id": 1
}
</pre>

id=2, select rows where "vni=1001" in "NLAN_Subnet" table:
<pre>
rpc = {
"method":"transact",
"params":[
    "Open_vSwitch",
    {
        "op": "select",
        "table": "NLAN_Subnet",
        "where": [["vni", "==", 1001]]
    }
    ],
"id": 2
}
</pre>

id=3, update "ip_dvr" where "vni=1001" in "NLAN_Subnet" table：
<pre>
rpc = {
"method":"transact",
"params":[
    "Open_vSwitch",
    {
        "op": "update",
        "table": "NLAN_Subnet",
        "where": [["vni", "==", 1001]],
        "row": {"ip_dvr": "10.0.1.2/24"}
    }
    ],
"id": 3
}
</pre>

id=4, select rows where "vni=1001" in "NLAN_Subnet" table：
<pre>
rpc = {
"method":"transact",
"params":[
    "Open_vSwitch",
    {
        "op": "select",
        "table": "NLAN_Subnet",
        "where": [["vni", "==", 1001]]
    }
    ],
"id": 4
}
</pre>

id=5, delete rows in "NLAN_Subnet" table(the value of "uuid_subnet" is from the result of id=4 transaction)：
<pre>
rpc = {
"method": "transact",
"params": [
    "Open_vSwitch",
    {
        "op": "mutate",
        "table": "NLAN",
        "where": [],
        "mutations": [
            [
                "subnets",
                "delete",
                [
                    "set",
                    [
                        [
                            "uuid",
                            uuid_subnet
                        ]
                    ]
                ]
            ]
        ]
    }
],
"id": 5
}
</pre>

Then I have executed the test script "ovsdb-test-client.py"：
<pre>
root@debian:~/neutron-lan/ovsdb# python ovsdb-test-client.py
{"id":0,"error":null,"result":[{"uuid":["uuid","57b0cdc6-c6bf-4899-8676-b529ce79a334"]}]}
{"id":1,"error":null,"result":[{"uuid":["uuid","5b87e1c6-64cf-49ff-93e1-9c41e9c08014"]},{"count":1}]}
{"id":2,"error":null,"result":[{"rows":[{"_uuid":["uuid","5b87e1c6-64cf-49ff-93e1-9c41e9c08014"],"ip_vhost":"","ports":["set",["eth0","veth-test"]],"ip_dvr":"10.0.0.1/24","vid":101,"_version":["uuid","5012ff9e-6aa5-4019-a15f-5e85add28b7b"],"vni":1001}]}]}
{"id":3,"error":null,"result":[{"count":1}]}
{"id":4,"error":null,"result":[{"rows":[{"_uuid":["uuid","5b87e1c6-64cf-49ff-93e1-9c41e9c08014"],"ip_vhost":"","ports":["set",["eth0","veth-test"]],"ip_dvr":"10.0.1.2/24","vid":101,"_version":["uuid","4b5ae6e8-f57c-4914-bdcc-7ee0ea894f57"],"vni":1001}]}]}
{"id":5,"error":null,"result":[{"count":1}]}
</pre>
