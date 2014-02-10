Modeling neutron-lan
====================

Model-driven/data-driven approach
---------------------

There are several ways for calling a remote python script on the router:
- RPC (XML-RPC, JSON-RPC etc)
- Mesaging (XMPP, AMQP, 0MP etc)
- Calling a remote python script via ssh

Because of the memory/storage limitations of OpenWRT routers, I will adopt the third one: calling via ssh.

Then I have been considering which one is better, api-driven or model-driven, since I have learned from OpenDaylight about model-driven service abstraction layer (MD-SAL): network modeling by using YANG data format and loose coupling between applications and drivers (south-bound APIs). I suspect the reason why ODL has adopted YANG is that Java does not have such a modeling language on its own and YANG is language-neutral.

And I have learned from SaltStack that YAML is a very simple modeling language. Although YANG is the best for modeling network, I would rather take YAML as a neutron-lan modeling language. YAML data represents neutron-lan states, and applications on the controller modifies the states via "nlan-ssh.py".

YAML for modeling neutron-lan
-----------------------------

This is an example of a model that represents neutron-lan:

<pre>
openwrt1:
   bridges: true
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
      - vid: '3'
        vni: '103'
        ip_dvr: '10.0.3.1/24'
        ip_vhost: '10.0.3.101/24'

openwrt2:
   bridges: true
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
      - vid: '3'
        vni: '103'
        ip_dvr: '10.0.3.1/24'
        ip_vhost: '10.0.3.102/24'

openwrt3:
   bridges: true
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
      - vid: '3'
        vni: '103'
        ip_dvr: '10.0.3.1/24'
        ip_vhost: '10.0.3.103/24'


rpi1:
   bridges: true
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
</pre>

If an application wants to change some state on the model, for example, wants to add a subnet, then the application askes "nlan-ssh.py" to add the subnet. "nlan-ssh.py" generates YAML data corresponding to the new subnet, then convert it into Python dict object. The dict object is serialized and sent to "nlan-agent.py" on the OpenWRT router (and possibly other routers than OpenWRT in future). "nlan-agent.py" deserializes the data, analyzes it and routes the request to a corresponding method. "nlan-ssh.py" inserts the YAML data into the states after having received a success reply from "nlan-agent.py".

YAML data (neutron-lan states) and "nlan-ssh.py" constitute Simple Service Abstraction Layer for neutron-lan.

Simple Service Abstraction Layer is a representaion of neutron-lan network in a model-driven or data-driven manner.

               ----------
              /YAML data/ neutron-lan states
             -----------
                  ^
                  |       Serialized into str or by "pickle"?             +--> method A -- cli/uci --> router
                  |              ----------                               |
      appl. --> nlan-ssh.py --- /dict data/ over ssh ---> nlan-agent.py --+--> method B -- cli/uci --> router
                  |            -----------                                |
                  |           CRUD operation                              +--> method C -- cli/uci --> router
                  V
              -----------
             / Roster   /  
            ------------
             
             

"nlan-ssh.py" can call multiple methods on the router in one request, and "nlan-agent.py" collects all the results from the methods.

             
               ----------
              /YAML data/ neutron-lan states
             -----------
                  ^
                  |       Serialized into str or by "pickle"?             +--- method A
                  |              ----------                               |
      appl. <-- nlan-ssh.py <-- /dict data/ over ssh ---- nlan-agent.py <-+--- method B
                  |            -----------                                |
                  V           CRUD operation                              +--- method C
              -----------
             / Roster   /  
            ------------

"nlan-agent.py" returns the results in the form of a Python dict object to "nlan.py".

"nlan-ssh.py' can execute row commands on the routers with '-r' option, similar to salt-ssh's '-r' option.

The Python dict object will be like this:

<pre>
sample_dict_args = {
'bridges': True,
'vxlan':{
	'local_ip': '192.168.57.101',
	'remote_ips': ['192.168.57.102', '192.168.57.103']
	},
'subnets': [{
	'vid': '1',
	'vni': '101',
	'ip_dvr': '10.0.1.1/24',
	'ip_vhost': '10.0.1.101/24'
	},{
	'vid': '3',
	'vni': '103',
	'ip_dvr': '10.0.3.1/24',
	'ip_vhost': '10.0.3.101/24'
	}]
}
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
- "add": Create
- "get": Read
- "set": Update
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
    [nlan-ssh.py] - - -/Python dict   / - - - - - > Agent-scripts under "/tmp" 
                      ---------------
                  < - - - - - - - - - - - - stdout
                  < - - - - - - - - - - - - stderr


Since I worked on mobile agent paradigm based on Java primordial class loader in late 1990's for managing networking equipment, I have considered using mobile-agent paradigm for executing the latest scripts for neutron-lan always. However, that approach must have a significant scaling problem and I have decided to take the approach described above.

<pre>
$ python nlan-ssh.py '*' --scp file1.py
</pre>

It is still under study about how to serialize the dict data: converted into str or pickle serialization format?

- TODO: Study whether a list of dict objects (i.e., collections.OrderedDict) is better or not as the argument...
- TODO: Study if 0mq over ssh works on OpenWRT.
