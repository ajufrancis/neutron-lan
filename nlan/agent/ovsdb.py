"""
2014/3/18, 3/31

OVSDB client libraries for neutron-lan

Reference: http://tools.ietf.org/rfc/rfc7047.txt 

"""

import random, oputil

DATABASE = 'Open_vSwitch'
PARENT = 'NLAN'
TABLES = __n__['tables']

def _index():
    return random.randint(0, 999999)

# OpenWRT's python-mini does not include the UUID package.
def _uuid_name():
    return 'temp_' + str(random.randint(0, 999999))

# Get a value of row "_uuid" in the response
# Limitation: This can get only the first row in the table
def get_uuid(response):
    return response["result"][0]["rows"][0]["_uuid"][1]

# OVSDB returns a non-list value even if it's 'max' is greater than 1.
# NLAN assumes that a value with 'max' greater than 1 is a list object
# even if it has only one member in the list.
def _iflist(module, param):
    iflist = False
    try:
        maxparam = __n__['types'][module][param]['max']
        if isinstance(maxparam, int):
            if maxparam > 1:
                iflist = True
        elif isinstance(maxparam, str):
            if maxparam == 'unlimited':
                iflist = True
    except:
        pass
    return iflist


def _iflist_tables(module):
    iflist = False
    try:
        maxparam = __n__['tables'][module]['max']
        if isinstance(maxparam, int):
            if int(maxparam) > 1:
                iflist = True
        elif isinstance(maxparam, str):
            if maxparam == 'unlimited':
                iflist = True
    except:
        pass
    return iflist

# Get a row in the form of Python dictionary 
def todict(response, module=None):

    dict_value = {}

    try:
        row = response["result"][0]["rows"][0]

        for key in row.keys():
            if key != '_uuid' and key != '_version':
                value = row[key]
                if isinstance(value, list):
                    if isinstance(value[1], list) and value[0] == 'set':
                        dict_value[key] = value[1]
                    if isinstance(value[1], list) and value[0] == 'map':
                        d = {} 
                        for l in value[1]:
                            d[l[0]] = l[1]
                        dict_value[key] = d
                    elif not(isinstance(value[1], list)) and value[0] == 'uuid':
                        dict_value[key] = value[1]
                else:
                    if _iflist(module, key):
                        dict_value[key] = [row[key]]
                    else:
                        dict_value[key] = row[key]
    except:
        pass

    return dict_value

# Get rows in the form of Python dictionary 
def todicts(response, module=None):

    dicts = [] 

    try:
        for row in response["result"][0]["rows"]:
            dict_value = {}

            for key in row.keys():
                if key != '_uuid' and key != '_version':
                    value = row[key]
                    if isinstance(value, list):
                        if isinstance(value[1], list) and value[0] == 'set':
                            dict_value[key] = value[1]
                        if isinstance(value[1], list) and value[0] == 'map':
                            d = {} 
                            for l in value[1]:
                                d[l[0]] = l[1]
                            dict_value[key] = d
                        elif not(isinstance(value[1], list)) and value[0] == 'uuid':
                            dict_value[key] = value[1]
                    else:
                        if _iflist(module, key):
                            dict_value[key] = [row[key]]
                        else:
                            dict_value[key] = row[key]

            dicts.append(dict_value)
    except:
        pass

    return dicts

            
# Get a value of count in the JSON-RPC response
def get_count(response):

    dict_value = {}

    count = 0
    try:
        count = response["result"][1]["count"]
    except:
        pass

    return count 

# Conversion between a Python list object and a list value
# as defined in RFC7047.
def _row(model):

    model_row = {}
    for key in model.keys():
        v = model[key]
        if isinstance(model[key], list):
            v = ["set", v]
        model_row[key] = v
    return model_row

# JSON-RPC transaction
def _send(request):

    import socket, json

    dumps = None
    loads = None
    sock = None
    dist = None 

    try:
        dist = __n__['platform']
    except:
        pass 

    if dist == 'openwrt':
        dumps = json.JsonWriter().write  
        loads = json.JsonReader().read
        sock = '/var/run/db.sock'
    else:
        dumps = json.dumps
        loads = json.loads
        sock = '/var/run/openvswitch/db.sock'

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(sock)

    
    pdu = dumps(request)
    s.send(pdu)
    response = s.recv(4096)

    __n__['logger'].debug(oputil.logstr('... JSON-RPC request ...', str(pdu), '... JSON-RPC response ...', response))

    return loads(response)

# JSON-RPC Operations as specified in RFC7047 #########################

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

    response = select(table, where)
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

# O/R mapper  ################################################
# This O/R mapper manipulate a raw as described in RFC7047.
# Usage:
# r = Row('Interface', ('name', 'vxlan_102'))
# print r['ofport']
# Limitations:
# Can get only one row (the first row) even if
# multiple rows mactch the index.
class OvsdbRow(object):
   
    # Creates an instance of a row 
    def __init__(self, table, index=None):

        self.table = table 
        self.index = index

        self.where = [] 
        
        if self.index != None:

            column = self.index[0]
            value = self.index[1]

            self.where = [[
                column,
                "==",
                value
                ]]

        response = select(self.table, self.where)
        self.row = todict(response)


    def __setitem__(self, key, value):
        v = value
        if isinstance(v, list):
            v = ["set", v]
        row = {key: v}
        update(self.table, self.where, row)
        self.row[key] = value

    def __getitem__(self, key):
        return self.row[key]

    def __delitem__(self, key):

        # TODO: this is an ugly coding... improve it!
        def _default(value):
            t = type(value)
            d = None
            if t == int:
                d = 0
            elif t == str or t == unicode:
                d = ''
            elif t == list:
                tt = type(value[0])
                if tt == int:
                    d = 0
                elif tt == str or tt == unicode:
                    d = ''
            if d == None:
                raise Exception ("Type error")
            else:
                return d

        value = self.row[key]
        row = {key: _default(value)}
        update(self.table, self.where, row)
        self.row[key] = None

    #def __getattr__(self, key):
    #    return self.row[key]
    
    def getrow(self):
        return self.row

    def getparam(self, *args):

        for key in args:
            if key in self.row.keys():
                yield self.row[key]
            else:
                yield None

# O/R mapper for NLAN ################################################
# This O/R mapper manipulate a raw as described in RFC7047.
# Usage:
# r = Row('subnets', ('vni', 1001))
# r.setrow(model)
# r['vid'] = 101
# r['ports'] = ['eth0', 'eth1']
# vid = r['vid']
# d = r.getrow()
# r.delrow()
class Row(OvsdbRow):


    # Creates an instance of a row 
    def __init__(self, module, index=None):

        response = insert('NLAN', {})
        self.module = module

        #self.parent = self.__class__.PARENT
        self.parent = PARENT

        #table = self.__class__.TABLES[module]
        table = TABLES[module]['key']['refTable']

        super(self.__class__, self).__init__(table, index)

    def setrow(self, model):
        row = _row(model)
        response = insert_mutate(self.table, row, self.parent, self.module)
        response = select(self.table, self.where)
        self.row = todict(response)

    def delrow(self):
        response = mutate_delete(self.table, self.where, self.parent, self.module)
        self.row = {} 

    
    def crud(self, crud, model):

        if __n__['init'] != 'start':

            ind = self.index[0]
            keys = model.keys()

            __n__['logger'].debug("CRUD operation ({0}): {1}".format(crud,str(model)))

            if ind in keys and crud == 'add':
                self.setrow(model)
            elif crud == 'add' or crud == 'update':
                for k in keys:
                    self[k] = model[k]
            elif ind in keys and crud == 'delete':
                self.delrow()
            elif crud == 'delete':
                for k in keys:
                    del self[k]
            else:
                raise Exception("Parameter error")


    @classmethod
    def clear(cls):
        #response = delete(cls.PARENT, [])
        response = delete(PARENT, [])

# Searches a table with 'column = value'.
# Returns rows in the form of Python dictionary
def search(table, columns, key=None, value=None):
  
    where = []
    if key and value:
        where = [[
            key,
            "==",
            value
            ]]

    response = select(table, where, columns)
    return todicts(response)

# Obtains ofport <=> peers mapping data for vxlan ports
# to construct broadcast trees for each vni
def get_vxlan_ports(peers=None):

    #print peers, type(peers)

    ofports = []
    tablesearch = search('Interface', ['ofport', 'options'], 'type', 'vxlan')
    vxlan_ports = []
    if peers:
        for ip in peers:
            for l in tablesearch:
                if l['options']['remote_ip'] == ip:
                    vxlan_ports.append(str(l['ofport']))
    else:
        for l in tablesearch:
            vxlan_ports.append(str(l['ofport']))

    return vxlan_ports

def get_vxlan_port(peer):

    tablesearch = search('Interface', 'type', 'vxlan', ['ofport', 'options']
)
    for l in tablesearch:
        if l['options']['remote_ip'] == peer:
            return l['ofport']

    raise Exception("No ofport found")

def get_current_state():

    state = {}

    row = todict(select('NLAN', []))

    for key in row:
        if key != '_uuid' and key != '_version':
            v = row[key]
            #if isinstance(v, list):
            if _iflist_tables(key):
                if len(v) > 0:
                    state[key] = todicts(select(table=TABLES[key]['key']['refTable'],where=[]),key)   
            elif isinstance(v, str) or isinstance(v, unicode):
                state[key] = todict(select(table=TABLES[key]['key']['refTable'],where=[]),key)

    return state


#######################################################################

# Unit test
if __name__=='__main__':

#    __builtins__.__n__ = {'platform': 'openwrt'}

    where = [[
        "vni",
        "==",
        1001
        ]]

    print "##### Insert test: 'NLAN' table #####"
    response = insert('NLAN', {})
    print str(get_count(response))

    row = {
        "vid": 101,
        "vni": 1001,
        "ip_dvr": "10.0.0.1/24",
        #"ports": ["set", ["eth0", "veth-test"]]
        }
   
    print "##### Insert and Mutate test: 'NLAN_Subnet' table #####"
    response = insert_mutate('NLAN_Subnet', row, 'NLAN', 'subnets')
    print str(get_count(response))

    print "##### Select test #####" 
    select('NLAN_Subnet', where)
    print search('NLAN_Subnet', "vid", 101, ["vni", "ip_dvr"])

    # This transaction shuld fail, since a row with vni=1001
    # has already been inserted.
    print "##### Insert and Mutate test: 'NLAN_Subnet' table #####"
    response = insert_mutate('NLAN_Subnet', row, 'NLAN', 'subnets')
    print str(get_count(response))

    select('NLAN_Subnet', where)

    print "##### Update test #####"
    row = {
            "ip_dvr": "10.0.1.2/24",
            "ports": ["set", ["eth0", "veth-test"]]
          }

    update('NLAN_Subnet', where, row)

    response = select('NLAN_Subnet', where)
    print str(todict(response))
   
    # Creates an instance of OVSDB O/R mapper 
    print "##### Row instance creation test #####"
    row = Row('subnets', ('vni', 1001))
    print "row: " + str(row.row)
    print "_uuid: " + row['_uuid']

    row['ports'] = ["eth0", "eth1"]
    row['ip_dvr'] = '10.0.111.222/24'

    print row.getrow()

    del row['ports']
    print row['ports']
    del row['vid']
    print row['vid']
    select('NLAN_Subnet', where)
   
    print "##### Delete test ######"
    
    # This fuction call fails, since one reference remains in 'NLAN' table.
    delete('NLAN_Subnet', where)
    
    #mutate_delete('NLAN_Subnet', where, 'NLAN', 'subnets')
    row.delrow()

    response = select('NLAN', [])
    
    print str(todict(response))

    print "##### Row class test #####"
    model = {
        "vid": 101,
        "vni": 1001,
        "ip_dvr": "10.0.0.1/24",
        "ports": ["eth0", "veth-test"]
        }

    row.setrow(model)
    v = row.getrow()
    print v
    for key in v.keys():
        print key + ': ' + str(v[key])
    #row.delrow()
    #print (row.getrow())
    Row.clear()

    print "##### Row class test2 #####"
    row = Row('subnets', ('vni', 1001))
    print "## crud: add ##"
    model = {
        "vid": 101,
        "vni": 1001,
        "ip_dvr": "10.0.0.1/24",
        "ports": ["eth0", "veth-test"]
        }
    row.crud('add', model)
    print row.getrow()
    print "## crud: update """
    model = {
        "ip_dvr": "20.0.0.1/24",
        "ports": ["eth0"]
        }
    row.crud('update', model)
    print row.getrow()
    print "## crud: delete ##"
    model = {
        "vid": 101,
        "ip_dvr": "20.0.0.1/24",
        "ports": ["eth0"]
        }
    row.crud('delete', model)
    print row.getrow()
    Row.clear()

    print "##### OvsdbRow class test #####"
    try:
        r = OvsdbRow('Interface', ('name', 'vxlan'))
        print 'ofport: ' + str(r['ofport'])
    except:
        pass

    print "##### Ovsdb search test #####"
    try:
        print search('Interface', 'type', 'vxlan', ['ofport', 'options'])
    except:
        pass


