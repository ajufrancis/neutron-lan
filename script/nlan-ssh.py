#!/usr/bin/python

"""
2014/2/6
2014/3/12
2014/3/20-27

Usage example: 
$ python nlan-ssh.py --help
$ python nlan-ssh.py '*' --scp * 
$ python nlan-ssh.py '*' --scpmod
$ python nlan-ssh.py openwrt1 --raw 'cat /etc/hosts'
$ python nlan-ssh.py '*' init.run
$ python nlan-ssh.py '*' test.ping 192.168.1.10
$ python nlan-ssh.py '*' test.hello hello world!

nlan-ssh.py can also execute an arbitrary python module.function:
$ python nlan-ssh.py '*' os.getenv PATH
$ python nlan-ssh.py '*' os.path.isdir '/tmp'

CRUD operations:
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
 

"""
import os, sys 
import yaml
import paramiko as para, scp
from optparse import OptionParser
from collections import OrderedDict
from time import sleep

NLAN_DIR = '/root/neutron-lan/script' 
ROSTER_YAML = os.path.join(NLAN_DIR,'roster.yaml')
NLAN_AGENT_DIR = '/tmp'
NLAN_AGENT = os.path.join(NLAN_AGENT_DIR,'nlan-agent.py')

dirs = os.listdir(NLAN_DIR)
MOD_DIRS = []
for f in dirs:
    if not f.startswith('.'):
        ff = os.path.join(NLAN_DIR, f)
        if os.path.isdir(ff):
            sys.path.append(ff)
            MOD_DIRS.append(f)

def _deploy(roster, router, operation, doc):
    
    from multiprocessing import Process, Lock, Pipe

    # ssh session per sub-process
    def _ssh_session(lock, router, host, user, passwd, platform, operation, cmd, cmd_args, child):

        from cStringIO import StringIO
        out = StringIO()
        err = StringIO()

        exitcode = 0

        try:
            ssh = para.SSHClient()
            ssh.set_missing_host_key_policy(para.AutoAddPolicy())
            ssh.connect(host,username=user,password=passwd)
            print >>out, '--- Router Response, router:' + router + ', platform:' + platform + ' -------'

            if operation != '--scp' and operation != '--scpmod':
                i,o,e = ssh.exec_command(cmd)
                if operation != '--raw' and operation != '':
                    i.write(cmd_args)
                    i.flush()
                    i.channel.shutdown_write()
                result = o.read()
                error = e.read()
                print >>out, result
                print >>out, '......' 
                if error == '':
                    print >>err, 'None'
                else:
                    print >>err, error
                    exitcode = 1 
            else:
                if operation == '--scp':
                    s = scp.SCPClient(ssh.get_transport())
                    print >>out, "target_dir: " + NLAN_AGENT_DIR
                    for f in cmd: 
                        print >>out, ">>> Copying a file: " + f
                        lf = os.path.join(NLAN_DIR, f)
                        s.put(lf, NLAN_AGENT_DIR)
                    rdir_modlist = os.path.join(NLAN_AGENT_DIR, 'nlan-env.txt')
                    mod_dir = [] 
                    for s in MOD_DIRS:
                        mod_dir.append(s) 
                    env = OrderedDict()
                    env['platform'] = platform
                    env['mod_dir'] = mod_dir
                    i,o,e = ssh.exec_command('echo ' + '"'+str(env)+'"' + ' > ' + rdir_modlist) 
                    result = o.read()
                    error = e.read()
                    print >>out, result
                    print >>out, '......'
                    if error == '':
                        print >>err, 'None'
                    else:
                        print >>err, error
                        exitcode = 1
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
                            print >>err, 'None'
                        else:
                            print >>err, error
                            exitcode = 1
                        for f in os.listdir(ldir):
                            ff = os.path.join(ldir, f) 
                            s.put(ff, rdir)

            
            lock.acquire()
            print(out.getvalue())
            print(err.getvalue())
            lock.release()
            out.close()
            ssh.close()
            child.send(exitcode)

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
        cmd = ''
	cmd_args = ''
        if operation == '--raw':
            assert(isinstance(doc,str))
            cmd = doc
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
        elif operation == '':
            cmd = NLAN_AGENT + ' ' + doc 
            print '--- Controller Request -------'
            print router+':'
            print 'platform: ' + platform 
            print 'command: ' + doc 
	else:
            cmd = NLAN_AGENT + ' ' + operation
            cmd_args = doc
            cmd_args = '"' + cmd_args + '"'
            print '--- Controller Request -------'
            print router+':'
            print 'platform: ' + platform 
            print 'operation: ' + operation 
            print 'dict_args: ' + cmd_args

        print ''
       
        # Pipe to receive an exitcode from a child process
        parent, child = Pipe()

        ssh_sessions.append([Process(target=_ssh_session, args=(lock, router, host, user, passwd, platform, operation, cmd, cmd_args, child)), parent])
    
    for l in ssh_sessions:
        l[0].start()

    for l in ssh_sessions:
        while True:
            sleep(0.2)
            if not l[0].is_alive():
                break
        exitcode = l[1].recv()
        if exitcode > 0:
            sys.exit(exitcode)


if __name__=="__main__":

    parser = OptionParser()
    parser.add_option("-r", "--raw", help="run a raw shell command on remote routers", action="store_true", default=False)
    parser.add_option("-a", "--add", help="add elements", action="store_true", default=False)
    parser.add_option("-g", "--get", help="get elements", action="store_true", default=False)
    parser.add_option("-u", "--update", help="update elements", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="delete elements", action="store_true", default=False)
    parser.add_option("-c", "--scp", help="copy neutron-lan scripts to remote routers", action="store_true", default=False)
    parser.add_option("-m", "--scpmod", help="copy neutron-lan modules to remote routers", action="store_true", default=False)
    
    (options, args) = parser.parse_args()


    router = ''
    operation = ''

    router = args[0]
    if router == '*':
        router = '__ALL__'

    doc = ' '.join(args[1:])
    if options.raw:
	operation = "--raw" 
	doc = args[1]
    elif options.scp:
        operation = "--scp"
	doc = []
        for line in args[1:]:
            doc.append(line)	
    elif options.scpmod:
        operation = "--scpmod"
    else:
        if options.add:
            operation = "--add" 
            doc = args[1]
        elif options.get:
            operation = "--get"
            doc = args[1]
        elif options.update:
            operation = "--update"
            doc = args[1]
        elif options.delete:
            operation = "--delete"
            doc = args[1]
	
    r = open(ROSTER_YAML,'r')
    roster = yaml.load(r.read())
    r.close()

    _deploy(roster=roster,router=router,operation=operation,doc=doc)


