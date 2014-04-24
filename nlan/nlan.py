#!/usr/bin/env python

"""
2014/2/6, created  
2014/4/21, merged with nlan_master.py 

"""
import os, sys 
import paramiko as para
import scp
#from paramiko import AuthenticationException, SSHException
from optparse import OptionParser
from time import sleep
import traceback
from collections import OrderedDict
from multiprocessing import Process, Lock, Pipe, Queue
import time, datetime
from cStringIO import StringIO

import cmdutil
import yaml, yamldiff
from env import * 

nlanconf = 'nlan_env.conf'

bar = '=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+'

def _printmsg_request(lock, router, platform):
    with lock:
        rp = "NLAN Request to router:{0},platform:{1}".format(router, platform)
        print bar[:5], rp, bar[5+len(rp):] 

def main(router='__ALL__',operation=None, doc=None, cmd_list=None, loglevel=None):

    rp = "Ping test to all the target routers"
    print bar[:5], rp, bar[5+len(rp):] 
    if _wait(router, PING_CHECK_WAIT) > 0:
        print ""
        print "Ping test failure! Transaction cancelled."
        sys.exit(1)

    start_datetime = str(datetime.datetime.now())
    start_utc = time.time()

    if doc and not operation or doc and operation == '--raw':
        doc = ' '.join(doc)
    if not loglevel:
        loglevel = ''
    #print router, operation, doc, cmd_list, loglevel
    

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


    # ssh session per child process
    def _ssh_session(lock, queue, router, host, user, passwd, platform, operation, cmd, cmd_args, child):


        out = StringIO()
        err = StringIO()
        ssh = None
        response = OrderedDict() 
        response['exit'] = 0
        exitcode = 0

        try:
            ssh = para.SSHClient()
            ssh.set_missing_host_key_policy(para.AutoAddPolicy())
            ssh.connect(host,username=user,password=passwd,timeout=SSH_TIMEOUT)


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
                    # scp NLAN Agent etc files
                    ldir = NLAN_ETC
                    rdir = NLAN_AGENT_ETC
                    exitcode = _ssh_exec_command(ssh, 'mkdir -p ' + rdir, None, out, err)
                    for f in os.listdir(ldir):
                        ff = os.path.join(ldir, f) 
                        s.put(ff, rdir)
                        filelist.append(f)

                    # nlan_env.conf generation
                    rdir_nlanconf = os.path.join(NLAN_AGENT_DIR, nlanconf)
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
                    env['etc_dir'] = NLAN_AGENT_ETC
                    lf = os.path.join('/tmp', '{}.{}'.format(nlanconf,router)) 
                    with open(lf, 'w') as f:
                        f.seek(0)
                        f.truncate()
                        f.write(str(env))
                    s.put(lf, rdir_nlanconf)
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
                        rp = "NLAN Response from router:{0},platform:{1}".format(router, platform)
                        print bar[:5], rp, bar[5+len(rp):] 
                if outvl > 0:
                    print(outv.rstrip('\n'))
                if errel > 0:
                    erre = erre.rstrip('\n').split('\n')
                    if len(erre) > 1:
                        print ('... stderr ...')
                    for l in erre[:-1]:
                        print l
                    print ('__ NLAN response __')
                    response = eval(erre[-1])

                finish_utc = time.time()
                queue.put([router, response, finish_utc])
                for key in response.keys():
                    print '{}: {}'.format(key, response[key])

        except Exception as e:
            response['exception'] = type(e).__name__
            response['message'] = 'See the traceback message'
            response['exit'] = 1 
            response['traceeback'] = traceback.format_exc()
            exitcode = 1
            finish_utc = time.time()
            queue.put([router, response , finish_utc])
            with lock:
                rp = "NLAN Request Failure router:{0},platform:{1}".format(router, platform)
                print bar[:5], rp, bar[5+len(rp):] 
                print ('__ Exception __')
                for key in response.keys():
                    print '{}: {}'.format(key, response[key])

        finally:
            out.close()
            err.close()
            ssh.close()
            child.send(exitcode)



    routers = []

    ssh_sessions = [] 
    lock = Lock()
    queue = Queue()

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

            ssh_sessions.append([Process(target=_ssh_session, args=(lock, queue, router, host, user, passwd, platform, operation, cmd, cmd_args, child)), parent])

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

            ssh_sessions.append([Process(target=_ssh_session, args=(lock, queue, router, host, user, passwd, platform, operation, cmd, cmd_args, child)), parent])
 
    # Start child processes
    try:
        for l in ssh_sessions:
            l[0].start()

        while True:
            if len(ssh_sessions) == 0:
                break
            sleep(0.5)
            temp = list(ssh_sessions)
            for l in temp:
                if not l[0].is_alive():
                    exitcode = l[1].recv()
                    l[0].terminate()
                    ssh_sessions.remove(l)
    except KeyboardInterrupt:
        print "\nOK. I will terminate the child processes..."
        for l in ssh_sessions:
            pid = str(l[0].pid)
            sub = cmdutil.output_cmd('ps -p', pid, 'h')
            l[0].terminate()
            l[0].join()
            print "child process:", sub 
        raise Exception("Operation stopped by Keyboard Interruption") 
    finally:
        if not queue.empty():
            title = "Transaction Summary"
            print bar[:5], title, bar[5+len(title):] 
            print ""
            print "Start Time: {}".format(start_datetime)
            print ""
            print "Router           Result    Elapsed Time"
            print "---------------------------------------"
            for l in ssh_sessions:
                l[0].terminate()
            while not queue.empty():
                smiley = ':-)'
                l = queue.get() 
                router = l[0]
                response = l[1]
                if response['exit'] > 0:
                    smiley = 'XXX'
                print "{:17s} {:3s}   {:10.2f}(sec)".format(router, smiley, l[2] - start_utc)
            

def _wait(router, timeout):

    import subprocess, time

    # child process
    def _ping(router, host, timeout, devnull, queue):

        start = time.time()
        okcheck = True
        if timeout < 0:
            timeout = abs(timeout)
            okcheck = False 
        while True:
            command = 'ping -c 1 -W 1 ' + host
            command = command.split()
            exitcode = subprocess.call(command, stdout=devnull)
            if okcheck and exitcode == 0 or not okcheck and exitcode > 0:
                queue.put((router, host, True))
                break
            if time.time() - start > timeout:
                queue.put((router, host, False))
                break

    hosts = {} 
    exit = 0

    with open(ROSTER_YAML,'r') as r:
        roster = yaml.load(r.read())
        if router == '__ALL__':
            for router in roster.keys():
                hosts[router] = roster[router]['host']
        else:
            hosts[router] = roster[router]['host']
     
    print "Router           Host           Ping"
    print "------------------------------------"
    children = []
    try:
        with open(os.devnull, 'w') as devnull:
            queue = Queue()
            for router, host in hosts.iteritems():
                child = Process(target=_ping, args=(router, host, timeout, devnull, queue))
                child.start()
                children.append(child)

            while True:
                if len(children) == 0:
                    break
                sleep(0.5)
                temp = list(children)
                for l in temp:
                    if not l.is_alive():
                        l.terminate()
                        children.remove(l)
                while not queue.empty():
                    q = queue.get()
                    router = q[0]
                    host = q[1]
                    result = q[2]
                    if timeout > 0 and result or timeout < 0 and not result:
                        print '{:17s}{:15s}OK'.format(router, host)
                    elif timeout > 0 and not result or timeout < 0 and result:
                        print '{:17s}{:15s}NG'.format(router, host)
                    if not result and exit == 0:
                        exit = 1
    except KeyboardInterrupt:
        print "\nOK. I will terminate the subprocesses..."
        for l in children:
            pid = str(l.pid)
            sub = cmdutil.output_cmd('ps -p', pid, 'h')
            l.terminate()
            l.join()
            print "child process:", sub 

    return exit


if __name__=='__main__':

    logo = """
       _  ____   ___   _  __  
      / |/ / /  / _ | / |/ /  
     /    / /__/ __ |/    /   
    /_/|_/____/_/ |_/_/|_/ 

    """

    usage = logo + "usage: %prog [options] [arg]..."
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--target", help="target router", action="store", type="string", dest="target")
    parser.add_option("-c", "--scp", help="copy scripts to remote routers", action="store_true", default=False)
    parser.add_option("-m", "--scpmod", help="copy NLAN Agent and NLAN modules to remote routers", action="store_true", default=False)
    parser.add_option("-a", "--add", help="(CRUD) add NLAN states", action="store_true", default=False)
    parser.add_option("-g", "--get", help="(CRUD) get NLAN states", action="store_true", default=False)
    parser.add_option("-u", "--update", help="(CRUD) update NLAN states", action="store_true", default=False)
    parser.add_option("-d", "--delete", help="(CRUD) delete NLAN states", action="store_true", default=False)
    parser.add_option("-r", "--raw", help="run a raw shell command on remote routers", action="store_true", default=False)
    parser.add_option("-w", "--wait", help="wait until all the routers become accessible (a value < 0 is for NG check, --target also applies)", action="store", type="int", dest="time")
    parser.add_option("-I", "--info", help="set log level to INFO", action="store_true", default=False)
    parser.add_option("-D", "--debug", help="set log level to DEBUG", action="store_true", default=False)
    parser.add_option("-G", "--git", help="use Git archive", action="store_true", default=False)

    (options, args) = parser.parse_args()


    option = None
    git = False
    target = None
    if options.add:
        option = '--add'
    elif options.get:
        option = '--get'
    elif options.update:
        option = '--update'
    elif options.delete:
        option = '--delete'
    elif options.scp:
        option = '--scp'
    elif options.scpmod:
        option = '--scpmod'
    elif options.raw:
        option = '--raw'
    elif options.git:
        git = True

    loglevel = None
    if options.info:
        loglevel = '--info'
    elif options.debug:
        loglevel = '--debug'

    router = '__ALL__'
    if options.target:
        router = options.target

    if options.time:
        timeout = options.time
        sys.exit(_wait(router, timeout))
    # --add, --get, --update, --delete, --scp, --scpmod, --raw, --wait
    elif option != None:
        main(router=router, operation=option, doc=args, loglevel=loglevel)
    else:
        # NLAN CRUD operations generated from a YAML state file
        if len(args) == 0:
            parser.print_usage()
            sys.exit(0)
        elif args[0].endswith('.yaml'):
            # State files
            for v in args:
                cmd_list = yamldiff.crud_diff(v)
                if len(cmd_list) != 0:
                    try:
                        main(router=router, operation='--batch', cmd_list=cmd_list, loglevel=loglevel)
                    except:
                        traceback.print_exc()
                        sys.exit(1)
                if git:
                    cmdutil.check_cmd('git add', v)
                    cmdutil.check_cmd('git commit -m updated')
        else:
            # NLAN command module execution
            main(router=router, doc=args, loglevel=loglevel)

