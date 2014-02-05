Modeling neutron-lan
====================

(still under study... api drivern or model driven???)

Model-driven approach
---------------------

There are several ways for calling a remote python script on the router:
- RPC (XML-RPC, JSON-RPC etc)
- Mesaging (XMPP, AMQP, 0MP etc)
- Calling a remote python script via ssh

Because of the memory/storage limitations of OpenWRT routers, I will adopt the third one: calling via ssh.

Then I have been considering which one is better, api-driven or model-driven, since I have learned from OpenDaylight about model-driven service abstraction layer (MD-SAL): network modeling by using YANG data format and loose coupling between applications and drivers (south-bound APIs).

And I have learned from SaltStack that YAML is a very simple modeling language. Although YANG is the best for modeling network, I would rather take YAML as a neutron-lan modeling language. YAML data represents neutron-lan states, and applications on the controller modifies the states via "nlan.py".

YAML for modeling neutron-lan
-----------------------------

This is an example of a model that represents neutron-lan:

<pre>
bridges: True
vxlan:
	local_ip: '192.168.57.101'
	remote_ips:
		- '192.168.57.102'
		- '192.168.57.103'
subnets:
	- vid: '1'
	  vni: '101'
	  ip_dvr: '10.0.1.1/24'
	  ip_vhost: '10.0.1.101/24'
	- vid: '3'
	  vni: '103'
	  ip_dvr: '10.0.3.1/24'
	  ip_vhost: '10.0.3.101/24'
</pre>

If an application wants to change some state on the model, for example, wants to add a subnet, then the application askes "nlan.py" to add the subnet. "nlan.py" generates YAML data corresponding to the new subnet, then convert it into Python dict object. The dict object is serialized and sent to "nlan-agent.py" on the OpenWRT router (and possibly other routers than OpenWRT in future). "nlan-agent.py" deserializes the data, analyzes it and routes the request to a corresponding method. "nlan.py" inserts the YAML data into the states after having received a success reply from "nlan-agent.py".

<pre>

               -----------
              /YAML data/ neutron-lan states
             -----------
                  ^
                  |       Serialized into str or by "pickle"?
                  |               ----------
application --> nlan.py -------- /dict data/ over ssh ---> nlan-agent.py
                                -----------
             get, add, set, delete operations

</pre>

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

It is still under study about how to serialize the dict data: converted into str or pickle serialization format?

TODO: Study whether a list of dict objects (i.e., collections.OrderedDict) is better or not as the argument...