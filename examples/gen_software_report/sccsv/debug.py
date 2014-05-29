import sys

DEBUG = False

def write(msg):
	if DEBUG:
		sys.stdout.write(msg)
    	sys.stdout.flush()