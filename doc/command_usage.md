NLAN Command Usage
==================

DevOps operations
-----------------
<pre>
- copy NLAN Agent and NLAN modules to remote routers
$ nlan.py -m

- enable the rc script (/etc/init.d/nlan)
$ nlan.py system.rc enable

- update the rc script (/etc/init.d/nlan)
$ nlan.py system.rc update 

- update OVSDB(conf.db) with new schema
$ nlan.py db.update

- deploy a network service with a default state file
$ nlan.py deploy 

- deploy a network service with a default state file and with verbose output
$ nlan.py -v deploy

- deploy a network service with a specific state file (e.g., 'state.yaml')
$ nlan.py state.yaml 

- deploy network service with logging enabled (either --info or --debug)
$ nlan.py dvsdvr.yaml --info

- execute a raw command at remote routers (e.g., ping)
$ nlan.py -t openwrt1 --raw 'ping -c4 192.168.1.10'

- execute a raw command at all the routers on the roster
$ nlan.py --raw 'ping -c4 192.168.1.10'

- wait until all the routers on the roster become accessible (-w <timeout>)
$ nlan.py -w 100

- wait until all the routers on the roster become inaccessible (-w -<timeout>)
$ nlan.py -w -50 
</pre>

Working with a local Git repo
------------------------------
<pre>
- deploy a network service with a default state file (the state file is commited to the local git repo after the deployment)
$ nlan.py -G deploy 

- rollback to the previous state
$ nlan.py init.run
$ nlan.py -R deploy
</pre>

Scenario Runner
---------------
<pre>
- execute a scenario (e.g., a scenario 'all.yaml')
$ nlans.py all.yaml
</pre>

Maintenance
-----------
<pre>
- echo test
$ nlan.py test.echo Hello World!

- show command list
$ nlan.py command.list

- ping test 
$ nlan.py test.ping 192.168.1.10

- shutdown all the routers
$ nlan.py system.halt

- reboot all the routers
$ nlan.py system.reboot

- show NLAN Agent environment(shows built-in "__n__" variable)
$ nlan.py nlan.env

- show the current NLAN state in OVSDB
$ nlan.py db.state

- show the current NLAN state in OVSDB at a specific router
$ nlan.py -t openwrt1 db.state

- show a specific NLAN row in OVSDB (e.g., subnets vni=101)
$ nlan.py db.getrow subnets vni 101
</pre>


NLAN schema update
------------------
<pre>
Update 'schema.sh' at first. Then,
$ schema.sh
$ nlan -m
$ nlan db.update 
</pre>


Standard Python libraries
-------------------------
<pre>
- print OS name tupple
$ nlan.py os.uname

- list a names of all the entries in the directory
$ nlan.py os.listdir /etc/init.d
</pre>
