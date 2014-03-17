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
#     controller: '192.168.1.1:6633'
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
      - vid: '1'
        vni: '101'
        ip_dvr: '10.0.1.1/24'
        ip_vhost: '10.0.1.101/24'
        ports:
           - eth0.1 
#          - veth0.1
      - vid: '3'
        vni: '103'
        ip_dvr: '10.0.3.1/24'
        ip_vhost: '10.0.3.101/24'
        ports:
           - eth0.3
#          - veth0.3
      - vid: '2'
        vni: '1'
        ip_dvr: '192.168.100.1/24'
        ip_vhost: '192.168.100.101/24'

openwrt2:
   bridges: 
      ovs_bridges: enabled
      controller: '192.168.1.1:6633'
   vxlan:
      local_ip: '192.168.1.102'
      remote_ips:
         - '192.168.1.101'
         - '192.168.1.103'
         - '192.168.1.104'
   subnets:
      - vid: '1'
        vni: '101'
        ip_dvr: '10.0.1.1/24'
        ip_vhost: '10.0.1.102/24'
        ports:
           - eth0.1
#          - veth0.1
      - vid: '3'
        vni: '103'
        ip_dvr: '10.0.3.1/24'
        ip_vhost: '10.0.3.102/24'
        ports:
           - eth0.3
#          - veth0.3
      - vid: '2'
        vni: '1'
        ip_dvr: '192.168.100.2/24'
        default_gw: '192.168.100.1'
        ip_vhost: '192.168.100.102/24'


openwrt3:
   bridges:
     ovs_bridges: enabled
     controller: '192.168.1.1:6633'
   vxlan:
     local_ip: '192.168.1.103'
     remote_ips:
        - '192.168.1.101'
        - '192.168.1.102'
        - '192.168.1.104'
   subnets:
      - vid: '1'
        vni: '101'
        ip_dvr: '10.0.1.1/24'
        ip_vhost: '10.0.1.103/24'
        ports:
           - eth0.1
#          - veth0.1
      - vid: '3'
        vni: '103'
        ip_dvr: '10.0.3.1/24'
        ip_vhost: '10.0.3.103/24'
        ports:
           - eth0.3
#          - veth0.3
      - vid: '2'
        vni: '1'
        ip_dvr: '192.168.100.3/24'
        default_gw: '192.168.100.1'
        ip_vhost: '192.168.100.103/24'

rpi1:
   bridges:
      ovs_bridges: enabled
      controller: '192.168.1.1:6633'
   vxlan:
      local_ip: '192.168.1.104'
      remote_ips:
         - '192.168.1.101' 
         - '192.168.1.102'
         - '192.168.1.103'
   subnets:
      - vid: '1'
        vni: '101'
        ip_dvr: '10.0.1.1/24'
        ip_vhost: '10.0.1.104/24'
      - vid: '3'
        vni: '103'
        ip_dvr: '10.0.3.1/24'
        ip_vhost: '10.0.3.104/24'
      - vid: '2'
        vni: '1'
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
openwrt1:
   host: 192.168.1.101
   user: root
   passwd: root
   hardware: bhr_4grv

openwrt2:
   host: 192.168.1.102
   user: root
   passwd: root
   hardware: bhr_4grv

openwrt3:
   host: 192.168.1.103
   user: root
   passwd: root
   hardware: bhr_4grv

rpi1:
   host: 192.168.1.104
   user: root
   passwd: root
   hardware: raspberry_pi_b
</pre>

CRUD operation
--------------

neutron-lan defines the following CRUD operations:
- "batch": Initial config
- "add": Create
- "get": Read (not supported yet)
- "set": Update (not supported yet)
- "delete": Delete

To execute the latest scripts on the routers, all of the nlan-related agent-scripts are copied to the target routers' /tmp directory before executing CRUD operations(add/get/set/delete). nlan-ssh.py's "--scp" options allows us to copy any scripts to the target router's "/tmp" directory.

     Step 1:
     
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


Since I worked on mobile agent paradigm based on Java in the past, I have considered appliying the mobile-agent paradigm to neutron-lan. However, that approach must have a significant scaling problem and I have decided to take the approach described above.

<pre>
$ python nlan-ssh.py '*' --scp file1.py
</pre>

It is still under study about how to serialize the dict data: converted into str or pickle serialization format?

- TODO: Study whether a list of dict objects (i.e., collections.OrderedDict) is better or not as the argument...
- TODO: Study if 0mq over ssh works on OpenWRT.

Command modules and config modules
----------------------------------

Neutron-lan modules are categolized into two categories:

Category 1: Command Modules (like SaltStack execution modules):
- init
- (other modules to be added)

Category 2: Config Modules (like SaltStack state modules):
- bridges
- gateway
- vxlan
- subnets
- (other modules to be added) 

To support CRUD operations, each config module should have "add", "get", "set" and "delete" functions in it.

For example,
- "init.run()" initializes the local system setting
- "bridges.add(...)" adds bridges required for neutron-lan

The config modules may interwork with OVSDB to create/read/update/delete local config, and a script under /etc/init.d reads the config in OVSDB to configure the system when rebooting.

OVSDB schema for neutron-lan is defined [in this page](https://github.com/alexanderplatz1999/neutron-lan/blob/master/ovsdb-schema.md)





