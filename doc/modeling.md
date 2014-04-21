YAML-based network modeling
===========================

Model-driven/data-driven approach
---------------------------------

There are several ways for calling a remote python script on the router:
- RPC such as NETCONF or OVSDB (XML-RPC, JSON-RPC etc)
- Mesaging (XMPP, AMQP, 0MP etc)
- SSH

Because of the memory/storage limitations of OpenWRT routers, I have adopted SSH.

Then I have considered which one is better, api-driven or model-driven, since I have learned from OpenDaylight about model-driven service abstraction layer (MD-SAL): modeling an inventory of network elements and network topology in YANG data format, and loose coupling between applications and drivers (south-bound APIs).

And I have learned from SaltStack that YAML is a very simple modeling language. Although YANG is the best for modeling network, I would rather take YAML as a neutron-lan modeling language.

YAML for modeling neutron-lan
-----------------------------

Refer to [neutron-lan YAML state file](../nlan/dvsdvr.yaml).

When an administrator has finished modifying the state file, he or she executes a neutron-lan command "nlan_master.py" to generete CRUD operations (add/delete/set) in the form of Python OrderedDict objects, comparing the file and the one archived in a local git repo.

The OrderedDict objects are serialized into string data and sent to target OpenWRT routers. "nlan_agent.py" deserializes the data, analyzes it and routes the requests to corresponding modules.

               /////////// Global CMDB /////////////                  ////// Local CMDB //////
               Local file             Local git repo                        
               ----------             ----------                            ----------
              /YAML data/ .. diff .. /YAML data/                           / OVSDB   /
             -----------            -----------                           -----------
                              ^                                                 ^
                              |                                                 |
                              |         Serialized into str           (OVSDB protocol)     +--> module A
                              |              ----------                         |          |
                            nlan.py ------ /dict data/ stdin over ssh ---> nlan_agent.py --+--> module B
                              |           -----------                                      |
                              |           CRUD operations                                  +--> module C
                              V       <---- stdout/stderr over ssh -------
                         -----------
                        / Roster   /  
                       ------------
             
Refer to [neutron-lan roster file](../nlan/roster.yaml).

"nlan.py" can issue multiple requests to routers in parallel at the same time.

"nlan-agent.py" returns the results to "nlan.py" via stdout/stderr over ssh.

"nlan.py' can also execute raw commands on the routers with '--raw' option, similar to salt-ssh's '-r' option.

The Python dict object will be like this:

<pre>
"OrderedDict([('bridges', {'ovs_bridges': 'enabled'}), ('gateway', {'network': 'eth0.2', 'rip': 'enabled'}), ('vxlan', {'remote_ips': ['192.168.1.103', '192.168.1.102', '192.168.1.104'], 'local_ip': '192.168.1.101'}), ('subnets', {('vni', 1): {'ip_vhost': '192.168.100.101/24', 'ip_dvr': '192.168.100.1/24', 'peers': ['192.168.1.102', '192.168.1.103'], 'vid': 2, 'vni': 1}, ('vni', 103): {'peers': ['192.168.1.102', '192.168.1.103'], 'vid': 3, 'ip_vhost': '10.0.3.101/24', 'vni': 103, 'ip_dvr': '10.0.3.1/24', 'ports': ['eth0.3']}, ('vni', 1001): {'peers': ['192.168.1.104'], 'vid': 1, 'ip_vhost': '10.0.1.101/24', 'vni': 1001, 'ip_dvr': '10.0.1.1/24', 'mode': 'hub', 'ports': ['eth0.1']}})])"
</pre>



CRUD operation
--------------
neutron-lan defines the following CRUD operations:
- "add": Create
- "get": Read
- "update": Update
- "delete": Delete

[yamldiff.py](https://github.com/alexanderplatz1999/neutron-lan/blob/master/nlan/yamldiff.py) is responsible for generating CRUD operations.

nlan_ssh.py's "--scpmod" option allows me to copy the nlan modules to the target router's "/opt/nlan" directory.

     Step 1:
     
                         ---------------              Target routers
     [nlan.py] ---------/Python scripts/-----------> "/opt/nlan" directory
                        --------------- /
                        ----------------
      
                         ---------------              Target routers
     [nlan.py] ---------/Python scripts/-----------> "/opt/nlan" directory
                        --------------- /
                        ----------------
                               :
                          
     Step 2:
     
                 stdin  ---------------              Target routers
    [nlan.py] ---------/Python dict   / - - - - - > Agent-scripts under "/opt/nlan" 
                      ---------------
                  < - - - - - - - - - - - - stdout
                  < - - - - - - - - - - - - stderr



Command modules and config modules
----------------------------------

Neutron-lan modules are categolized into three categories:

Category 1: NLAN Command Modules (like SaltStack execution modules):
- init
- system
- test
- (other modules to be added)

For example, the following will reboot all the routers on the roster: 
<pre>
$ python nlan_master.py system.reboot 
</pre>

Category 2: NLAN Config Modules (like SaltStack state modules):
- bridges
- services
- gateway
- vxlan
- subnets
- (other modules to be added) 

nlan.py reads a YAML file and invoke corresponding config modules on remote routers:
<pre>
$ python nlan.py dvsdvr.yaml
</pre>

Category 3: Other python modules
- Any modules that can be reachable via 'sys.path'. For example, to access 'os.getenv':

For example, the following will invoke os.getenv module to obtain PATH environement variable:
<pre>
$ python nlan.py os.getenv PATH
</pre>

To support CRUD operations, each config module should implement "add", "get", "update" and "delete" functions in it.

For example,
- "init.run()" initializes the local system setting
- "bridges.add(...)" adds bridges required for neutron-lan

The config modules interworks with OVSDB (Open vSwtich Database) to create/read/update/delete local config, and my plan is to write a script that reads the config in OVSDB to re-configure the system when rebooting.

OVSDB schema for neutron-lan is defined [in this page](https://github.com/alexanderplatz1999/neutron-lan/blob/master/doc/ovsdb-schema.md)

All the way from YAML to OVSDB
------------------------------

The following command reads a local YAML file, generates CRUD operations and invokes modules at each router:
<pre>
$ python nlan.py dvsdvr.yaml
</pre>

Each remote module stores its 'model' in OVSDB at the end of the configuration process.

Here is a sample output of 'ovsdb-client dump Open_vSwitch':

At "rpi1",
<pre>
$ ovsdb-client dump Open_vSwitch

                        :

NLAN table
_uuid                                bridges                              gateway services                               subnets                                                                      vxlan
------------------------------------ ------------------------------------ ------- -------------------------------------- ---------------------------------------------------------------------------- ------------------------------------
2928cfe4-1615-4e5a-ad56-5e10b881a9bb b96c47b6-1ace-4ea4-af7c-946d2623cacc []      [bf9038c4-5b02-45d0-adfd-51176b24ca49] [376c0b57-9108-44c1-8fcd-d28634953977, d11f17e3-1457-4a24-b7fd-34710af48ca2] 42da0c85-688a-4231-9082-5e43a63756bd

NLAN_Bridges table
_uuid                                controller ovs_bridges
------------------------------------ ---------- -----------
b96c47b6-1ace-4ea4-af7c-946d2623cacc []         enabled

NLAN_Gateway table
_uuid network rip
----- ------- ---

NLAN_Service table
_uuid                                chain                  name
------------------------------------ ---------------------- --------
bf9038c4-5b02-45d0-adfd-51176b24ca49 ["dmz.1001", "mz.101"] "snort1"

NLAN_Subnet table
_uuid                                default_gw ip_dvr ip_vhost mode peers                              ports        vid vni
------------------------------------ ---------- ------ -------- ---- ---------------------------------- ------------ --- ----
376c0b57-9108-44c1-8fcd-d28634953977 []         []     []       []   ["192.168.1.101"]                  ["dmz.1001"] 111 1001
d11f17e3-1457-4a24-b7fd-34710af48ca2 []         []     []       []   ["192.168.1.102", "192.168.1.103"] ["mz.101"]   1   101

NLAN_VXLAN table
_uuid                                local_ip        remote_ips
------------------------------------ --------------- ---------------------------------------------------
42da0c85-688a-4231-9082-5e43a63756bd "192.168.1.104" ["192.168.1.101", "192.168.1.102", "192.168.1.103"]
</pre>


At "openwrt1",
<pre>
$ ovsdb-client dump Open_vSwitch

                        :
NLAN table
_uuid                                bridges                              gateway                              services subnets
                                                                               vxlan
------------------------------------ ------------------------------------ ------------------------------------ -------- ------------------------------------
------------------------------------------------------------------------------ ------------------------------------
c34d377e-b97f-48ab-bef9-8ff46ba8719b a93fc4d8-2984-4971-b9ae-f3b701c96a62 0b7c575e-e6cb-4d73-b492-2fc53b9f912c []       [04520957-a9ed-41c9-b839-fd89caa052b
0, 75558f79-cd81-42e0-850d-e1d5419dd91c, d0b0c61a-147e-4488-972a-e3668ac4230d] 895c1751-2805-4620-9baa-8a29de5b82b4

NLAN_Bridges table
_uuid                                controller ovs_bridges
------------------------------------ ---------- -----------
a93fc4d8-2984-4971-b9ae-f3b701c96a62 []         enabled

NLAN_Gateway table
_uuid                                network  rip
------------------------------------ -------- -------
0b7c575e-e6cb-4d73-b492-2fc53b9f912c "eth0.2" enabled

NLAN_Service table
_uuid chain name
----- ----- ----

NLAN_Subnet table
_uuid                                default_gw ip_dvr             ip_vhost             mode peers                              ports      vid vni
------------------------------------ ---------- ------------------ -------------------- ---- ---------------------------------- ---------- --- ----
04520957-a9ed-41c9-b839-fd89caa052b0 []         "10.0.1.1/24"      "10.0.1.101/24"      hub  ["192.168.1.104"]                  ["eth0.1"] 1   1001
d0b0c61a-147e-4488-972a-e3668ac4230d []         "10.0.3.1/24"      "10.0.3.101/24"      []   ["192.168.1.102", "192.168.1.103"] ["eth0.3"] 3   103
75558f79-cd81-42e0-850d-e1d5419dd91c []         "192.168.100.1/24" "192.168.100.101/24" []   ["192.168.1.102", "192.168.1.103"] []         2   1

NLAN_VXLAN table
_uuid                                local_ip        remote_ips
------------------------------------ --------------- ---------------------------------------------------
895c1751-2805-4620-9baa-8a29de5b82b4 "192.168.1.101" ["192.168.1.102", "192.168.1.103", "192.168.1.104"]
</pre>


At "openwrt2",
<pre>
$ ovsdb-client dump Open_vSwitch

                        :
NLAN table
_uuid                                bridges                              gateway services subnets
                                                  vxlan
------------------------------------ ------------------------------------ ------- -------- -----------------------------------------------------------------
------------------------------------------------- ------------------------------------
bfa24ce6-5d69-4cd3-adfb-fdaffa0ba561 b7c5bdfa-de84-4e59-a673-3a718b3705a6 []      []       [26c7c4a6-fc44-4c41-bcc1-806e4281834b, 34ef67ed-334b-4d9e-a3fa-bd
8795042f92, eae7e8fb-aeca-4400-bd66-30dc33ca6438] c4dc4f8a-d0ad-4913-bc1a-bf05db8d4823

NLAN_Bridges table
_uuid                                controller ovs_bridges
------------------------------------ ---------- -----------
b7c5bdfa-de84-4e59-a673-3a718b3705a6 []         enabled

NLAN_Gateway table
_uuid network rip
----- ------- ---

NLAN_Service table
_uuid chain name
----- ----- ----

NLAN_Subnet table
_uuid                                default_gw      ip_dvr             ip_vhost             mode      peers                              ports      vid vni
------------------------------------ --------------- ------------------ -------------------- --------- ---------------------------------- ---------- --- ---
eae7e8fb-aeca-4400-bd66-30dc33ca6438 []              "10.0.1.1/24"      "10.0.1.102/24"      spoke_dvr ["192.168.1.103", "192.168.1.104"] ["eth0.1"] 1   101
26c7c4a6-fc44-4c41-bcc1-806e4281834b []              "10.0.3.1/24"      "10.0.3.102/24"      []        ["192.168.1.101", "192.168.1.103"] ["eth0.3"] 3   103
34ef67ed-334b-4d9e-a3fa-bd8795042f92 "192.168.100.1" "192.168.100.2/24" "192.168.100.102/24" []        ["192.168.1.101", "192.168.1.103"] []         2   1

NLAN_VXLAN table
_uuid                                local_ip        remote_ips
------------------------------------ --------------- ---------------------------------------------------
c4dc4f8a-d0ad-4913-bc1a-bf05db8d4823 "192.168.1.102" ["192.168.1.101", "192.168.1.103", "192.168.1.104"]
</pre>

