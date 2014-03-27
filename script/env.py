# 2014/3/28

import os
from collections import OrderedDict

NLAN_AGENT_DIR = '/tmp'

# Environment values
with open(os.path.join(NLAN_AGENT_DIR, 'nlan-env.txt'), 'r') as envfile:
    ENV = eval(envfile.read())

