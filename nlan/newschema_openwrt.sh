#!/bin/ash

/etc/init.d/openvswitch stop
ovsdb-tool convert /etc/openvswitch/conf.db /tmp/vswitch.schema_2.0.0
/etc/init.d/openvswitch start
