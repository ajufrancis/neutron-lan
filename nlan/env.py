# 2014/4/14
# NLAN Environment 

import os
import yaml
import nlan_schema

# NLAN Master Home Directory (local)
NLAN_DIR = '/root/neutron-lan/nlan'

# NLAN etc directory (local)
NLAN_ETC = '/root/neutron-lan/nlan/etc'

# Directory of NLAN agent scripts including NLAN modules (local)
NLAN_SCP_DIR = os.path.join(NLAN_DIR, 'agent') 

# roster file (local)
ROSTER_YAML = os.path.join(NLAN_ETC,'roster.yaml')
roster = {}
with open(ROSTER_YAML, 'r') as f:
    roster = yaml.load(f.read())
ROSTER = roster

# NLAN Agent Home Directory (remote)
NLAN_AGENT_DIR = '/opt/nlan'

# NLAN agent script file (local)
NLAN_AGENT = os.path.join(NLAN_AGENT_DIR,'nlan_agent.py')

# NLAN libraries shared by both NLAN Master(local) and NLAN Agent(remote)
NLAN_LIBS = ['cmdutil.py', 'errors.py']

# NLAN module directories (python packages)
NLAN_MOD_DIRS = ['command', 'config']

# NLAN schema file in YAML (local)
NLAN_SCHEMA = os.path.join(NLAN_DIR, 'agent/share/nlan.schema_0.0.2.yaml')

# Target OVSDB schema, merged with NLAN_SCHEMA
SCHEMA = 'ovsdb_nlan.schema'

state_order, tables, indexes, types = nlan_schema.analyze_schema(NLAN_SCHEMA)
# NLAN state order (rule: lower states depend on upper states)
STATE_ORDER = state_order 
# NLAN tables
TABLES = tables
# List indexes for NLAN "dvsdvr" state 
INDEXES = indexes 
# NLAN state parameter types
TYPES = types 

# SSH connect timeout (in seconds)
SSH_TIMEOUT = 10.0

# PING check wait time (in seconds)
PING_CHECK_WAIT = 10
