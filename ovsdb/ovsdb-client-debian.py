"""
2014/3/13

"""

import socket, json

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect('/var/run/openvswitch/db.sock')

query0 = {"method":"list_dbs", "params":[], "id": 0} 
query1 =  {"method":"transact", "params":['Open_vSwitch',{"op":"select","table":"Open_vSwitch","where":[["_uuid","==",["uuid","d8149874-5bd9-4a58-88e8-106603b8a0e9"]]]}], "id": 0}
query2 =  {"method":"transact", "params":['Open_vSwitch',{"op":"select","table":"Bridge","where":[["_uuid","==",["uuid","6f75d0a0-b2b8-489e-996b-d56172e02a5c"]]]}], "id": 0}
query3 =  {"method":"transact", "params":['Open_vSwitch',{"op":"select","table":"Bridge","where":[["_uuid","==",["uuid","6f75d0a0-b2b8-489e-996b-d56172e02a5c"]]],"columns":["flow_entries"]}], "id": 0}

print "method: list_dbs"
s.send(json.dumps(query0))
result0 = s.recv(4096)
print result0

print ""
print "method: transct, table: Open_vSwitch"
s.send(json.dumps(query1))
result1 = s.recv(4096)
print result1

print""
print "method: transact, table: Bridge"
s.send(json.dumps(query2))
result2 = s.recv(4096)
print result2

print ""
print "method: transact, table: Bridge, column: flow_entries"
s.send(json.dumps(query3))
result3 = s.recv(4096)
print result3

