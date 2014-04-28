# 2014/4/18
# OVSDB and NLAN schema utility

import sys, json, yaml, lya
from optparse import OptionParser

# [Reference] http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = decode_dict(item)
        rv.append(item)
    return rv

def decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = decode_dict(value)
        rv[key] = value
    return rv

def merge_schema(nlan_yaml, ovsdb_json):

    with open(ovsdb_json, 'r') as f:
        ovs = f.read()
    with open(nlan_yaml, 'r') as f:
        nlan = f.read()
    ovs_dict = json.loads(ovs, object_hook=decode_dict)
    nlan_dict = yaml.load(nlan)
    for key, value in nlan_dict.iteritems():
        ovs_dict['tables'][key] = value
    return json.dumps(ovs_dict)

def analyze_schema(nlan_yaml):

    with open(nlan_yaml, 'r') as f:
        nlan = f.read()
    tables = {}
    indexes = {}
    types = {}
    dict_schema = {}
    # STATE_ORDER
    nlan_dict = yaml.load(nlan, lya.OrderedDictYAMLLoader)
    columns = nlan_dict['NLAN']['columns']
    yield columns.keys()
    # Hereafter, state order does not matter
    nlan_dict = yaml.load(nlan)
    columns = nlan_dict['NLAN']['columns']
    for module in columns.keys():
        tables[module] = columns[module]['type']
    yield tables
    for module in tables.keys():
        table = tables[module]['key']['refTable'] 
        table = nlan_dict[table]
        types[module] = {}
        if 'indexes' in table:
            indices = table['indexes']
            index = None
            for line in indices:
                index = line[0]
            indexes[module] = index
        for param in table['columns'].keys():
            types[module][param] = table['columns'][param]['type']
    # INDEXES
    yield indexes
    yield types

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-o", "--ovsdb", help="Original OVSDB schema file (JSON)", action="store", type="string", dest="ovsdb_file")
    parser.add_option("-n", "--nlan", help="NLAN schema file (YAML)", action="store", type="string", dest="nlan_file")
    parser.add_option("-m", "--merge", help="Merge NLAN and OVSDB schema", action="store_true", default=False)
    parser.add_option("-y", "--yaml", help="Output YAML", action="store_true", default=False)
    parser.add_option("-j", "--json", help="Output JSON", action="store_true", default=False)
    parser.add_option("-d", "--dict", help="Output Python dict", action="store_true", default=False)
    parser.add_option("-a", "--analyze", help="Analyze NLAN schema", action="store_true", default=False)

    (options, args) = parser.parse_args()

    nlan_yaml = options.nlan_file
    ovsdb_json = options.ovsdb_file

    if not ovsdb_json and not nlan_yaml:
        parser.print_help()
    else:
        if options.merge:
            print merge_schema(nlan_yaml, ovsdb_json)
        elif options.yaml:
            if ovsdb_json:
                with open(ovsdb_json, 'r') as f:
                    d = json.loads(f.read(), object_hook=decode_dict)
                    print yaml.dump(d)
        elif options.analyze:
            state_order, tables, indexes, types = analyze_schema(nlan_yaml)
            print state_order
            print tables
            print indexes
            print types 



    """
    f = open(sys.argv[2], 'r').read()
    d = json.loads(f, object_hook=decode_dict)
    print "##### Python Dictionary #####"
    print d
    
    y = yaml.dump(d)
    print "##### YAML #####"
    print y

    j = yaml.load(y)
    print "##### Python Dictionary #####"
    print j

    j= merge_schema(sys.argv[1], sys.argv[2])
    print "##### Merged JSON #####"
    print j
    
    d = json.loads(j, object_hook=decode_dict)
    y = yaml.dump(d)
    print "##### Merged YAML #####"
    print y
    """

