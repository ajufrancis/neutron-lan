#
# cmdutil.py: command execution utilities. 
# Usage example: python cmd.py 'ls -l' 'check_output'
# Refer to Python documentation: http://docs.python.org/2/library/subprocess.html
#
# 2014/1/29

import subprocess

		
def _cmd(check, *args):
	
	args = list(args)
	cmd_args = '["'
	for arg in args:
		if cmd_args == '["':
			cmd_args += arg.replace(' ', '","')
		else:
			cmd_args += '","' + arg.replace(' ', '","')
	cmd_args += '"]'
	print 'cmd: ' + cmd_args
	cmd_args = eval(cmd_args)
	
	if check == 'call':
		return subprocess.call(cmd_args, stderr=subprocess.STDOUT)
	elif check == 'check_call':
		return subprocess.check_call(cmd_args, stderr=subprocess.STDOUT)
	elif check == 'check_output':
		return subprocess.check_output(cmd_args, stderr=subprocess.STDOUT)
	else:
		print("Error: illegal argument -- " + check)


# If you can ignore error condition, use this function.
def cmd(*args):
	return _cmd('call', *args)

# If you want the program to stop in case of error, use this function.	
def check_cmd(*args):
	return _cmd('check_call', *args)

# If you want to get command output, use this function.
def output_cmd(*args):
	return _cmd('check_output', *args)
	

if __name__ == "__main__":

	import sys
	if len(sys.argv) < 3:
		check_cmd(sys.argv[1])
	elif len(sys.argv) == 3:
		_cmd(sys.argv[2], sys.argv[1])
	else:
		print ("Error: requires at least two arguments")
		
	
