"""
2014/3/18

OVSDB client libraries for neutron-lan

"""

import os, socket, json
import random

DIST = 'debian'
DATABASE = 'Open_vSwitch'

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

def _index():
    return random.randint(0, 999999)

# OpenWRT's python-mini does not include the UUID package.
def _uuid_name():
    return 'temp_' + str(random.randint(0, 999999))

# Get a value of row "_uuid" in the response
def get_uuid(response):
    return response["result"][0]["rows"][0]["_uuid"][1]

# Get a value of row in the response
def get_rows(response):

    dict_value = {}

    try:
        rows = response["result"][0]["rows"][0]

        for key in rows.keys():
            value = rows[key]
            if isinstance(value, list):
                if isinstance(value[1], list) and value[0] == 'set':
                    dict_value[key] = value[1]
                elif not(isinstance(value[1], list)) and value[0] == 'uuid':
                    dict_value[key] = value[1]
            else:
                dict_value[key] = rows[key]
    except:
        pass

    return dict_value
            
# Get a value of count in the response
def get_count(response):

    dict_value = {}

    count = 0
    try:
        count = response["result"][1]["count"]
    except:
        pass

    return count 

def _send(request):

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(sock)

    print '----- JSON-RPC TRANSACTION -----'
    print str(request)
    s.send(dumps(request))
    print '---'
    response = s.recv(4096)
    print response
    return loads(response)

# JSON-RPC Operations #################################################

"""
"op": "insert"              required
"table": <table>            required
"row": <row>                required
"uuid-name": <id>           optional

"""
def insert(table, row):
    
    i = _index()

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        {
            "op": "insert",
            "table": table,
            "row": row 
        }
        ],
    "id": i 
    }

    return _send(request)


"""
"op": "insert"              required
"table": <table>            required
"row": <row>                required
"uuid-name": <id>           optional

"""
def insert_mutate(table, row, parent_table, parent_column):

    i = _index() 
    uuid_name = _uuid_name()

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        {
            "op": "insert",
            "table": table,
            "row": row, 
            "uuid-name": uuid_name
        },{
            "op": "mutate",
            "table": parent_table,
            "where": [],
            "mutations": [
                [
                    parent_column,
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

    return _send(request)


"""
"op": "select"              required
"table": <table>            required
"where": [<conditions>*]    required
"columns": [<column>*]      optional

"""
def select(table, where, columns=None):

    i = _index()

    obj = {
        "op": "select",
        "table": table,
        "where": where
        }

    if columns != None:
        obj['columns'] = columns

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        obj
        ],
    "id": i 
    }
    
    return _send(request)


"""
"op": "update"              required
"table": <table>            required
"where": [<conditions>*]    required
"row": <row>                required
"""
def update(table, where, row):

    i = _index()

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        {
            "op": "update",
            "table": table,
            "where": where,
            "row": row
        }
        ],
    "id": i 
    }
    
    return _send(request)


"""
"op": "delete"              required
"table": <table>            required
"where": [<condition>*]     required

"""
def delete(table, where):

    i = _index() 
    uuid_name = _uuid_name()

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        {
            "op": "delete",
            "table": table,
            "where": where 
        }
        ],
    "id": i 
    }

    return _send(request)


def mutate_delete(table, where, parent_table, parent_column):

    i = _index() 

    response = select('NLAN_Subnet', where)
    uuid = get_uuid(response)

    request = {
    "method":"transact", 
    "params":[
        DATABASE,
        {
            "op": "mutate",
            "table": parent_table,
            "where": [],
            "mutations": [
                [
                    parent_column,
                    "delete",
                    [
                        "set",
                        [
                            [
                                "uuid",
                                uuid
                            ]
                        ]
                    ]
                ]
            ]
        }
        ],
    "id": i 
    }

    return _send(request)

# O/R mapper for OVSDB ################################################
class ovsdb:
    
    def __init__(self, module, index=None):

        TABLES = {
            'subnets': 'NLAN_Subnet'
        }
        self.module = module
        self.index = index
        table = TABLES[module]
        self.table = table
        
        if index != None:

            column = index[0]
            value = index[1]

            where = [[
                column,
                "==",
                value
                ]]

            response = select('NLAN_Subnet', where)
            print str(get_rows(response))

    def __setattr__(self, name, value):
        pass

    def __getattr__(self, key):
        pass

    def __delattr__(self, key):
        pass
            
#######################################################################

# Unit test
if __name__=='__main__':

    response = insert('NLAN', {})
    print str(get_count(response))

    row = {
        "vid": 101,
        "vni": 1001,
        "ip_dvr": "10.0.0.1/24",
        #"ports": ["set", ["eth0", "veth-test"]]
        }
    
    response = insert_mutate('NLAN_Subnet', row, 'NLAN', 'subnets')
    print str(get_count(response))
   
    # This transaction shuld fail, since a rows with vni=1001
    # has already been inserted.
    response = insert_mutate('NLAN_Subnet', row, 'NLAN', 'subnets')
    print str(get_count(response))

    where = [[
        "vni",
        "==",
        1001
        ]]

    select('NLAN_Subnet', where)

    row = {
            "ip_dvr": "10.0.1.2/24",
            "ports": ["set", ["eth0", "veth-test"]]
          }

    update('NLAN_Subnet', where, row)

    response = select('NLAN_Subnet', where)
    print str(get_rows(response))
   
    # Creates an instance of OVSDB O/R mapper 
    mod = ovsdb('subnets', ('vni', 1001))
   
    # This fuction call fails, since one reference remains in 'NLAN' table.
    delete('NLAN_Subnet', where)
    
    mutate_delete('NLAN_Subnet', where, 'NLAN', 'subnets')

    response = select('NLAN', [])
    
    print str(get_rows(response))
