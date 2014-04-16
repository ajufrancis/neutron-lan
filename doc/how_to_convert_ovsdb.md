OVSDB schema upgrade
--------------------
Upgrading OVSDB(conf.db) with new schema is quite easy. Just type the following command:
$ python nlan_master.py config.update_schema

Manual upgrade
--------------
For OpenWrt,

$ /etc/init.d/openvswitch stop
$ ovsdb-tool convert /etc/openvswitch/conf.db /tmp/vswitch.schema_2.0.0
$ /etc/init.d/openvswitch start

Note that ovsdb.py requires the following package:
$ opkg install python-json

