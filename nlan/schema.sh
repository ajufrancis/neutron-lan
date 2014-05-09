#!/bin/bash
#
# Schema merge utility
# -n <nlan_schema(yaml)>
# -o <ovsdb_schema(json)>
# -m
#

SHARE=./agent/share

python nlan_schema.py -n $SHARE/nlan.schema_0.0.1.yaml -o $SHARE/vswitch.schema_2.0.0 -m > $SHARE/ovsdb_nlan.schema
