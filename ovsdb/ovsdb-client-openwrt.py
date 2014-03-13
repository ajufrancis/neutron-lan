"""
2014/3/13

$ pip install python-json

To check uuid of Open_vSwitch and Bridge, type these:
$ ovs-vsctl show
$ ovs-vsctl list Bridge 

then modify the code.

"""

import socket, json

s = '{"test": [3, 4, 5] ,"test2":null}'
d = json.read(s)
print "This is a Python dictionary object: " + str(d)
print "This is a JSON string: " + json.write(d)
print "This is a value None in a Python dictionary: " + str(d['test2'])
print ""

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect('/var/run/db.sock')

query0 = {"method":"list_dbs", "params":[], "id": 0}
query1 =  {"method":"transact", "params":['Open_vSwitch',{"op":"select","table":"Open_vSwitch","where":[["_uuid","==",["uuid","07178244-eed9-4018-a424-c71d2a4290d4"]]]}], "id": 0}
query2 =  {"method":"transact", "params":['Open_vSwitch',{"op":"select","table":"Bridge","where":[["_uuid","==",["uuid","83e0464f-f997-4ac4-a284-e3dc4b94d13f"]]]}], "id": 0}
query3 =  {"method":"transact", "params":['Open_vSwitch',{"op":"select","table":"Bridge","where":[["_uuid","==",["uuid","83e0464f-f997-4ac4-a284-e3dc4b94d13f"]]],"columns":["name","ports"]}], "id": 0}

dumps = json.JsonWriter().write

print "method: list_dbs"
s.send(dumps(query0))
result0 = s.recv(4096)
print result0

print ""
print "method: transct, table: Open_vSwitch"
s.send(dumps(query1))
result1 = s.recv(4096)
print result1

print""
print "method: transact, table: Bridge"
s.send(dumps(query2))
result2 = s.recv(4096)
print result2

print ""
print "method: transact, table: Bridge, column: name, ports"
s.send(dumps(query3))
result3 = s.recv(4096)
print result3
