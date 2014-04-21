NLAN Command Usage
==================

DevOps operation
----------------
<pre>
- copy NLAN Agent and NLAN modules to remote routers
$ nlan.py --scpmod

- update OVSDB(conf.db) with new schema
$ nlan.py db.update

- deploy network service with 'dvsdvr.yaml' state file
$ nlan.py dvsdvr.yaml

- deploy network service with logging enabled (either --info or --debug)
$ nlan.py dvsdvr.yaml --info

- execute raw command at remote routers (e.g., ping)
$ nlan.py -t openwrt1 --raw 'ping -c4 192.168.1.10'
</pre>

Maintenance
-----------
<pre>
- echo test
$ nlan.py test.echo hello world!

- show command list
$ nlan.py command.list

- ping test 
$ nlan.py test.ping 192.168.1.10

- shutdown all the routers
$ nlan.py system.halt

- reboot all the routers
$ nlan.py system.reboot

- show NLAN Agent environment
$ nlan.py nlan.env

- show command list
$ nlan.py command.list

- show current all NLAN states in OVSDB
$ nlan.py db.state

</pre>
