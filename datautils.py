__author__ = 'r.espanol'

import sys
import os
import re
import json
import shelve
import fileinput
from debug import *
from dygraph_utils import *

sarIOData = ['tps', 'rtps', 'bread', 'wtps', 'bwrtn']

sarMemoryData = ['memfree', 'memused', 'memused-percent', 'buffers', 'cached', 'commit', 'commit-percent', 'active',
				 'inactive']

sarCpuData = ['cpu', 'user', 'nice', 'system', 'iowait', 'steal', 'idle']

sarNetworkData = ['iface', 'rxpck', 'txpck', 'rxkB', 'txkB', 'rxcmp', 'txcmp', 'rxmcst']

'''
routines to run programs locally
using os.commands()

'''


def runLocalCommand(command):
	s = os.popen(command).read()
	return s


def get_statistics(jsonfile):
	json_data = open(jsonfile).read()
	data = json.loads(json_data)
	return data["sysstat"]["hosts"][0]["statistics"]


def getSarStatistics(jsonfile):
	json_data = open(jsonfile).read()
	data = json.loads(json_data)
	return data["sysstat"]["hosts"][0]["statistics"]


def get_timestamp(stat):
	return stat["timestamp"]["date"] + ":" + stat["timestamp"]["time"]


'''
sar data consists of io,memory,cpu and
network data in json format. funcs will be
need to extract data sets and data attributes
(eg. time, host where colleted..etc)
'''


def sarConvertTimeStamp(timestamp):
	date,time=timestamp.split(':')
	ftime=sarConvertTimeHyphenToColon(time)
	fdate=sarConvertDateHyphenToSlash(date)
	fdatetime=fdate + ' ' + ftime
	return fdatetime
	pass


def sarGetCpuStats(cpu_string, cpufile):
	stat_list = get_statistics(cpufile)
	result_map = {}
	for stat in stat_list:
		result_map[get_timestamp(stat)] = str(stat["cpu-load"][0][cpu_string])
	return result_map


''' retreive data for specific element of sar Cpu/memory/network or IO data from json file'''


def sarGetIoStats(io_string, iofile):
	stat_list = get_statistics(iofile)
	result_map = {}
	for stat in stat_list:
		if io_string == "rtps" or io_string == "bread":
			result_map[get_timestamp(stat)] = str(stat["io"]["io-reads"][io_string])

		elif io_string == "wtps" or io_string == "bwrtn":
			result_map[get_timestamp(stat)] = str(stat["io"]["io-writes"][io_string])
		else:
			result_map[get_timestamp(stat)] = str(stat["io"][io_string])
	return result_map


def sarGetMemoryStats(mem_string, memfile):
	stat_list = get_statistics(memfile)
	result_map = {}
	for stat in stat_list:
		result_map[get_timestamp(stat)] = str(stat["memory"][mem_string])
	return result_map


def sarGetNetworkStats(net_string, iface, netfile):
	stat_list = get_statistics(netfile)
	result_map = {}
	for stat in stat_list:
		for net_iface in stat["network"]["net-dev"]:
			if net_iface["iface"] == iface:
				result_map[get_timestamp(stat)] = str(net_iface[net_string])
	return result_map


'''
each sar data file contains a timestamp with one or more
series of data collected. we can plot multiple series but
we need functions for setting up series data. we use
multiple arrays to represent each series.
'''

'''
==================================================
 routines to save context into info.db shelve file
==================================================
'''


def saveInfo(info, key):
	s = shelve.open('info.db')
	try:
		s[key] = info
	finally:
		s.close()

	return s


def GetInfo(key):
	s = shelve.open('info.db')
	try:
		existing = s[key]
	finally:
		s.close()

	return existing


'''
from info.db, get sar stats for key
'''


def infoDbGetSarStats(key):
	dbInfo = GetInfo(key)
	return dbInfo[2]
	pass


def infoDbGetLeaves(key):
	dbInfo = GetInfo(key)
	return dbInfo[1]


'''
========================
routines for json file
flattening, leaf identification
..etc

========================
'''


def print_dict(dictionary, ident='', braces=1):
	""" Recursively prints nested dictionaries."""

	for key, value in dictionary.iteritems():
		if isinstance(value, dict):
			print '%s%s%s%s' % (ident, braces * '[', key, braces * ']')
			print_dict(value, ident + '  ', braces + 1)
		else:
			print ident + '%s = %s' % (key, value)


import sys


def showkeys(d, leaf, printit, root=''):
	import simplejson
	import urllib

	if d == '-':
		d = simplejson.load(sys.stdin)
	elif isinstance(d, str):
		d = simplejson.load(urllib.urlopen(d))

	''' print each leaf if printif flag==1 '''
	for k, v in d.items():
		if isinstance(v, str):
			if printit:
				print "%s[%s]=%r" % (root, k, v)
			leaf.append(k)

		if isinstance(v, unicode):
			if printit:
				print "%s[%s]=%r" % (root, k, v)
			leaf.append(k)

		if isinstance(v, int):
			if printit:
				print "%s[%s]=%r" % (root, k, v)
			leaf.append(k)

		if isinstance(v, float):
			if printit:
				print "%s[%s]=%r" % (root, k, v)
			leaf.append(k)

		if isinstance(v, dict):
			showkeys(v, leaf, printit, root=root + '[' + k + ']')
		#leaf.append(v)

		if isinstance(v, list):
			for i, v in enumerate(v):
				showkeys(v, leaf, printit, root=root + '[' + k + ']' + '[' + str(i) + ']')


'''
SHELVE routines - using
the shelve library to save
context data per session.

we save:
 1. file.leaf objects and sar stats for that file.
 2. per plot series data using 'default as key for 1st plot.
'''

''' shelve is used to remember: 1.file name,2. the file_name.keys array 3. the json data '''


def loadJsonFile(file, leafonly):
	leaf = []
	dbinfo = []
	if leafonly == 1:
		show = 0
	else:
		show = 1

	file_name = file.replace('.', '_', 1)
	dbinfo.append(file)

	json_leaves = []
	showkeys(file, leaf, show, root='[root]')
	leaves = set(leaf)
	for data_leaf in leaves:
		x = file_name + '.' + data_leaf
		json_leaves.append(x)
	dbinfo.append(json_leaves)

	json_data = open(file).read()
	data = json.loads(json_data)
	dbinfo.append(data)

	key = file
	saveInfo(dbinfo, key)
	return json_leaves


def loadJson(file, leavesonly=1):
	currentLeaves = getPlotInfo('info.db', 'currentleaves')
	currentJsonFiles = getPlotInfo('info.db', 'currentJsonFiles')

	#currentLeaves.append(file)
	leaves = loadJsonFile(file, leavesonly)
	print "Leaf nodes from json data:"
	dprint(3, "LoadJson(): leaves from json file %s: " % file)
	dprint(3, leaves)
	leafs = []
	for item in leaves:
		print "leaf: %s" % item
		#file_name,itemkey=item.rsplit('.',1)
		#print "key: %s" % itemkey
		leafs.append(item)
	currentLeaves.append(leafs)

	if not (file in currentJsonFiles):
		currentJsonFiles.append(file)
		saveInfo(currentJsonFiles, 'currentJsonFiles')
		saveInfo(currentLeaves, 'currentleaves')


'''
same as LoadJson() but returns statistics:
open the sar json file and extract just the
statistics items from the structure
'''


def LoadSarStats(file, printit=0):
	leaf = []
	jsondata = open(file).read()
	data = json.loads(jsondata)

	dbinfo = []
	dbinfo.append(file)
	file_name = file.replace('.', '_', 1)

	''' statistics data is same returned by get_statistics() call'''
	statistics_data = data["sysstat"]["hosts"][0]["statistics"]
	sardata = statistics_data[0]
	json_leaves = []
	showkeys(sardata, leaf, 0, root='[root]')
	leaves = set(leaf)
	for data_leaf in leaves:
		x = file_name + '.' + data_leaf
		json_leaves.append(x)
	dbinfo.append(json_leaves)
	dbinfo.append(statistics_data)
	if printit == 1:
		print "Leaf objects for json file: %s " % file
		print "--------------------------------"
		for item in leaf:
			print "leaf: %s" % item
	key = file_name
	saveInfo(dbinfo, key)
	return json_leaves, statistics_data
	pass


def convertSarDataMapToSeriesList(datamap):
	xseries = []
	yseries = []
	count = 0
	'''
	we need to transform from '-' seperated to '/'
	seperated for date and from '-' to ':' seperation
	for time.
	'''
	for key in datamap:
		datekey, timekey = key.split(':')

		ftime = sarConvertTimeHyphenToColon(timekey)
		fdate = sarConvertDateHyphenToSlash(datekey)
		fdatetime = fdate + ' ' + ftime

		xseries.append(fdatetime)
		yseries.append(datamap[key])
		count += 1
		dprint(3, "convertSarDataMapToSeriesList() - added %s to time series and %s to y-series" % (
			fdatetime, datamap[key]))
		dprint(3, xseries)
		dprint(3, yseries)
		serieslist = []
		serieslist.append(xseries)
		serieslist.append(yseries)

	return serieslist
	pass


def convertStringArrayToFloatArray(stringarray):
	farray = []
	for i in stringarray:
		#print i
		farray.append(float(i))
	return farray
	pass


def convertFloatArrayToStringArray(floatarray):
	str_array = []
	for i in floatarray:
		#print i
		str_array.append(str(i))
	return str_array
	pass


'''
sort the time series and line up
corresponding Y values to this sorted
time series.
'''


def sortSarSeries(series):
	sortedSeries = []
	sortedValues = []
	sortedTimeSeries = sorted(series[0])

	seriesLen = len(series[0])
	for i in sortedTimeSeries:
		for j in range(0, seriesLen):
			if series[0][j] == i:
				sortedValues.append(series[1][j])

	sortedSeries.append(sortedTimeSeries)
	sortedSeries.append(sortedValues)
	return sortedSeries
	pass


def getSarStatByKey(file_key):
	file_name, key_string = file_key.split('.')
	file = file_name.replace('_', '.')

	if key_string in sarIOData:
		title = 'SAR IO Data'
		mapFunc = sarGetIoStats
	elif key_string in sarCpuData:
		title = 'SAR Cpu Data'
		mapFunc = sarGetCpuStats
	elif key_string in sarMemoryData:
		title = 'SAR Memory Data'
		mapFunc = sarGetMemoryStats
	elif key_string in sarNetworkData:
		title = 'SAR Network/eth0 Data'
		mapFunc = sarGetNetworkStats
	else:
		title = 'SAR Cpu Data'
		dprint(3, 'using default map Func\n')
		mapFunc = sarGetCpuStats

	dprint(3, 'getSarStatByKey()- using SAR statistics function: %s\n' % mapFunc)

	if mapFunc == sarGetNetworkStats:
		result_map = mapFunc(key_string, 'eth0', file)
	else:
		result_map = mapFunc(key_string, file)

	return result_map


def mergeFileKeyName(filekey1, filekey2):
	filename1, key1 = filekey1.split('.')
	filename2, key2 = filekey2.split('.')
	mergedName = filename1 + '_' + key1 + '-' + filename2 + '_' + key2
	return mergedName
	pass


def getCurrentPlotByKey():
	return (GetInfo('currentplot'))
	pass


def saveCurrentPlot(plot):
	saveInfo(plot, 'currentplot')
	pass


def saveCurrentPlotKey(file_key):
	saveInfo(file_key, 'currentfilekey')
	pass


def saveCurrentPlotFile(filename):
	saveInfo(filename, 'currentfilename')
	pass


def saveCurrentPlotDygraphFile(default='dygraph.html'):
	dprint(3, "saveCurrentPlotDygraphFile(): Saving to %s" % default)
	saveInfo(default, 'currentdygraphfile')
	pass


def getCurrentPlotDygraphFile():
	return GetInfo('currentdygraphfile')


def getCurrentPlotStatus(dbfile=''):
	if dbfile:
		savedPlotFile=dbfile + '.db'
		currentplot = getPlotInfo(savedPlotFile,'currentplot')
		currentfile = getPlotInfo(savedPlotFile,'currentfilename')
		currentfilekey = getPlotInfo(savedPlotFile,'currentfilekey')
		pass
	else:
		currentplot = GetInfo('currentplot')
		currentfile = GetInfo('currentfilename')
		currentfilekey = GetInfo('currentfilekey')

	return currentfile, currentfilekey, currentplot
	pass


def saveCurrentPlotState(plot, file_key, filename):
	dprint(3, "saveCurrentPlotState(): Saving plot state: file.key=%s , file name: %s" % (file_key, filename))
	saveCurrentPlot(plot)
	saveCurrentPlotKey(file_key)
	saveCurrentPlotFile(filename)
	pass


def savePlotFile(default='dygraph.html'):
	dprint(3, "savePlotFile():  Saving to %s" % default)
	myOS = sys.platform
	if myOS == 'win32':
		command = 'copy dygraph.html %s' % default
		output = runLocalCommand(command)
	else:
		command = 'cp dygraph.html %s' % default
		output = runLocalCommand(command)

	pass


def savePlot(default=''):
	if not default:
		print "savePlot(): using default shelve file: info.db"
		pass
	else:
		print "savePlot(): using user defined shelve file name: %s" % default
		dbname = default + '.db'
		currentfile, currentfilekey, currentplot = getCurrentPlotStatus()
		''' save plot series,file_keys,dygraph file, last SAR file name to specified shelve db'''
		savePlotInfo(dbname, currentplot, 'currentplot')
		savePlotInfo(dbname, currentfilekey, 'currentfilekey')
		savePlotInfo(dbname, currentfile, 'currentfilename')
		''' now save into info.db...remember, stashed-info.db is saved version of info.db'''

		currentJsonFiles=getPlotInfo('info.db','currentJsonFiles')
		currentleaves=getPlotInfo('info.db','currentleaves')

		s=savePlotInfo(dbname, currentJsonFiles, 'currentJsonFiles')
		s=savePlotInfo(dbname, currentleaves, 'currentleaves')


def showSavedPlots():
	pass

''' load from saved plot info file to become default session plot info'''
def loadSavedPlot(savedplotfile):
	savedPlotFile=savedplotfile+'.db'
	stashedPlotFile='stashed-info.db'
	command = 'cp info.db %s' % stashedPlotFile
	output = runLocalCommand(command)
	print "loadSavedPlot() - saved current plot info to %s" % stashedPlotFile
	''' load saved plot info to become current info.db contents'''

	currentplot=getPlotInfo(savedPlotFile,'currentplot')
	currentfilekey=getPlotInfo(savedPlotFile,'currentfilekey')
	currentfilename=getPlotInfo(savedPlotFile,'currentfilename')
	currentJsonFiles=getPlotInfo(savedPlotFile,'currentJsonFiles')
	currentleaves=getPlotInfo(savedPlotFile,'currentleaves')

	''' now save into info.db...remember, stashed-info.db is saved version of info.db'''
	s=savePlotInfo(savedPlotFile, currentplot, 'currentplot')
	s=savePlotInfo(savedPlotFile, currentfilekey, 'currentfilekey')
	s=savePlotInfo(savedPlotFile, currentfilename, 'currentfilename')
	s=savePlotInfo(savedPlotFile, currentJsonFiles, 'currentJsonFiles')
	s=savePlotInfo(savedPlotFile, currentleaves, 'currentleaves')




	pass


'''
use a shelve file dbase to enter
data and key to save.
'''


def savePlotInfo(dbname, info, key):
	s = shelve.open(dbname)
	try:
		s[key] = info
	finally:
		s.close()

	return s


'''
return data given
a correct key returns
good data
'''


def getPlotInfo(dbname, key):
	s = shelve.open(dbname)
	try:
		existing = s[key]
	finally:
		s.close()

	return existing


def checkPlot():
	status = getCurrentPlotStatus()
	return status
	pass


def initPlot():
	plot = []
	file_key = []
	json_files = []
	file = 'None'
	saveCurrentPlot(plot)
	s = savePlotInfo('info.db', file_key, 'currentleaves')
	saveCurrentPlotFile(file)
	s = savePlotInfo('info.db', json_files, 'currentJsonFiles')
	s = savePlotInfo('info.db', file_key, 'currentfilekey')
	pass


'''
flush out any current plotting instance data from info.db. Also, if filename
is not default, savePlotFile() will create a new shelve db file and save
plot information to it so nothing is lost.
'''


def closePlot(filename=''):
	plot = []
	file_key = []
	json_files = []
	file = 'None'
	saveCurrentPlot(plot)
	s = savePlotInfo('info.db', file_key, 'currentleaves')
	saveCurrentPlotFile(file)
	s = savePlotInfo('info.db', json_files, 'currentJsonFiles')
	s = savePlotInfo('info.db', file_key, 'currentfilekey')
	if filename:
		savePlotFile(filename)
		print "closePlot(): Saved plot info to shelve db: %s" % filename
		return
	else:
		return
	pass


def openPlot():
	currentfile, currentfilekey, currentplot = getCurrentPlotStatus()
	if 'no_file.no_key' in currentfilekey:
		print "openPlot(): Inactive plot session. Use plot() command to start new session..."
	else:
		print "openPlot(): Trying to open running session files, you must closePlot() first to make inactive"


def showJsonLeaves(filename=''):
	leaves = getPlotInfo('info.db', 'currentleaves')
	if filename:
		print "\nusing file : %s" % filename
		print "================="
		#convert filename to file_name format
		# and print out keys in leaves list
		file_name = filename.replace('.', '_')
		for i in range(0, len(leaves)):
			# print "current leaves: "
			# print leaves[i]
			if file_name in str(leaves[i]):
				for item in leaves[i]:
					print item

	else:
		print "\nShowing all loaded json file-keys:\n"
		print "================="
		for i in range(0, len(leaves)):
			for item in leaves[i]:
				print item
			#print leaves
	pass


def listSarData(file_key, lines=''):
	linecount = 0
	sarStats = getSarStatByKey(file_key)
	for key in sarStats:
		print "%s: %s " % (str(key), str(sarStats[key]))
		linecount += 1
		if (lines):
			if (linecount % lines) == 0:
				raw_input('Press enter for more lines... :')
	print "Listed: %s Sar items." % linecount
	pass


def listSarSeriesData(file_key, lines=''):
	linecount = 0
	sarStats = getSarStatByKey(file_key)
	#this sorts the time series (keys) but
	# not the key-value pairings
	sortedSarStats=sorted(sarStats)
	#print sortedSarStats
	for k in sortedSarStats:
		seriesDateTime=sarConvertTimeStamp(k)
		print "%s - %s " %(seriesDateTime,sarStats[k])
		linecount+=1

	# for key in sarStats:
	# 	seriesDateTime=sarConvertTimeStamp(key)
	# 	print "%s: %s " % (seriesDateTime, str(sarStats[key]))
	# 	linecount += 1
		if (lines):
			if (linecount % lines) == 0:
				raw_input('Press enter for more lines... :')
	print "Listed: %s Sar items." % linecount
	pass


def fileKeyAlreadyPlotted(file_key):
	currFilekey = getPlotInfo('info.db', 'currentfilekey')
	if file_key in currFilekey:
		print "fileKeyAlreadyPlotted(): found %s in current plot already!" % file_key
		return 1
	else:
		return 0
	pass


'''
convert a series list time series into
zero-time(time begins at zero) onward.
'''


def convertTimeSeriesToZeroStart(series):
	xlen = len(series[0])
	numYseries = len(series)

	print "convertTimeSeriesToZeroStart() - series to convert is length: %d" % xlen
	if xlen:
		newSeries = []
		convertedTimeSeries = []
		convertTimeSeries = range(0, xlen)
		print "convertTimeSeriesToZeroStart() - converted SAR times to zero-time:"
		print convertTimeSeries
		newSeries.append(convertTimeSeries)

		#add the Y series to this converted time-series
		print "convertTimeSeriesToZeroStart() - adding %d" % numYseries
		for i in range(1, numYseries):
			newSeries.append(series[i])

		return newSeries


