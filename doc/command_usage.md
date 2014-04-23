NLAN Command Usage
==================

DevOps operation
----------------
<pre>
- copy NLAN Agent and NLAN modules to remote routers
$ nlan.py -m

- enable the rc script (/etc/init.d/nlan)
$ nlan.py system.rc enable

- update the rc script (/etc/init.d/nlan)
$ nlan.py system.rc update 

- update OVSDB(conf.db) with new schema
$ nlan.py db.update

- deploy network service with 'dvsdvr.yaml' state file
$ nlan.py dvsdvr.yaml

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
</pre>


Standard Python libraries
-------------------------
<pre>
- print OS name tupple
$ nlan.py os.uname

- list a names of all the entries in the directory
$ nlan.py os.listdir /etc/init.d
</pre>
