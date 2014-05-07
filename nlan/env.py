# 2014/4/14
# NLAN Environment 
#

import os
import yaml
import nlan_schema

# Note:
# NLAN modules sometimes refer to "__n__" built-in variable
# that is dynamically generated by nlan-agent.py.
# "__n__" includes a platform type and NLAN module directories.
#

# NLAN Master Home Directory
NLAN_DIR = '/root/neutron-lan/nlan'

# NLAN_ETC
NLAN_ETC = os.path.join(NLAN_DIR, 'agent/etc')

# Directory of NLAN agent scripts including NLAN modules
NLAN_SCP_DIR = os.path.join(NLAN_DIR, 'agent') 

# nlan-ssh script file
NLAN_SSH = os.path.join(NLAN_DIR, 'nlan_ssh.py')

# roster file 
ROSTER_YAML = os.path.join(NLAN_DIR,'roster.yaml')
roster = {}
with open(ROSTER_YAML, 'r') as f:
    roster = yaml.load(f.read())
ROSTER = roster

# NLAN Agent Home Directory
NLAN_AGENT_DIR = '/opt/nlan'

# NLAN Agent etc directory
NLAN_AGENT_ETC = os.path.join(NLAN_AGENT_DIR, 'etc')

# NLAN agent script file
NLAN_AGENT = os.path.join(NLAN_AGENT_DIR,'nlan_agent.py')

# NLAN libraries used by NLAN Agent and NLAN modules
NLAN_LIBS = ['cmdutil.py', 'errors.py']

# NLAN module directories
NLAN_MOD_DIRS = ['command', 'config']

# NLAN agent etc directory
NLAN_AGENT_ETC = os.path.join(NLAN_AGENT_DIR, 'etc')

# NLAN schema file in YAML
NLAN_SCHEMA = os.path.join(NLAN_ETC, 'nlan.schema_0.0.1.yaml')
# Original OVSDB schema file
#OVSDB_SCHEMA = os.path.join(SCHEMA_DIR, 'vswitch.schema_2.0.0')

# Target OVSDB schema file merged with NLAN_SCHEMA
SCHEMA = 'ovsdb_nlan.schema'

state_order, tables, indexes, types = nlan_schema.analyze_schema(NLAN_SCHEMA)
# NLAN state order (rule: lower states depend on upper states)
#STATE_ORDER = ['bridges', 'services', 'gateway', 'vxlan', 'subnets']
STATE_ORDER = state_order 
# NLAN tables
TABLES = tables
# List indexes for NLAN "dvsdvr" state 
#INDEXES = {'subnets': 'vni', 'services': 'name'}
INDEXES = indexes 
# NLAN state parameter types
TYPES = types 

# SSH connect timeout (in seconds)
SSH_TIMEOUT = 10.0

# PING check wait time (in seconds)
PING_CHECK_WAIT = 10
