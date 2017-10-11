


debuglevel=0




def setdebug(default=0):
	global debuglevel
	if not default:
		print "using default debug level: 0"
	else:
		print "Setting debug level to %s" % default
		debuglevel = default
        print debuglevel
	pass

def getdebug():
    global debuglevel
    return debuglevel

def dprint(level, msg):
    if debuglevel >= level:
        print msg

    pass