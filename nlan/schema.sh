#!/bin/bash

python nlan_schema.py -n nlan.schema_0.0.1.yaml -o vswitch.schema_2.0.0 -m > agent/ovsdb_nlan.schema
