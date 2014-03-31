YAML-based network modeling
===========================

Model-driven/data-driven approach
---------------------------------

There are several ways for calling a remote python script on the router:
- RPC such as NETCONF or OVSDB (XML-RPC, JSON-RPC etc)
- Mesaging (XMPP, AMQP, 0MP etc)
- SSH

Because of the memory/storage limitations of OpenWRT routers, I will adopt SSH.

Then I have been considering which one is better, api-driven or model-driven, since I have learned from OpenDaylight about model-driven service abstraction layer (MD-SAL): modeling an inventory of network elements and network topology in YANG data format, and loose coupling between applications and drivers (south-bound APIs).

And I have learned from SaltStack that YAML is a very simple modeling language. Although YANG is the best for modeling network, I would rather take YAML as a neutron-lan modeling language.

YAML for modeling neutron-lan
-----------------------------

This is an example of a model that represents neutron-lan:

<pre>
openwrt1:
   bridges: 
      ovs_bridges: enabled
#      controller: '192.168.1.1:6633'
   gateway:
      rip: enabled
      network: eth0.2
#     network: eth2 
   vxlan:
      local_ip: '192.168.1.101'
      remote_ips:
         - '192.168.1.102'
         - '192.168.1.103'
         - '192.168.1.104'
   subnets:
      - vid: 1
        vni: 101
        ip_dvr: '10.0.1.1/24'
        ip_vhost: '10.0.1.101/24'
        ports:
           - eth0.1 
#          - veth0.1
      - vid: 3
        vni: 103
        ip_dvr: '10.0.3.1/24'
        ip_vhost: '10.0.3.101/24'
        ports:
           - eth0.3
#          - veth0.3
      - vid: 2
        vni: 1
        ip_dvr: '192.168.100.1/24'
        ip_vhost: '192.168.100.101/24'

openwrt2:
   bridges: 
      ovs_bridges: enabled
#     controller: '192.168.1.1:6633'
   vxlan:
      local_ip: '192.168.1.102'
      remote_ips:
         - '192.168.1.101'
         - '192.168.1.103'
         - '192.168.1.104'
   subnets:
      - vid: 1
        vni: 101
        ip_dvr: '10.0.1.1/24'
        ip_vhost: '10.0.1.102/24'
        ports:
           - eth0.1
#          - veth0.1
      - vid: 3
        vni: 103
        ip_dvr: '10.0.3.1/24'
        ip_vhost: '10.0.3.102/24'
        ports:
           - eth0.3
#          - veth0.3
      - vid: 2
        vni: 1
        ip_dvr: '192.168.100.2/24'
        default_gw: '192.168.100.1'
        ip_vhost: '192.168.100.102/24'


openwrt3:
   bridges:
     ovs_bridges: enabled
#    controller: '192.168.1.1:6633'
   vxlan:
     local_ip: '192.168.1.103'
     remote_ips:
        - '192.168.1.101'
        - '192.168.1.102'
        - '192.168.1.104'
   subnets:
      - vid: 1
        vni: 101
        ip_dvr: '10.0.1.1/24'
        ip_vhost: '10.0.1.103/24'
        ports:
           - eth0.1
#          - veth0.1
      - vid: 3
        vni: 103
        ip_dvr: '10.0.3.1/24'
        ip_vhost: '10.0.3.103/24'
        ports:
           - eth0.3
#          - veth0.3
      - vid: 2
        vni: 1
        ip_dvr: '192.168.100.3/24'
        default_gw: '192.168.100.1'
        ip_vhost: '192.168.100.103/24'

rpi1:
   bridges:
      ovs_bridges: enabled
#     controller: '192.168.1.1:6633'
   vxlan:
      local_ip: '192.168.1.104'
      remote_ips:
         - '192.168.1.101' 
         - '192.168.1.102'
         - '192.168.1.103'
   subnets:
      - vid: 1
        vni: 101
        ip_dvr: '10.0.1.1/24'
        ip_vhost: '10.0.1.104/24'
      - vid: 3
        vni: 103
        ip_dvr: '10.0.3.1/24'
        ip_vhost: '10.0.3.104/24'
      - vid: 2
        vni: 1
        ip_dvr: '192.168.100.4/24'
        default_gw: '192.168.100.1'
        ip_vhost: '192.168.100.104/24'
</pre>

When an administrator has finished modifying the state file, he or she executes a neutron-lan command "nlan-master.py" to generete CRUD operations (add/delete/set) in the form of Python dict objects, comparing the file and the one archived in a local git repo.

The dict objects are serialized into string data and sent to target OpenWRT routers. "nlan-agent.py" deserializes the data, analyzes it and routes the requests to corresponding methods.

               /////////// Global CMDB /////////////                  ////// Local CMDB //////
               Local file             Local git repo                        
               ----------             ----------                            ----------
              /YAML data/ .. diff .. /YAML data/                           / OVSDB   /
             -----------            -----------                           -----------
                              ^                                                 ^
                              |                                                 |
                              |         Serialized into str           (OVSDB protocol)     +--> method A
                              |              ----------                         |          |
                       nlan-master.py ---- /dict data/ stdin over ssh ---> nlan-agent.py --+--> method B
                              |           -----------                                      |
                              |           CRUD operations                                  +--> method C
                              V       <---- stdout/stderr over ssh -------
                         -----------
                        / Roster   /  
                       ------------
             
"nlan-master.py" can call multiple methods on the router in one request, and "nlan-agent.py" collects all the results from the methods. Also "nlan-master.py" can issue multiple requests in parallel at the same time.

"nlan-agent.py" returns the results to "nlan.py" via stdout/stderr over ssh.

"nlan-ssh.py' can execute raw commands on the routers with '-r' option, similar to salt-ssh's '-r' option.

The Python dict object will be like this:

<pre>
"{'bridges': {'ovs_bridges': 'enabled'}, 'gateway': {'network': 'eth0.2', 'rip': 'enabled'}, 'vxlan': {'remote_ips': ['192.168.1.102', '192.168.1.103', '192.168.1.104'], 'local_ip': '192.168.1.101'}, 'subnets': [{'ip_dvr': '10.0.1.1/24', 'ip_vhost': '10.0.1.101/24', 'vid': '1', 'vni': '101', 'ports': ['eth0.1']}, {'ip_dvr': '10.0.3.1/24', 'ip_vhost': '10.0.3.101/24', 'vid': '3', 'vni': '103', 'ports': ['eth0.3']}, {'ip_dvr': '192.168.100.1/24', 'ip_vhost': '192.168.100.101/24', 'vid': '2', 'vni': '1'}]}"
</pre>

And the roster file will be like this:
<pre>   
# 2014/2/6
# Roster of OpenWRT routers. 
#

openwrt1:
   host: 192.168.1.101
   user: root
   passwd: root
   platform: openwrt 

openwrt2:
   host: 192.168.1.102
   user: root
   passwd: root
   platform: openwrt 

openwrt3:
   host: 192.168.1.103
   user: root
   passwd: root
   platform: openwrt 

rpi1:
   host: 192.168.1.104
   user: root
   passwd: root
   platform: raspbian
</pre>

CRUD operation
--------------
neutron-lan defines the following CRUD operations:
- "batch": Initial config (to be depricated)
- "add": Create
- "get": Read
- "update": Update
- "delete": Delete

[yamldiff.py](https://github.com/alexanderplatz1999/neutron-lan/blob/master/script/yamldiff.py) is responsible for generating CRUD operations.

To execute the latest scripts on the routers, all of the nlan-related agent-scripts are copied to the target routers' 
/tmp directory before executing CRUD operations(add/get/set/delete). nlan-ssh.py's "--scp" options allows us to copy any
scripts to the target router's "/tmp" directory.
     Step 1:
     
                         ---------------              Target routers
     [nlan-ssh.py] -----/Python scripts/-----------> "/tmp" directory
                        --------------- /
                        ----------------
      
                         ---------------              Target routers
     [nlan-ssh.py] -----/Python scripts/-----------> "/tmp" directory
                        --------------- /
                        ----------------
                               :
                          
     Step 2:
     
                 stdin  ---------------              Target routers
    [nlan-master.py] --/Python dict   / - - - - - > Agent-scripts under "/tmp" 
                      ---------------
                  < - - - - - - - - - - - - stdout
                  < - - - - - - - - - - - - stderr


<pre>
$ python nlan-ssh.py '*' --scp file1.py
</pre>

It is still under study about how to serialize the dict data: converted into str or pickle serialization format?

- TODO: Study whether a list of dict objects (i.e., collections.OrderedDict) is better or not as the argument...
- TODO: Study if 0mq over ssh works on OpenWRT.

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
$ python nlan-master.py system.reboot 
</pre>

Category 2: NLAN Config Modules (like SaltStack state modules):
- bridges
- gateway
- vxlan
- subnets
- (other modules to be added) 

The following will read a YAML file and invoke corresponding config modules on remote routers:
<pre>
$ python nlan-master.py dvsdvr.yaml
</pre>

Category 3: Other python modules
- Any modules that can be reachable via 'sys.path'. For example, to access 'os.getenv':

For example, the following will invoke os.getenv module to obtain PATH environement variable:
<pre>
$ python nlan-master.py os.getenv PATH
</pre>

To support CRUD operations, each config module should have "add", "get", "update" and "delete" functions in it.

For example,
- "init.run()" initializes the local system setting
- "bridges.add(...)" adds bridges required for neutron-lan

The config modules may interwork with OVSDB to create/read/update/delete local config, and a script under /etc/init.d reads the config in OVSDB to configure the system when rebooting.

OVSDB schema for neutron-lan is defined [in this page](https://github.com/alexanderplatz1999/neutron-lan/blob/master/ovsdb-schema.md)

All the way from YAML to OVSDB
------------------------------

The following command reads a local YAML file, generates CRUD operations and invokes modules at each router:
<pre>
$ python nlan-master.py dvsdvr.yaml
</pre>

Each remote module stores its 'model' in OVSDB at the end of the configuration process.

Here is a sample output of 'ovsdb-client dump Open_vSwitch':
<pre>
NLAN table
_uuid                                bridges                              gateway                              subnets
                                                                              vxlan
------------------------------------ ------------------------------------ ------------------------------------ -------------------------------------
----------------------------------------------------------------------------- ------------------------------------
8c0dda8d-1cf8-4f4b-a70f-a63b1050215c af06efd9-df9b-485c-8301-da7d43037003 74f0b0b5-e68b-48e2-8c6b-09b440961dc1 [9f992391-ec60-4ca8-8af7-4fe894d32ab3
, c91f5e75-9f91-47f7-b0c5-81653a8d57c2, e120f2d7-13fc-4da0-8a08-c3b0a97a985c] 6a578ec1-dcbb-4c40-a6e3-499261243b42

NLAN_Bridges table
_uuid                                controller ovs_bridges
------------------------------------ ---------- -----------
af06efd9-df9b-485c-8301-da7d43037003 ""         enabled

NLAN_Gateway table
_uuid                                network  rip
------------------------------------ -------- -------
74f0b0b5-e68b-48e2-8c6b-09b440961dc1 "eth0.2" enabled

NLAN_Subnet table
_uuid                                ip_dvr             ip_vhost             ports      vid vni
------------------------------------ ------------------ -------------------- ---------- --- ---
e120f2d7-13fc-4da0-8a08-c3b0a97a985c "10.0.1.1/24"      "10.0.1.101/24"      ["eth0.1"] 1   101
9f992391-ec60-4ca8-8af7-4fe894d32ab3 "10.0.3.1/24"      "10.0.3.101/24"      ["eth0.3"] 3   103
c91f5e75-9f91-47f7-b0c5-81653a8d57c2 "192.168.100.1/24" "192.168.100.101/24" []         2   1

NLAN_VXLAN table
_uuid                                local_ip        remote_ips
------------------------------------ --------------- ---------------------------------------------------
6a578ec1-dcbb-4c40-a6e3-499261243b42 "192.168.1.101" ["192.168.1.102", "192.168.1.103", "192.168.1.104"]
</pre>


