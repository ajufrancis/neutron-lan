#!/usr/bin/python

"""
2014/2/6
2014/3/12
2014/3/20-22

Usage example: 
$ python nlan-ssh.py --help
$ python nlan-ssh.py '*' --scp * 
$ python nlan-ssh.py '*' --scpmod
$ python nlan-ssh.py --batch dvsdvr.yaml 
$ python nlan-ssh.py openwrt1 --raw 'cat /etc/hosts'
$ python nlan-ssh.py '*' --init

CRUD operations have not yet supported:
--add: Create
--get: Read
--update: Update 
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

dirs = os.listdir(NLAN_DIR)
MOD_DIRS = []
for f in dirs:
    ff = os.path.join(NLAN_DIR, f)
    if os.path.isdir(ff):
        sys.path.append(ff)
        MOD_DIRS.append(f)

def _deploy(roster, router, operation, doc):
    
    from multiprocessing import Process, Lock

    # ssh session per sub-process
    def _ssh_session(lock, router, host, user, passwd, platform, operation, cmd, cmd_args):
        from cStringIO import StringIO
        out = StringIO()

        try:
            ssh = para.SSHClient()
            ssh.set_missing_host_key_policy(para.AutoAddPolicy())
            ssh.connect(host,username=user,password=passwd)
            print >>out, '--- Router Response, router:' + router + ', platform:' + platform + ' -------'

            if operation != '--scp' and operation != '--scpmod':
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
                if operation == '--scp':
                    s = scp.SCPClient(ssh.get_transport())
                    print >>out, "target_dir: " + NLAN_AGENT_DIR
                    for f in doc: 
                        print >>out, ">>> Copying a file: " + f
                        s.put(f, NLAN_AGENT_DIR)
                    rdir_modlist = os.path.join(NLAN_AGENT_DIR, 'nlan-modlist.txt')
                    mod_list = [] 
                    for s in MOD_DIRS:
                        mod_list.append('"'+s+'"') 
                    i,o,e = ssh.exec_command('echo ' + str(mod_list) + ' > ' + rdir_modlist) 
                    result = o.read()
                    error = e.read()
                    print >>out, result
                    print >>out, '......'
                    if error == '':
                        print >>out, 'None'
                    else:
                        print >>out, error
                elif operation == '--scpmod':
                    s = scp.SCPClient(ssh.get_transport())
                    for moddir in MOD_DIRS:
                        ldir = os.path.join(NLAN_DIR, moddir)
                        rdir = os.path.join(NLAN_AGENT_DIR, moddir)
                        i,o,e = ssh.exec_command('mkdir -p ' + rdir) 
                        result = o.read()
                        error = e.read()
                        print >>out, result
                        print >>out, '......'
                        if error == '':
                            print >>out, 'None'
                        else:
                            print >>out, error
                        for f in os.listdir(ldir):
                            ff = os.path.join(ldir, f) 
                            s.put(ff, rdir)

            
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
        platform = roster[router]['platform']
        platform_args = '--platform '+ platform 
        cmd = ''
	cmd_args = ''
        if operation == '--raw':
            assert(isinstance(doc,str))
            cmd = doc
            print '--- Controller Request ------'
            print router+':'
            print 'operation: ' + operation 
        elif operation == '--init':
            cmd = NLAN_AGENT + ' ' + operation + ' ' + platform_args
            print '--- Controller Request ------'
            print router+':'
            print 'operation: ' + operation 
        elif operation == '--scpmod':
            print '--- Controller Request ------'
            print router+':'
            print 'operation: ' + operation 
        elif operation == '--scp':
            assert(isinstance(doc,list))
            cmd = doc
            for f in doc:
                fp = os.path.join(NLAN_DIR, f)
                if os.path.isdir(fp):
                    cmd.remove(f)
            print '--- Controller Request ------'
            print router+':'
            print 'operation: ' + operation 
            print 'files: ' + str(cmd)	
	else:
            assert(isinstance(doc,dict))
            cmd = NLAN_AGENT + ' ' + operation + ' ' + platform_args 
            cmd_args = str(doc[router])
            cmd_args = '"' + cmd_args + '"'
            print '--- Controller Request -------'
            print router+':'
            print 'platform: ' + platform 
            print 'operation: ' + operation 
            print 'dict_args: ' + cmd_args

        print ''

        ssh_sessions.append(Process(target=_ssh_session, args=(lock, router, host, user, passwd, platform, operation, cmd, cmd_args)))
    
    for l in ssh_sessions:
        l.start()


if __name__=="__main__":

    parser = OptionParser()
    parser.add_option("-r", "--raw", help="run a raw shell command on remote routers", action="store_true", default=False)
    parser.add_option("-a", "--add", help="add elements", action="store_true", default=False)
    parser.add_option("-g", "--get", help="get elements", action="store_true", default=False)
    parser.add_option("-s", "--update", help="update elements", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="delete elements", action="store_true", default=False)
    parser.add_option("-c", "--scp", help="copy neutron-lan scripts to remote routers", action="store_true", default=False)
    parser.add_option("-m", "--scpmod", help="copy neutron-lan modules to remote routers", action="store_true", default=False)
    parser.add_option("-i", "--init", help="initialize remote routers", action="store_true", default=False)
    parser.add_option("-b", "--batch", help="configure remote routers in a batch mode", action="store_true", default=False)
    
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
    elif options.scpmod:
        operation = "--scpmod"
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
            operation = "--update"
        elif options.delete:
            operation = "--delete"
        doc = {router: {args[0]: eval(args[1])}}
	
    r = open(ROSTER_YAML,'r')
    roster = yaml.load(r.read())
    r.close()

    _deploy(roster=roster,router=router,operation=operation,doc=doc)


