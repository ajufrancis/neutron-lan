NLAN Command Usage
==================

DevOps operation
----------------
<pre>
- copy NLAN Agent and NLAN modules to remote routers
$ nlan_master.py --scpmod

- update OVSDB(conf.db) with new schema
$ nlan_master.py config.update_schema

- deploy network service with 'dvsdvr.yaml' state file
$ nlan_master.py dvsdvr.yaml

- deploy network service with logging enabled (either --info or --debug)
$ nlan_master.py dvsdvr.yaml --info

- execute raw command at remote routers (e.g., ping)
$ nlan-ssh.py openwrt1 --raw 'ping -c4 192.168.1.10'
</pre>

Maintenance
-----------
<pre>
- echo test
$ nlan_master.py test.echo hello world!

- show command list
$ nlan_master.py command.list

- ping test 
$ nlan_master.py test.ping 192.168.1.10

- shutdown all the routers
$ nlan_master.py system.halt

- reboot all the routers
$ nlan_master.py system.reboot

- show NLAN Agent environment
$ nlan_master.py system.env

- show command list
$ nlan_master command.list

- show current NLAN state in OVSDB (e.g., 'bridges' state)
$ nlan_master row.getrow bridges

- show current all NLAN states in OVSDB
$ nlan_master ovsdb.get_current_state

</pre>
