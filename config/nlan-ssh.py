#!/usr/bin/python

"""
2014/2/6

This "nlan-ssh.py" script works like a "salt-ssh" command provided by
SaltStack. However, this script has no dependencies on SaltStack.

I have stopped using SaltStack, since OpenWRT has not yet supported
salt-minion. I will also study using "zmq" over ssh.

For the time being, "paramiko" is used for manipulating a remote script
via ssh.

Usage example: 
$ python nlan-ssh.py '*' --add dvsdvr.yaml 
$ python nlan-ssh.py openwrt3 -a dvsdvr.yaml 
$ python nlan-ssh.py openwrt1 -r 'cat /etc/hosts'
$ python nlan-ssh.py '*' --row 'date'

"nlan.py" referes to the following YAML files before calling "nlan-agent.py"
via ssh on OpenWRT routers:
- roster.yaml 
  This is a copy of /etc/salt/roster, although I have stopped using
  salt-ssh any longer.
- CONFIG_YAML (e.g, dvsdvr.yaml)
  This is a config file of neutron-lan in YAML format. 
 
YAML data is converted into Dict data, then the Dict data is
converted into str data.
The str data is transferred to nlan-agent.py via stdin:
YAML data => Dict data => str data => stdin => nlan-agent.py 

I may consider using "collections.OrderedDict" instead of normal dict data
later on.


"""

import yaml
import paramiko as para
from optparse import OptionParser

ROSTER_YAML = '/root/roster.yaml'
NLAN_AGENT = '/root/nlan-agent.py'

def _test(roster,router,operation,doc):

	routers = []

	if router == '__ALL__':	
		routers = roster.keys()
	else:
		routers.append(router)

	for router in routers:
		host = roster[router]['host']
		user = roster[router]['user']
		passwd = roster[router]['passwd']	
		cmd_args = ''
		if operation == '--row':
			cmd = doc
			print '--- Controller Request ------'
			print router+':'
			print 'command: ' + cmd 
		else:
			cmd = NLAN_AGENT + ' ' + operation
			cmd_args = str(doc[router])
			cmd_args = '"' + cmd_args + '"'
			print '--- Controller Request -------'
			print router+':'
			print 'operation: ' + operation 
			print 'dict_args: ' + cmd_args
		try:
			conn = para.SSHClient()
			conn.set_missing_host_key_policy(para.AutoAddPolicy())
			conn.connect(host,username=user,password=passwd)
			i,o,e = conn.exec_command(cmd)
			if operation != '--row':
				i.write(cmd_args)
				i.flush()
				i.channel.shutdown_write()
			result = o.read()
			print '--- OpenWRT response ---------'
			print result
			print ''
		finally:
			if conn: conn.close()
		

if __name__=="__main__":

	import sys

	parser = OptionParser()
	parser.add_option("-r", "--row", dest="row", help="Execute row shell commands", action="store_true", default=False)
	parser.add_option("-a", "--add", dest="add", help="Add an element", action="store_true", default=False)

	(options, args) = parser.parse_args()

	router = ''
	operation = ''
	doc = ''
	
	router = sys.argv[1]
	if router == '*':
		router = '__ALL__'
	
	if options.row:
		operation = "--row" 
		doc = sys.argv[3]
	elif options.add:	
		operation = "--add" 
		f = open(sys.argv[3])
		doc = yaml.load(f.read())
		f.close()
	
	r = open(ROSTER_YAML,'r')
	roster = yaml.load(r.read())
	r.close()
	_test(roster=roster,router=router,operation=operation,doc=doc)


