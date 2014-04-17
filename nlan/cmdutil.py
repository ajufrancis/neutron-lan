#
# cmdutil.py: command execution utilities. 
# Usage example: python cmd.py 'ls -l' 'check_output'
# Refer to Python documentation: http://docs.python.org/2/library/subprocess.html
#
# 2014/1/29

import subprocess

logger = None
try:
    logger = __n__['logger']
except:
    pass
		
def _cmd(check, persist, *args):

    args = list(args)
    cmd_args = '["'
    for arg in args:
        if cmd_args == '["':
            cmd_args += arg.replace(' ', '","')
        else:
            cmd_args += '","' + arg.replace(' ', '","')
    cmd_args += '"]'
    cmd_args = eval(cmd_args)
        
    return _cmd2(check=check, persist=persist, args=cmd_args)


# If type(args) is list, use this function.
def _cmd2(check, persist, args):

    logstr = 'cmd: ' + ' '.join(args)

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
        return subprocess.check_call(args, stderr=subprocess.STDOUT)
    elif check == 'check_output':
        return subprocess.check_output(args, stderr=subprocess.STDOUT)
    else:
	print("Error: illegal argument -- " + check)


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
	if len(sys.argv) < 3:
		check_cmd(sys.argv[1])
	elif len(sys.argv) == 3:
		_cmd(sys.argv[2], sys.argv[1])
	else:
		print ("Error: requires at least two arguments")
		
	
