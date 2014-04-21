#!/bin/bash

ETC=./agent/etc

python nlan_schema.py -n $ETC/nlan.schema_0.0.1.yaml -o $ETC/vswitch.schema_2.0.0 -m > $ETC/ovsdb_nlan.schema
