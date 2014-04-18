NLAN Command Usage
==================

DevOps operation
----------------
<pre>
- copy NLAN Agent and NLAN modules to remote routers
$ nlan --scpmod

- update OVSDB(conf.db) with new schema
$ nlan db.update

- deploy network service with 'dvsdvr.yaml' state file
$ nlan dvsdvr.yaml

- deploy network service with logging enabled (either --info or --debug)
$ nlan dvsdvr.yaml --info

- execute raw command at remote routers (e.g., ping)
$ nlan -t openwrt1 --raw 'ping -c4 192.168.1.10'
</pre>

Maintenance
-----------
<pre>
- echo test
$ nlan test.echo hello world!

- show command list
$ nlan command.list

- ping test 
$ nlan test.ping 192.168.1.10

- shutdown all the routers
$ nlan system.halt

- reboot all the routers
$ nlan system.reboot

- show NLAN Agent environment
$ nlan nlan.env

- show command list
$ nlan command.list

- show current all NLAN states in OVSDB
$ nlan db.state

</pre>
