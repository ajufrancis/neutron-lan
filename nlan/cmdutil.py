#
# cmdutil.py: command execution utilities. 
# Usage example: python cmd.py 'ls -l' 'check_output'
# Refer to Python documentation: http://docs.python.org/2/library/subprocess.html
#
# 2014/1/29

import subprocess

CalledProcessError = subprocess.CalledProcessError

		
def _cmd(check, persist, *args):

    cmd_args = []
    args = list(args)
    for l in args:
        for ll in l.split():
            cmd_args.append(ll)
    return _cmd2(check=check, persist=persist, args=cmd_args)


# If type(args) is list, use this function.
def _cmd2(check, persist, args):
   
    logger = None
    try:
        logger = __n__['logger']
    except:
        pass

    argstring = ' '.join(args)
    logstr = 'cmd: ' + argstring 

    if persist:
        if __n__['init'] == 'start':
            logstr = logstr + ' [SKIPPED...]'
            logger.debug(logstr)
            return

    if logger:
        logger.debug(logstr)
    else:
        print logstr
	
    if check == 'call':
        return subprocess.call(args, stderr=subprocess.STDOUT)
    elif check == 'check_call':
        try:
            return subprocess.check_call(args, stderr=subprocess.STDOUT)
        except CalledProcessError as e:
            raise CmdError(argstring, e.returncode) 
        except Exception as e:
            raise CmdError(argstring, 1)
    elif check == 'check_output':
        try:
            out = None
            out = subprocess.check_output(args, stderr=subprocess.STDOUT)
            return out
        except CalledProcessError as e:
            raise CmdError(argstring, e.returncode, out)
        except Exception as e:
            raise CmdError(argstring, 1)
    else:
	print("Error: illegal argument -- " + check)


class CmdError(Exception):

    def __init__(self, command, returncode, out=None):

        self.message = "Command execution error" 
        self.command = command
        self.returncode = returncode
        self.out = out

    def __str__(self):

        message = ''
        if self.out:
            message = "{}\ncommand: {}\nstdout: {}\nexit: {}".format(self.message, self.command, self.out, self.returncode)
        else:
            message = "{}\ncommand: {}\nexit: {}".format(self.message, self.command, self.returncode)

        return message

# If you can ignore error condition, use this function.
def cmd(*args):
	return _cmd('call', False, *args)

def cmd2(args):
        return _cmd2('call', False, args)

def cmdp(*args):
	return _cmd('call', True, *args)

def cmd2p(args):
        return _cmd2('call', True, args)

# If you want the program to stop in case of error, use this function.	
def check_cmd(*args):
	return _cmd('check_call', False, *args)

def check_cmd2(args):
        return _cmd2('check_call', False, args)

def check_cmdp(*args):
	return _cmd('check_call', True, *args)

def check_cmd2p(args):
        return _cmd2('check_call', True, args)

# If you want to get command output, use this function.
def output_cmd(*args):
	return _cmd('check_output', False, *args)

def output_cmd2(args):
        return _cmd2('check_output', False, args)
	
def output_cmdp(*args):
	return _cmd('check_output', True, *args)

def output_cmd2p(args):
        return _cmd2('check_output', True, args)


if __name__ == "__main__":

    import sys

    args = ' '.join(sys.argv[1:])
    try:
        #cmd(args)
        #print check_cmd(args)
        print output_cmd(args)
    except CmdError as e:
        print e
        print e.command
        print e.out
        print e.returncode
	
