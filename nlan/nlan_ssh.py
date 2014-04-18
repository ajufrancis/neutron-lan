#!/usr/bin/env python

"""
2014/2/6

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

If ssh login is very slow to start, set UseDNS no in sshd_config.  
Refer to http://www.openssh.com/faq.html

"""
import os, sys 
import yaml
import paramiko as para, scp
from optparse import OptionParser
from time import sleep
from env import * 
from cmdutil import output_cmd

nlanconf = 'nlan_env.conf'

bar = '=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+'

def _printmsg_request(lock, router, platform):
    with lock:
        rp = "NLAN Request to router:{0},platform:{1}".format(router, platform)
        print bar[:5], rp, bar[5+len(rp):] 

def _deploy(router, operation, doc, cmd_list, loglevel):

    #print router, operation, doc, cmd_list, loglevel
    
    from multiprocessing import Process, Lock, Pipe

    with open(ROSTER_YAML,'r') as r:
        roster = yaml.load(r.read())


    def _ssh_exec_command(ssh, cmd, cmd_args, out, err):

        i,o,e = ssh.exec_command(cmd)

        if cmd_args:
            i.write(cmd_args)
            i.flush()
            i.channel.shutdown_write()
        result = o.read()
        error = e.read()
        if result != '': 
            print >>out, result
        if error != '':
            print >>err, error

        return o.channel.recv_exit_status()


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


            if operation != '--scp' and operation != '--scpmod':
                exitcode = _ssh_exec_command(ssh, cmd, cmd_args, out, err)
            else:
                filelist = []
                if operation == '--scp':
                    s = scp.SCPClient(ssh.get_transport())
                    print >>out, "target_dir: " + NLAN_AGENT_DIR
                    for f in cmd: 
                        s.put(f, NLAN_AGENT_DIR)
                        filelist.append(f)
                elif operation == '--scpmod':
                    s = scp.SCPClient(ssh.get_transport())
                    print >>out, "target_dir: " + NLAN_AGENT_DIR
                    # scp NLAN modules
                    for moddir in NLAN_MOD_DIRS:
                        ldir = os.path.join(NLAN_SCP_DIR, moddir)
                        rdir = os.path.join(NLAN_AGENT_DIR, moddir)
                        exitcode = _ssh_exec_command(ssh, 'mkdir -p ' + rdir, None, out, err)
                        for f in os.listdir(ldir):
                            ff = os.path.join(ldir, f) 
                            s.put(ff, rdir)
                            filelist.append(f)
                    # scp NLAN-Agent scripts
                    for f in os.listdir(os.path.join(NLAN_SCP_DIR)):
                        lf = os.path.join(NLAN_SCP_DIR, f)
                        if os.path.isdir(lf):
                            pass
                        else:
                            s.put(lf, NLAN_AGENT_DIR)
                            filelist.append(f)
                    # scp NLAN libs
                    for f in NLAN_LIBS:
                        lf = os.path.join(NLAN_DIR, f)
                        s.put(lf, NLAN_AGENT_DIR)
                        filelist.append(f)
                    # nlan_env.conf generation
                    rdir_modlist = os.path.join(NLAN_AGENT_DIR, nlanconf)
                    env = {} 
                    env['router'] = router
                    env['platform'] = platform
                    env['agent_dir'] = NLAN_AGENT_DIR
                    env['mod_dir'] = NLAN_MOD_DIRS 
                    env['schema'] = SCHEMA
                    env['state_order'] = STATE_ORDER
                    env['tables'] = TABLES
                    env['indexes'] = INDEXES
                    env['types'] = TYPES 
                    lf = os.path.join(NLAN_DIR, nlanconf) 
                    with open(lf, 'w') as f:
                        f.seek(0)
                        f.truncate()
                        f.write(str(env))
                    s.put(lf, NLAN_AGENT_DIR)
                    #cmd = 'echo ' + '"'+str(env)+'"' + ' > ' + rdir_modlist 
                    #exitcode = _ssh_exec_command(ssh, cmd, None, out, err)
                    filelist.append(nlanconf)
                
                print >>out, "files: " + str(filelist)
            
            with lock:
                outv = out.getvalue()
                erre = err.getvalue()
                outvl = len(outv)
                errel = len(erre)
                if operation == '--scpmod' or operation == '--scp':
                        rp = "Files copied to router:{0},platform:{1}".format(router, platform)
                        print bar[:5], rp, bar[5+len(rp):] 
                else:
                    if outvl + errel > 0:
                        rp = "NLAN Reply from router:{0},platform:{1}".format(router, platform)
                        print bar[:5], rp, bar[5+len(rp):] 
                if outvl > 0:
                    print(outv)
                if errel > 0:
                    if outvl > 0:
                        print ('...')
                    print(erre)

            out.close()
            err.close()
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

    if operation == '--batch':
        for l in cmd_list:

            router = l[0]
            operation = l[1]
            doc = l[2]

            host = roster[router]['host']
            user = roster[router]['user']
            passwd = roster[router]['passwd']	
            platform = roster[router]['platform']

            cmd = NLAN_AGENT + ' ' + operation + ' --envfile ' + os.path.join(NLAN_AGENT_DIR, nlanconf) + ' ' + loglevel
            cmd_args = doc
            cmd_args = '"' + cmd_args + '"'
            _printmsg_request(lock, router, platform)
            print 'operation: ' + operation 
            print 'dict_args: ' + cmd_args

            # Pipe to receive an exitcode from a child process
            parent, child = Pipe()

            ssh_sessions.append([Process(target=_ssh_session, args=(lock, router, host, user, passwd, platform, operation, cmd, cmd_args, child)), parent])

    else:
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
                _printmsg_request(lock, router, platform)
                print 'operation: ' + operation 
                print 'command: ' + cmd	
            elif operation == '--scpmod':
                _printmsg_request(lock, router, platform)
                print 'operation: ' + operation 
            elif operation == '--scp':
                assert(isinstance(doc,list))
                cmd = doc
                for f in doc:
                    fp = os.path.join(NLAN_DIR, f)
                    if os.path.isdir(fp):
                        cmd.remove(f)
                _printmsg_request(lock, router, platform)
                print 'operation: ' + operation 
                print 'files: ' + str(cmd)	
            elif operation == None:
                cmd = NLAN_AGENT + ' ' + doc + ' --envfile ' + os.path.join(NLAN_AGENT_DIR, nlanconf) + ' ' + loglevel
                _printmsg_request(lock, router, platform)
                print 'command: ' + doc 
            else:
                cmd = NLAN_AGENT + ' ' + operation + ' --envfile ' + os.path.join(NLAN_AGENT_DIR, nlanconf) + ' ' + loglevel
                cmd_args = doc
                cmd_args = '"' + cmd_args + '"'
                _printmsg_request(lock, router, platform)
                print 'operation: ' + operation 
                print 'dict_args: ' + cmd_args

            # Pipe to receive an exitcode from a child process
            parent, child = Pipe()

            ssh_sessions.append([Process(target=_ssh_session, args=(lock, router, host, user, passwd, platform, operation, cmd, cmd_args, child)), parent])
 
    # Start subprocesses
    try:
        for l in ssh_sessions:
            l[0].start()

        while True:
            if len(ssh_sessions) == 0:
                break
            sleep(0.5)
            for l in ssh_sessions:
                if not l[0].is_alive():
                    exitcode = l[1].recv()
                    l[0].terminate()
                    ssh_sessions.remove(l)
                    if exitcode > 0:
                        print ''
                        raise Exception("NLAN Agent raised an error [exit code = {0}]".format(exitcode)) 
                #else:
                #    with lock:
                #        print str(l[0])
    except KeyboardInterrupt:
        print "\nOK. I will terminate the subprocesses..."
        for l in ssh_sessions:
            pid = str(l[0].pid)
            sub = output_cmd('ps -p', pid, 'h')
            l[0].terminate()
            l[0].join()
            print "subrocess:", sub 
        raise Exception("Operation stopped by Keyboard Interruption") 
    finally:
        for l in ssh_sessions:
            l[0].terminate()
        

if __name__=="__main__":

    usage = "usage: %prog [options] [router] [arg]..."
    parser = OptionParser(usage=usage)
    parser.add_option("-r", "--raw", help="run a raw shell command on remote routers", action="store_true", default=False)
    parser.add_option("-a", "--add", help="add NLAN states", action="store_true", default=False)
    parser.add_option("-g", "--get", help="get NALN states", action="store_true", default=False)
    parser.add_option("-u", "--update", help="update NLAN states", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="delete NLAN states", action="store_true", default=False)
    parser.add_option("-c", "--scp", help="copy scripts to remote routers", action="store_true", default=False)
    parser.add_option("-m", "--scpmod", help="copy NLAN Agent and NLAN modules to remote routers", action="store_true", default=False)
    parser.add_option("-I", "--info", help="set log level to INFO", action="store_true", default=False)
    parser.add_option("-D", "--debug", help="set log level to DEBUG", action="store_true", default=False)

    
    (options, args) = parser.parse_args()


    operation = None 

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
        for l in args[1:]:
            doc.append(l)
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

    loglevel = ''
    if options.info:
        loglebel = '--info'
    elif options.debug:
        loglevel = '--debug'
	
    _deploy(router=router,operation=operation,doc=doc,cmd_list=None,loglevel=loglevel)


def main(router='__ALL__',operation=None, doc=None, cmd_list=None, loglevel=''):

    if doc and not operation:
        doc = ' '.join(doc)
    
    _deploy(router=router,operation=operation,doc=doc,cmd_list=cmd_list,loglevel=loglevel)