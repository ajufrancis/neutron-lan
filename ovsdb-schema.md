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
                  "min": 0, "max": "1"}},
       "gateway": {
         "type": {"key": {"type": "uuid",
                          "refTable": "NLAN_Gateway"},
                  "min": 0, "max": "1"}},
       "vxlan": {
         "type": {"key": {"type": "uuid",
                          "refTable": "NLAN_VXLAN"},
                  "min": 0, "max": "1"}},
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
     "indexes": [["name"]]}
<\pre>
     
