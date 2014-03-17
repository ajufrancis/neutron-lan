#!/usr/bin/python

"""
2014/2/6
2014/3/12

Usage example: 
$ python nlan-ssh.py --help
$ python nlan-ssh.py '*' --scp * 
$ python nlan-ssh.py --batch dvsdvr.yaml 
$ python nlan-ssh.py openwrt1 --raw 'cat /etc/hosts'
$ python nlan-ssh.py '*' --init

CRUD operations have not yet supported:
--add: Create
--get: Read
--set: Set
--delete: Delete

"nlan.py" referes to the following YAML files before calling "nlan-agent.py"
via ssh on OpenWRT routers:
- roster.yaml 
  This is sort of /etc/salt/roster, although I have stopped using
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
import os, sys 
import yaml
import paramiko as para, scp
from optparse import OptionParser

NLAN_DIR = '/root/neutron-lan/script' 
ROSTER_YAML = os.path.join(NLAN_DIR,'roster.yaml')
NLAN_AGENT_DIR = '/tmp'
NLAN_AGENT = os.path.join(NLAN_AGENT_DIR,'nlan-agent.py')

def _deploy(roster, router, operation, doc):
    
    from multiprocessing import Process, Lock

    # ssh session per sub-process
    def _ssh_session(lock, router, host, user, passwd, hardware, operation, cmd, cmd_args):
        from cStringIO import StringIO
        out = StringIO()

        try:
            ssh = para.SSHClient()
            ssh.set_missing_host_key_policy(para.AutoAddPolicy())
            ssh.connect(host,username=user,password=passwd)
            print >>out, '--- Router Response, router:' + router + ', hardware:' + hardware + ' -------'

            if operation != '--scp':
                i,o,e = ssh.exec_command(cmd)
                if operation != '--raw' and operation != '--init':
                    i.write(cmd_args)
                    i.flush()
                    i.channel.shutdown_write()
                result = o.read()
                error = e.read()
                print >>out, result
                print >>out, '......'
                if error == '':
                    print >>out, 'None'
                else:
                    print >>out, error
            else:
                s = scp.SCPClient(ssh.get_transport())
                print >>out, "target_dir: " + NLAN_AGENT_DIR
                for file in doc: 
                    print >>out, ">>> Copying a file: " + file
                    s.put(file, NLAN_AGENT_DIR)
            
            lock.acquire()
            print(out.getvalue())
            lock.release()
            out.close()
            ssh.close()

        except Exception as e:
            print e.message


    routers = []

    ssh_sessions = [] 
    lock = Lock()

    if router == '__ALL__':	
        routers = roster.keys()
    else:
        routers.append(router)

    for router in routers:
        host = roster[router]['host']
        user = roster[router]['user']
        passwd = roster[router]['passwd']	
        hardware = roster[router]['hardware']
        hardware_args = '--type '+ hardware 
        cmd = ''
	cmd_args = ''
        if operation == '--raw':
            assert(isinstance(doc,str))
            cmd = doc
            print '--- Controller Request ------'
            print router+':'
            print 'operation: ' + operation 
        elif operation == '--init':
            cmd = NLAN_AGENT + ' ' + operation + ' ' + hardware_args
            print '--- Controller Request ------'
            print router+':'
            print 'operation: ' + operation 
        elif operation == '--scp':
            assert(isinstance(doc,list))
            cmd = doc
            print '--- Controller Request ------'
            print router+':'
            print 'operation: ' + operation 
            print 'files: ' + str(cmd)	
	else:
            assert(isinstance(doc,dict))
            cmd = NLAN_AGENT + ' ' + operation + ' ' + hardware_args 
            cmd_args = str(doc[router])
            cmd_args = '"' + cmd_args + '"'
            print '--- Controller Request -------'
            print router+':'
            print 'hardware: ' + hardware 
            print 'operation: ' + operation 
            print 'dict_args: ' + cmd_args

        print ''

        ssh_sessions.append(Process(target=_ssh_session, args=(lock, router, host, user, passwd, hardware, operation, cmd, cmd_args)))
    
    for l in ssh_sessions:
        l.start()


if __name__=="__main__":

    parser = OptionParser()
    parser.add_option("-r", "--raw", help="Execute raw shell commands", action="store_true", default=False)
    parser.add_option("-a", "--add", help="Add elements", action="store_true", default=False)
    parser.add_option("-g", "--get", help="Get elements", action="store_true", default=False)
    parser.add_option("-s", "--set", help="Set elements", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="Delete elements", action="store_true", default=False)
    parser.add_option("-c", "--scp", help="Secure copy", action="store_true", default=False)
    parser.add_option("-i", "--init", help="Initialization", action="store_true", default=False)
    parser.add_option("-b", "--batch", help="Batch config mode", action="store_true", default=False)
    
    (options, args) = parser.parse_args()


    router = ''
    operation = ''
    doc = ''

    if options.batch:
        router = '__ALL__'
    else:
        router = args[0]
        if router == '*':
            router = '__ALL__'

    if options.raw:
	operation = "--raw" 
	doc = args[1]
        print doc
    elif options.scp:
        operation = "--scp"
	doc = []
        for line in args[1:]:
            doc.append(line)	
    elif options.init:
        operation = "--init"
    elif options.batch:
        operation = "--add"
        f = open(args[0])
        doc = yaml.load(f.read())
        f.close()
    else:
        if options.add:
            operation = "--add" 
        elif options.get:
            operation = "--get"
        elif options.get:
            operation = "--set"
        elif options.delete:
            operation = "--delete"
        doc = {router: {args[0]: eval(args[1])}}
	
    r = open(ROSTER_YAML,'r')
    roster = yaml.load(r.read())
    r.close()

    _deploy(roster=roster,router=router,operation=operation,doc=doc)


