import json
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from debug import *
from datautils import *
from dygraph_utils import *
#from userPlot import *


sarIOData=['tps','rtps','bread','wtps','bwrtn']

sarMemoryData=['memfree','memused','memused-percent','buffers','cached','commit','commit-percent','active','inactive']

sarCpuData=['cpu','user','nice','system','iowait','steal','idle']

sarNetworkData=['iface','rxpck','txpck','rxkB','txkB','rxcmp','txcmp','rxmcst']


def Help():
	print "\nSAR Plot Utilities Help :\n\n"
	print "+ LoadJson(filename)- load a json SAR file and show leaves of structure.\n\n"
	print "+ plot(file.key)- create dygraph plot of filename.key item where filename.key \n       specifies the file and SAR item to plot\n       eg. plot('network_json.rxpck')\n\n"
	print "+ addPlot(file.key) - plot new file.key item using last plot data, creating 2 or more \n      Y series in same plot\n         eg.  addPlot('network_json.txpck','2014/06/03 23:01:17')\n\n"
	print "+ plotSarMovingAvg('network2_json.txkB',4 )- given file-key and \n         interval eg.2,plot moving average\n\n"
	print "+ closePlot(filename) - save current plot to shelve file filename.db if given.\n         and set context database to \'Nothing\'\n      NOTE: all plot info is erased.\n\n"
	print "+ savePlot(file_db_name) - save the current plot array to new named context \n        database: \'file_db_name eg. \'mysaved\' \n\n"
	print "+ openPlot() - check the open state of current plot, indicates inactive \n         or opened session is current and closePlot() makes the state inactive, plot() creates\n  and opens new session.\n"
	print "+ renderDyGraphWebPage(dygraph-sar.html) - invokes user's browser to render the HTML page generated from seriesListToDygrahp() API call \n\n"
	print "+ seriesListToDygraph('newplot.html','sar time stamp','wtps\,rtps',plot,'New SAR wtps plot')"
	print "+ showJsonLeaves(filename) - shows keys for the json SAR data file name given, if no args all leaves will be dumped\n\n"
	print "+ listSarData('io_json.wtps',10 ) - list out SAR data using \'key:value\' format.keys are time stamps.\n      optional number of lines to show and pause, pressing <CR> continues listing next number of lines.\n\n"
	print "+ plotFromSaved() - plot a dygraph using the saved data from current session ('info.db')\n\n"
	print "+ plotSeriesList(series_list,YseriesLabels) - plot a dygraph using series_list and optional \n      series labels.YsereisLabels is a list of SAR data keys\n    eg.  ['io_json.wtps',network_json.rxpck'] "


def HelpTools():
	print "\nSAR Plot Helper Utilities Help :\n\n"
	print "+ rmap=getSarStatByKey('file_name.key')- extract the SAR data from json file for specified key into data map.\n\n"
	print "+ slist=convertSarDataMapToSeriesList(rmap) - convert the result map (data map format) into dygraph series format\n\n"
	print "+ plotSeriesList(slist) - render a dygraph HTML file of plotted series list (slist) - named dygraph-UnknownPlot.html\n\n"
	print "+ getPlotInfo('info'.db','key') - show the shelve database data based on the \'key\'. eg. \'currentfilekey\'\n        other keys:\'currentfilename\',\'currentplot\' and \'currentleaves\'.\n\n"
	print "+ checkPlot()- dump out session database ('info.db') contents for current plot.\n\n"
	print "+ alignSeriesList(seriesList) - take seriesList, sort the time series and make \n      sure Y series line up with correct data/times (keys)\n\n"
	print "+ alignedSeriesCombine(series1,series2) - given two aligned series lists, combine into one series.\n       Aligned means each series is sorted and both series have the same X-series (keys).\n\n"

	pass

def _compare_keys(x, y):
	if x[len(x)-1]=='k':
		x=x[:-1]
	if y[len(y)-1]=='k':
		y=y[:-1]
	try:
		x = int(x)
	except ValueError:
		xint = False
	else:
		xint = True
	try:
		y = int(y)
	except ValueError:
		if xint:
			return -1
		return cmp(x.lower(), y.lower())
		# or cmp(x, y) if you want case sensitivity.
	else:
		if xint:
			return cmp(x, y)
		return 1

def plot_2d(x_label, y_label, output_string, result_map, directory):
	xLabel = x_label
	yLabel = y_label
	yaxis = []
	xaxis  = []
	for key in sorted(result_map, cmp=_compare_keys):
		if result_map[key]!=None:
			xaxis.append(key)
			if isinstance(result_map[key],list):
				yaxis.append(result_map[key][0])
			else:
				yaxis.append(result_map[key])

	print xaxis
	print "Length xaxis: " +str(len(xaxis))
	print yaxis
	print "Length yaxis: " +str(len(yaxis))
	if len(yaxis)==0:
		return
	fig, ax = plt.subplots()
#	ax.set_xscale('log')
	plt.xticks(range(len(xaxis)),xaxis,rotation='vertical')
	ax.plot(range(len(xaxis)),yaxis,'--',color='k', markersize=10)
	plot_name = output_string

	ax.set_title (plot_name)
	ax.set_xlabel(xLabel)
	ax.set_ylabel(yLabel)

	plot_name = plot_name+'.png'
	plt.show(block=False)
#	plt.savefig(directory+plot_name, bbox_inches=0)
#	plt.close()
	return None

def get_statistics(jsonfile):
	json_data = open(jsonfile).read()
	data = json.loads(json_data)
	return data["sysstat"]["hosts"][0]["statistics"]

def get_timestamp(stat):
	return stat["timestamp"]["date"]+":"+stat["timestamp"]["time"]

def plot_cpu_sar_data(cpu_string, cpufile):
	result_map=sarGetCpuStats(cpu_string, cpufile)
	dygraphfile="dygraph-sar.html"
	dataMapToDygraph(dygraphfile,'Time','Plot of %s' % cpu_string,result_map,'CPU Stats:')
	renderDyGraphWebPage(dygraphfile)
	plot_2d("Time",cpu_string,"Plot of "+cpu_string+" vs Time",result_map,"./")

##	render_dygraph(keylist,result_map)

def plot_io_sar_data(io_string, iofile):
	#stat_list=get_statistics(iofile)
	result_map=sarGetIoStats(io_string, iofile)
	plot_2d("Time",io_string,"Plot of "+io_string+" vs Time",result_map,"./")
	xlabel='Time'
	ylabel='Plot of %s' % io_string
	createDygraph(xlabel,ylabel,result_map,'SAR IO Stats:')
	dprint (3,result_map)

def plot_memory_sar_data(mem_string, memfile):
	stat_list=get_statistics(memfile)
	result_map={}
	for stat in stat_list:
		result_map[get_timestamp(stat)] = str(stat["memory"][mem_string])
	plot_2d("Time",mem_string,"Plot of "+mem_string+" vs Time",result_map,"./")

def plot_network_sar_data(net_string, iface, netfile):
	stat_list=get_statistics(netfile)
	result_map={}
	for stat in stat_list:
		for net_iface in stat["network"]["net-dev"]:
			if net_iface["iface"] == iface:
				result_map[get_timestamp(stat)] = str(net_iface[net_string])
	plot_2d("Time",net_string,"Plot of "+net_string+" vs Time",result_map,"./")

'''
given an array of strings indicating which
data key to use, generate an array of
multiple series data arrays.
can only be used for same SAR file/same keys
'''
def plot_SarMultipleSeries(datafile,dataList):
	xSeries=[]
	thisSeries=[]
	seriesList=[]
	dtype=type(dataList)
	if str(dtype) == "<type 'str'>":
		dprint (3,'plot_SarMultipleSeries: data list is single string')
		data=dataList
		dataIsString=True
	elif str(dtype) == "<type 'list'>" :
		dprint (3,'plot_SarMultipleSeries: data list is list')
		data=dataList[0]
		dataIsString=False


	#data=dataList[0]
	if data in sarIOData:
		dprint (3,'plot_SarMultipleSeries:using sarGetIoStats\n')
		mapFunc=sarGetIoStats
	elif data in sarCpuData:
		dprint (3,'using sarGetCpuStats\n')
		mapFunc=sarGetCpuStats
	elif data in sarMemoryData:
		dprint (3,'using sarGetMemoryStats\n')
		mapFunc=sarGetMemoryStats
	elif data in sarNetworkData:
		dprint (3,'using sarGetNetworkStats\n')
		mapFunc=sarGetNetworkStats
	else:
		dprint (3,'using default map Func\n')
		mapFunc=sarGetCpuStats

		dprint (3,"Map func=%s" % mapFunc)
	if dataIsString==False:
		dprint (3,"Using List data: " + str(data))
		for i,item in enumerate(dataList):
			if mapFunc==sarGetNetworkStats:
				result_map=mapFunc(item,'eth0',datafile)
			else:
				result_map=mapFunc(item,datafile)

			#result_map=mapFunc(item,datafile)
			#result_map=sarGetIoStats(item, datafile)
			''' retrieve the time series (x axis) values '''
			if i == 0:
				for k in result_map.keys():
					xSeries.append(k)
					value=result_map[k]
					thisSeries.append(value)
				seriesList.append(xSeries)
				seriesList.append(thisSeries[:])
			else:
				'''get all other non-time series values'''
				for k in result_map.keys():
					thisSeries.append(result_map[k])
				seriesList.append(thisSeries[:])
			del thisSeries[:]
	elif dataIsString==True:
		dprint (3,"Using String data:%s" % data)
		if mapFunc==sarGetNetworkStats:
			result_map=mapFunc(data,'eth0',datafile)
		else:
			result_map=mapFunc(data,datafile)
		for k in result_map.keys():
			xSeries.append(k)
			value=result_map[k]
			thisSeries.append(value)
			seriesList.append(xSeries)
			seriesList.append(thisSeries[:])
	return seriesList
	pass

import numpy as np
nan = np.nan


'''
using numpy,nan's to fill null values
in data arrays with holes, interpolate
values for each nan hole in an array.
given a normal no-holes array, it leaves
as is.
'''
def interp(A):
	ok = -np.isnan(A)
	xp = ok.ravel().nonzero()[0]
	fp = A[-np.isnan(A)]
	x  = np.isnan(A).ravel().nonzero()[0]
	A[np.isnan(A)] = np.interp(x, xp, fp)
	pass


'''
for the new combined time series, check
each Y data element and if there is not
a matching time stamp (x coord) then make
it a NaN. linear interpolation will convert
NaN to usable value later. return numpy array

'''
def createNumpyArray(newtimeseries,series1,series2):
	global debuglevel
	nan=np.nan
	'''
	 check each time series for
	 a corresponding y1 and y2 value.
	 if not there, use a 'nan'
	'''

	y_new1=[]
	y_new2=[]
	timeserieslength=len(newtimeseries)
	for i in range(0,timeserieslength):
		dprint (3,newtimeseries[i])
		if newtimeseries[i] in series1[0]:
			dprint (3,"createNumpyArray(): member of series 1.")
			y0=series1[1][series1[0].index(newtimeseries[i])]
			dprint (3,y0)
			y_new1.append(float(y0))

		else:
			y_new1.append(nan)
			y0=nan
	for j in range(0,timeserieslength):
		if newtimeseries[j] in series2[0]:
			dprint (3,"createNumpyArray(): member of series 2.")
			y0=series2[1][series2[0].index(newtimeseries[j])]
			dprint (3,y0)
			y_new2.append(float(y0))
		else:
			y_new2.append(nan)
			y0=nan
	return y_new1,y_new2



def createSingleNumpyArray(newtimeseries,series):
	global debuglevel
	nan=np.nan
	y_new1=[]
	timeserieslength=len(newtimeseries)
	for i in range(0,timeserieslength):
		dprint (3,newtimeseries[i])
		if newtimeseries[i] in series[0]:
			dprint (3,"createNumpyArray(): member of series 1.")
			y0=series[1][series[0].index(newtimeseries[i])]
			dprint (3,y0)
			y_new1.append(float(y0))

		else:
			y_new1.append(nan)
			y0=nan

	return y_new1





def combineTimeSeries(series1,series2):
	print "combineTimeSeries(): operating on series1,series2:"
	print series1
	print series2
	'''
	take time series and combine
	into one time series.
	'''
	xseries=series1[0][:]
	dprint (3,"combineTimeSeries(): x-series values:")
	dprint (3,xseries)


	xseries.extend(series2[0][:])
	newseries=sorted(set(xseries))
	print "combineTimeSeries(): returning this new series:"
	dprint (3,sorted(set(xseries)))
	return newseries

def mergeSeriesLists(serieslist1,serieslist2):
	newseries=combineTimeSeries(serieslist1,serieslist2)
	print "mergeSeriesLists(): new combined series:"
	print newseries

	y_1,y_2=createNumpyArray(newseries,serieslist1,serieslist2)

	IO=np.array(y_1)
	NW=np.array(y_2)
	interp(NW)
	dprint (3,"interpolated y1 list:")
	dprint (3,NW)


	interp(IO)
	dprint (3,"interpolated y2 list:")
	dprint (3,IO)

	seriesList=[]
	seriesList.append(newseries)
	seriesList.append(NW.tolist())
	seriesList.append(IO.tolist())
	return seriesList

def mergeSeries(stats1,stats2,file1,file2):
	
	series1=plot_SarMultipleSeries(file1,stats1)
	series2=plot_SarMultipleSeries(file2,stats2)

	newseries=combineTimeSeries(series1,series2)
	y_1,y_2=createNumpyArray(newseries,series1,series2)

	IO=np.array(y_1)
	NW=np.array(y_2)
	interp(NW)
	dprint (3,"interpolated y1 list:")
	dprint (3,NW)


	interp(IO)
	dprint (3,"interpolated y2 list:")
	dprint (3,IO)

	seriesList=[]
	seriesList.append(newseries)
	seriesList.append(NW.tolist())
	seriesList.append(IO.tolist())
	return seriesList
	pass

def combineSeriesLists(timeSeries,series1,series2):
	y_1,y_2=createNumpyArray(timeSeries,series1,series2)

	IO=np.array(y_1)
	NW=np.array(y_2)
	interp(NW)
	dprint (3,"interpolated y1 list:")
	dprint (3,NW)


	interp(IO)
	dprint (3,"interpolated y2 list:")
	dprint (3,IO)

	seriesList=[]
	seriesList.append(timeSeries)
	seriesList.append(NW.tolist())
	seriesList.append(IO.tolist())
	return seriesList
	pass

def get_timestamp(stat):
	return stat["timestamp"]["date"]+":"+stat["timestamp"]["time"]

def sarConvertDateHyphenToSlash(date):
	xdate=re.sub('-','/',date)
	return xdate
	pass


def sarConvertTimeHyphenToColon(time):
	xtime=re.sub('-',':',time)
	return xtime
	pass

'''
sar data consists of io,memory,cpu and
network data in json format. funcs will be
need to extract data sets and data attributes
(eg. time, host where colleted..etc)
'''
def sarConvertTimeStamp(timestamp):
	pass

def sarGetCpuStats(cpu_string, cpufile):
	stat_list=get_statistics(cpufile)
	result_map={}
	for stat in stat_list:
		result_map[get_timestamp(stat)] = str(stat["cpu-load"][0][cpu_string])
	return result_map

''' retreive data for specific element of sar Cpu/memory/network or IO data from json file'''
def sarGetIoStats(io_string, iofile):
	stat_list=get_statistics(iofile)
	result_map={}
	for stat in stat_list:
		if io_string == "rtps" or io_string == "bread":
			result_map[get_timestamp(stat)] = str(stat["io"]["io-reads"][io_string])

		elif io_string == "wtps" or io_string == "bwrtn":
			result_map[get_timestamp(stat)] = str(stat["io"]["io-writes"][io_string])
		else:
			result_map[get_timestamp(stat)] = str(stat["io"][io_string])
	return result_map

def sarGetMemoryStats(mem_string, memfile):
	stat_list=get_statistics(memfile)
	result_map={}
	for stat in stat_list:
		result_map[get_timestamp(stat)] = str(stat["memory"][mem_string])
	return result_map

def sarGetNetworkStats(net_string, iface, netfile):
	stat_list=get_statistics(netfile)
	result_map={}
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



def plotStats(stats,key):
	pass


'''
given an array, determine
the simple moving average based
on window (interval before/after)
and return the starting index of
data point which was a valid
candidate for averages and the
array of moving avg. values.

usage: startindex,simpleMovingAvgArray=movingaverage(list,5)

'''
def movingaverage (values, window):
	startPt=window-1
	weights = np.repeat(1.0, window)/window
	#sma = np.convolve(values, weights, 'valid')
	sma = np.convolve(values, weights)[startPt:-(startPt)]
	return startPt,sma


'''
a series is a list containing a time-series and y-series.
you must construct such a list to pass to calcMovingAvg().
It extracts the y-series, calculates a new array with moving
averages and fills the holes (invalid points) with 'none'
values.
'''
def seriesCalcMovingAvg(series,window):

	y=series[1]
	startIndex,yMA = movingaverage(y,3)
	dprint (3,yMA)
	'''
	convert to python List
	then fill the holes with none
	'''
	yma=yMA.tolist()

	for i in range (0,startIndex):
		yma.insert(0,None)

	dprint (3,"seriesCalcMovingAvg(): bappending moving avg to seriesList and printing:")
	series.append(yma)
	return series

''' pass this a SAR string valued Y series
   to calculate moving average of Y series
   and return the Y-moving avg array
'''
def arrayCalcMovingAvg(stringArray,window):

	y=convertStringArrayToFloatArray(stringArray)

	startIndex,yMA = movingaverage(y,window)
	dprint (3,yMA)
	'''
	convert to python List
	then fill the holes with none
	'''
	yma=yMA.tolist()

	for i in range (0,startIndex):
		yma.insert(0,None)
	return yma


# def plotMovingAvg(series,window):
# 	seriesList=seriesCalcMovingAvg(series,3)
# 	dprint (3,seriesList)
#
# 	chartTitle='Series Plot with Simple Moving Avg:'
# 	dygraphfile="dygraph-sar.html"
# 	xlabel='Time'
# 	ylabel='Plot of X-Y,Moving Avg'
#     seriesListToDygraph(dygraphfile,xlabel,ylabel,seriesList,chartTitle)
# 	renderDyGraphWebPage(dygraphfile)
#

def sarSeriesPlotMovingAvg(key,serieslist,window):
	xsorted=sorted(serieslist[0])

	''' note: need func to adjust values to sorted time keys'''

	plotseries=[]
	plotseries.append(xsorted)
	plotseries.append(serieslist[1])
	yMA=arrayCalcMovingAvg(serieslist[1],2)
	plotseries.append(yMA)

	seriesLabel='%s,movingAvg' % key
	ylabel=[]
	ylabel.append(str(key))
	ylabel.append('moving Avg')

	seriesListToDygraph('movAvg.html','date/time',seriesLabel,plotseries,'Moving Average Plot of %s'% key,ylabel)
	renderDyGraphWebPage('movAvg.html')

	pass

def alignSeriesList(seriesList):
	sorted_series=sortSarSeries(seriesList)
	return sorted_series
	pass




def plotSarMovingAvg(key,window):
	rmap=getSarStatByKey(key)
	slist=convertSarDataMapToSeriesList(rmap)
	series=alignSeriesList(slist)
	sarSeriesPlotMovingAvg(key,series,window)
	pass


def plotByFileKey(file_key):
	infokey='plot'+ file_key
	file_name,key_string=file_key.split('.')
	file=file_name.replace('_','.')
	title='Plot of %s:%s' % (file,key_string)

		#open the shelve database to get current json files loaded
	currentJsonFiles=getPlotInfo('info.db','currentJsonFiles')
	print currentJsonFiles
	if not(file in currentJsonFiles):
		print ("file-key combination not loaded, Please use \'loadJson(\'file.json\') to load keys.")
		return
	else:
		yLabel=[]
		yLabel.append(key_string)
		rmap=getSarStatByKey(file_key)
		slist=convertSarDataMapToSeriesList(rmap)
		series=alignSeriesList(slist)
		saveInfo(series,infokey)
		seriesListToDygraph('dygraph-sar.html','Date-Time',key_string,series,title,yLabel)
		renderDyGraphWebPage('dygraph-sar.html',1)
		dprint (3,"Saved plot series data as %s" %infokey)

	keys=getPlotInfo('info.db','currentfilekey')
	if not (file_key in keys):
		keys.append(file_key)
		saveCurrentPlot(series)
		saveCurrentPlotKey(keys)
		saveCurrentPlotFile(file)
	#saveCurrentPlotDygraphFile()
	pass






def SarPlot(file_key):
	import fileinput as input
	file_name,key_string=file_key.split('.')
	file=file_name.replace('_','.')

	if key_string in sarIOData:
		title='SAR IO Data'
		mapFunc=sarGetIoStats
	elif key_string in sarCpuData:
		title='SAR Cpu Data'
		mapFunc=sarGetCpuStats
	elif key_string in sarMemoryData:
		title='SAR Memory Data'
		mapFunc=sarGetMemoryStats
	elif key_string in sarNetworkData:
		title='SAR Network/eth0 Data'
		mapFunc=sarGetNetworkStats
	else:
		title='SAR Cpu Data'
		#print 'using default map Func\n'
		mapFunc=sarGetCpuStats

	dprint (3,'SarPlot(): using SAR statistics function: %s\n' % mapFunc)

	if mapFunc==sarGetNetworkStats:
		result_map=mapFunc(key_string,'eth0',file)
	else:
		result_map=mapFunc(key_string,file)


	xlabel='Time'
	ylabel='Plot of %s' % key_string
	createDygraph(xlabel,ylabel,result_map,title)
	dprint(3, "SarPlot(): X and Y series:")
	dprint (3,result_map)
	pass

def addPlot(file_key,starttime='',zero=''):
	keystatus=fileKeyAlreadyPlotted(file_key)
	if keystatus==1:
			print "addPlot(): this key is already plotted, use plot() to do again."
			return

	if starttime:
		if zero:
			combineWithCurrentPlot(file_key,starttime)
		else:
			mergeWithCurrentPlot(file_key,starttime)

	else:
		addToSavedPlotWithoutStartTime(file_key)
	pass


def oldaddPlot(file_key):
	#addToSavedPlot(file_key)
	pass


def setDebug(level):
	setdebug(level)





'''====== generic conversion utilities ==='''
'''
convert the 2014/03/12 00:00:15 format
back to 2013-03-12:00-00-15 SAR format
'''
def convertDygraphTimeFormatToSarFormat(timeseries):
	newTimeSeries=[]
	for item in timeseries:
		dprint (3,"converting into SAR format: %s" % item)
		sardate=item.split(' ')
		odate=sardate[0]
		otime=sardate[1]
		newitem=odate.replace('/','-',2)
		newitem2=otime.replace(':','-',2)
		newitem3='%s %s'% (str(newitem),str(newitem2))
		dprint (3,"replaced: %s" % newitem3)
		newTimeSeries.append(newitem3)
	return newTimeSeries
	pass

def convertSarTimeSeriesToDygraphFormat(dyGraphTimeseries):
	newTimeSeries=[]
	for item in dyGraphTimeseries:
		dprint (3,"converting into SAR format: %s" % item)
		odate,otime=item.split(':')
		newitem=odate.replace('-','/',2)
		newitem2=otime.replace('-',':',2)
		newitem3='%s %s'% (str(newitem),str(newitem2))
		dprint (3,"replaced: %s" % newitem3)
		newTimeSeries.append(newitem3)
	return newTimeSeries
	pass


''' interpolate a series with possible holes '''
def interpolateYSeries(xseries,series):
	ynum3b=createSingleNumpyArray(xseries,series)
	ynump3b=np.array(ynum3b)
	interp(ynump3b)
	return ynump3b.tolist()
	pass


''' interpolated and add series to a saved plot '''
def plotAddSeries(newseries):
	'''
	 -series list X-values are in dygraph form already
	 so you must either convert to SAR format or convert
	 sar series to dygraph format (eg 2014/02/12 00:12:11).
	 -also, series lists are already sorted before being plotted
	 as dygraph and saved so no alignSeriesList() is required.

	 -just combine time series, align the new Y-series to combined
	 x-series and append all saved y-series to plot list.
	'''

	#get the saved plot from shelve db should already be in dygraph xseries format.
	plot=getPlotInfo('info.db','currentplot')


	# 1. determine how many y-series there are in this saved plot:
	yseriesLength=len(plot)

	pplot=[]


	pplot.append(plot[0])
	#pplot.append(plotTimeSeries)
	pplot.append(plot[1])

	#sort and combine saved(pplot) and new series into one.
	nxs2=combineTimeSeries(newseries,pplot)
	print "combined time series list:"
	print nxs2
	ynum3a=createSingleNumpyArray(nxs2,newseries)
	ynump3a=np.array(ynum3a)

	#interpolate new series as numpy array
	interp(ynump3a)
	slist=[]
	slist.append(nxs2)
	#convert and append to series list be plotted
	slist.append(ynump3a.tolist())

	'''
	append the rest of the saved plot y-series lists
	to the complete serieslist
	'''

	for k in range (1,yseriesLength):
		savedplotseries=[]
		savedplotseries.append(plot[0])
		print plot[k]
		savedplotseries.append(plot[k])
		#interpolate Y series from saved plot against combined x-series
		interpedPlot=interpolateYSeries(nxs2,savedplotseries)
		slist.append(interpedPlot)
		pass


	#slist.append(interpedPlot)
	print "combined series list:"
	print slist
	return slist
	pass


''' given a new file_name.key format arg,
	convert to file.name and SAR data key,
	create a new series and plot.
	NOTE : used to be addToSavedPlot()
'''
def addToSavedPlotWithoutStartTime(file_key):
	''' get series for new key to add to this plot'''
	file_name,key_string=file_key.split('.')
	file=file_name.replace('_','.')
	klist=[]
	key=str(key_string)
	klist.append(key)

	#check if that file is loaded.
	currentJsonFiles=getPlotInfo('info.db','currentJsonFiles')
	if not(file in currentJsonFiles):
		print ("file-key combination not loaded, Please use \'loadJson(\'file.json\') to load keys.")
		return
	else:
		#file is loaded, now check if keys already plotted
		plottedLeaves=getPlotInfo('info.db','currentfilekey')
		print " current keys %s " % plottedLeaves
		if (file_key in  plottedLeaves):
			print "key %s in current keys already!" %key_string
			return
		else:
			ys1=plot_SarMultipleSeries(file,klist)
			sortedslist=alignSeriesList(ys1)


			addseries=convertSarTimeSeriesToDygraphFormat(sortedslist[0])
			#addseries2=convertDygraphTimeFormatToSarFormat(sortedslist[0])
			sarTimeFormatted=[]
			sarTimeFormatted.append(addseries)
			sarTimeFormatted.append(sortedslist[1])


			slist=plotAddSeries(sarTimeFormatted)
			dygraphfile='dygraph-sar.html'
			plotTitle='SAR Series Plot'
			ylabel='SAR Statistic Values'
			xlabel='Time'



			dbname='info.db'

			#get the current file key list and update with new file.key
			getkey=getPlotInfo(dbname,'currentfilekey')
			getkey.append(file_key)
			print "Current file key(s):"
			print getkey

			currentfile=dygraphfile
			savePlotInfo(dbname, slist, 'currentplot')
			savePlotInfo(dbname, getkey, 'currentfilekey')
			savePlotInfo(dbname, currentfile, 'currentfilename')

			#createDygraphSeriesPlot(dygraphfile,slist,plotTitle,xlabel,ylabel)
			ylabels=createDygraphYLabel()
			seriesListToDygraph(dygraphfile,xlabel,ylabel,slist,plotTitle,ylabels)
			#renderDyGraphWebPage(dygraphfile)
			print "Current plot saved as %s" % currentfile
	pass


def updateSavedFileKey(new_filekey):

	pass

def createDygraphYLabel():
	Ylabel=[]
	fk=getPlotInfo('info.db','currentfilekey')
	for item in fk:
		file_name,key=item.split('.')
		print file_name
		print key
		Ylabel.append(key)
	return Ylabel

	pass

def plotFromSaved():
	series=getPlotInfo('info.db','currentplot')
	YLabel=createDygraphYLabel()
	dygraphfile='dygraph-sar.html'
	plotTitle='SAR Series Plot'
	ylabel='SAR Statistics Values'
	xlabel='Time'
	seriesListToDygraph(dygraphfile,xlabel,ylabel,series,plotTitle,YLabel)
	renderDyGraphWebPage(dygraphfile,1)
	pass


def plotMovingAvg(series,window):
	seriesList=seriesCalcMovingAvg(series,3)
	dprint (3,seriesList)
	YLabel=createDygraphYLabel()
	chartTitle='Series Plot with Simple Moving Avg:'
	dygraphfile="dygraph-sar.html"
	xlabel='Time'
	ylabel='Plot of X-Y,Moving Avg'
	seriesListToDygraph(dygraphfile,xlabel,ylabel,seriesList,chartTitle,)
	renderDyGraphWebPage(dygraphfile)


def plotSeriesList(series,seriesLabel=''):
	dygraphfile='dygraph-sar.html'
	plotTitle='SAR Series Plot'
	ylabel='SAR Statistics Values'
	xlabel='Time'
	#YLabel=['unknown']
	if seriesLabel:
		YLabel=[]
		YLabel.extend(seriesLabel)
	else:
		YLabel=createDygraphYLabel()
	seriesListToDygraph(dygraphfile,xlabel,ylabel,series,plotTitle,YLabel)
	renderDyGraphWebPage(dygraphfile,1)
	pass


def plot(filekey,starttime=''):
	if starttime:
		print "using start time: %s " % str(starttime)
		sarStats=getSarStatByKey(filekey)
		# note: series list is [ [x-series],[y1-series],...[yn-series]]
		seriesList=convertSarDataMapToSeriesList(sarStats)
		#aligh Y data to correct time values
		sortedseries=sortSarSeries(seriesList)
		newSeries=getSeriesListWithStartTime(sortedseries,starttime)
		if newSeries:
			plotSeriesList(newSeries)
			s=saveInfo(newSeries,'currentplot')
			file_key=[]
			file_key.append(filekey)
			print "plot()- saving file-key %s" %str(filekey)
			s=saveInfo(file_key,'currentfilekey')
			s=saveInfo('dygraph-sar.html','currentfile')
		else:
			print "plot(): no series created containing start time %s" %str(starttime)
	else:
		plotByFileKey(filekey)



def addSarSeriesWithStartTime(file_key,starttime=''):
	currPlotList=getPlotInfo('info.db','currentplot')
	currKey=getPlotInfo('info.db','currentfilekey')
	if currKey:
		key=currKey[0]
		file_name,key_string=key.split('.')
	else:
		print "No current plot keys found! , use plot() to create current plot..."
		return

	if starttime:
		file_name2,key_string2=file_key.split('.')
		sarStat=getSarStatByKey(file_key)
		sarseriesList=convertSarDataMapToSeriesList(sarStat)
		newSeries1=getSeriesListWithStartTime(sarseriesList,starttime)
		newSeries2=getSeriesListWithStartTime(currPlotList,starttime)
		print "finished merging series with starttime: %s" %str(starttime)
		print newSeries1
		print newSeries2
		if newSeries1 and newSeries2:
			print "Start time at : %s was found for current plot and added series!" % str(starttime)
			file_name2,key_string2=file_key.split('.')
			# sarStat=getSarStatByKey(file_key)
			# seriesList=convertSarDataMapToSeriesList(sarStat)
			mergedSeries=mergeSeriesLists(newSeries1,newSeries2)
			print "merged series: "
			print mergedSeries
			seriesLabel=[]
			seriesLabel.append(key_string)
			seriesLabel.append(key_string2)
			print seriesLabel
			plotSeriesList(mergedSeries,seriesLabel)
			#plotSeriesList(newSeries)
		else:
			print "plot(): no X-series created containing start time %s in one of current plot or added series!" %str(starttime)
			return
	else:
		print "You must provide a start time for 2nd series list"
		return




''' given a file_name.key, add this to current plotted series list'''
def addSeriesByKeyAndPlot(file_key):
	currPlotList=getPlotInfo('info.db','currentplot')
	currKey=getPlotInfo('info.db','currentfilekey')
	key=currKey[0]
	file_name,key_string=key.split('.')

	file_name2,key_string2=file_key.split('.')
	sarStat=getSarStatByKey(file_key)
	seriesList=convertSarDataMapToSeriesList(sarStat)
	mergedSeries=mergeSeriesLists(currPlotList,seriesList)
	seriesLabel=[]
	seriesLabel.append(key_string)
	seriesLabel.append(key_string2)
	plotSeriesList(mergedSeries,seriesLabel)

'''
userPlot.py stuff
'''

''' given start-time, create series list starting at start-time'''
def getSeriesListWithStartTime(serieslist,starttime):
	new_serieslist=[]
	xlen=len(serieslist[0])
	new_xseries=[]
	idx=-1
	count=0
	print "getSeriesListWithStartTime(): x length: %s" % xlen
	xseries=serieslist[0]

	print "getSeriesListWithStartTime(): examining series for start time:"
	print xseries

	# create x -series
	for x in xseries:
		if starttime in x:
			if idx==-1:
				idx=count
		count+=1

	if idx==-1:
		print "getSeriesListWithStartTime(): getSeriesListWithStartTime: start time: %s not found!" % str(starttime)
		return new_serieslist
	else:
		print "getSeriesListWithStartTime(): starting index: %s" %str(idx)
	#create the new x series
	for k in range(idx,xlen):
		new_xseries.append(xseries[k])


	ylen=len(new_xseries)
	print "getSeriesListWithStartTime(): Y length: %s" % str(ylen)
	new_serieslist.append(new_xseries)
	#create new Y-series
	# for all Y series
	for i in range(1,len(serieslist)):
		print "getSeriesListWithStartTime(): Y series[%s]" %str(i)
		new_yseries=[]
		#for all elements in each Y series
		for j in range(idx,ylen+(idx)):
			new_yseries.append(serieslist[i][j])
		new_serieslist.append(new_yseries)

	print "getSeriesListWithStartTime(): new re-aligned series list:"
	print new_serieslist
	return new_serieslist

	pass


def plotSeriesWithStartTime(series,starttime=''):
	if starttime:
		ns=getSeriesListWithStartTime(series,starttime)
		plotSeriesList(ns)
	else:
		plotSeriesList(series)
	pass



def compare(filekey1,fileky2,starttime):
	pass

def alignSeriesListDataPoints(seriesList):
	sorted_series=sortSarSeries(seriesList)
	return sorted_series
	pass

def mergeWithCurrentPlot(file_key,starttime):
	pl=getPlotInfo('info.db','currentplot')
	cfk=getPlotInfo('info.db','currentfilekey')
	print "mergeWithCurrentPlot(): current key=%s"% cfk
	# currkey=cfk.split('.')
	ss=getSarStatByKey(file_key)
	sl=convertSarDataMapToSeriesList(ss)
	#make sure Y-data pts matched with X(time) pts.
	asl=alignSeriesList(sl)
	aslst=getSeriesListWithStartTime(asl,starttime)
	plst=getSeriesListWithStartTime(pl,starttime)
	#aligned means Y-data points for x-series matched up.
	msl=alignedSeriesCombine(plst,aslst)
	cfk.append(file_key)
	print "mergeWithCurrentPlot(): added new file key : %s " %str(file_key)
	print cfk
	plotSeriesList(msl,cfk)
	'''
	save the current plot, file keys
	'''
	s=saveInfo(cfk,'currentfilekey')
	s2=saveInfo(msl,'currentplot')
	pass


'''
take current plot, set series list to
have x-series with time-0 at start and
continue with only SAR time data starting
from time 0 onward.
'''
def combineWithCurrentPlot(file_key,starttime):
	#get current plot info
	pl=getPlotInfo('info.db','currentplot')
	cfk=getPlotInfo('info.db','currentfilekey')
	print "combineWithCurrentPlot(): current key=%s"% cfk
	# currkey=cfk.split('.')- need to find the key
	ss=getSarStatByKey(file_key)
	#convert to series list
	sl=convertSarDataMapToSeriesList(ss)
	#make sure Y-data pts matched with X(time) pts.
	asl=alignSeriesList(sl)

	firstTimeval=pl[0][0]
	aslst=getSeriesListWithStartTime(asl,starttime)
	#create a list with startime as first element of series
	if firstTimeval==0:
		print "combineWithCurrentPlot() - The current plot is in time-zero series:"
		#exit(0)
		pass
	else:
		aslst=getSeriesListWithStartTime(asl,starttime)
		pass

	print "combineWithCurrentPlot() - adding this series:"
	print aslst

	#also create series list from current plot with starttime as first member
	plst=getSeriesListWithStartTime(pl,starttime)


	#aligned means Y-data points for x-series matched up.
	msl=alignedSeriesCombine(plst,aslst)
	print "combineWithCurrentPlot() -merged add,current plot series:"
	print msl

	#take time series and convert to time-0 onward
	timeZero_series=convertTimeSeriesToZeroStart(msl)

	print "combineWithCurrentPlot() - time zero series to plot:"
	print timeZero_series




	cfk.append(file_key)
	print "combineWithCurrentPlot(): added new file key : %s " %str(file_key)
	print cfk
	plotSeriesList(timeZero_series,cfk)
	'''
	save the current plot, file keys
	'''
	s=saveInfo(cfk,'currentfilekey')
	s2=saveInfo(timeZero_series,'currentplot')
	s3=saveInfo('dygraph-sar.html','currentfile')
	pass

def alignedSeriesCombine(series1,series2):
	combinedSeries=[]
	series1len=len(series1)
	series2len=len(series2)

	combinedSeries.append(series1[0])

	#append the series1 y-values
	for i in range(1,series1len):
		combinedSeries.append(series1[i])

	for i in range(1,series2len):
		combinedSeries.append(series2[i])

	return combinedSeries

	pass
'''

NOTES:

1) SAR format should be used to determine where time0 is.
2)use start-time to determine time0-A.
3)use start-time to determine time0-B
4)create new timeseries merged starting with (time0-A/time0-B,range)

C:\Python27\Scripts>python
Python 2.7.5 (default, May 15 2013, 22:43:36) [MSC v.1500 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import ephem
>>> import datetime
>>> datetime.datetime.now()
datetime.datetime(2014, 5, 29, 17, 40, 6, 4000)
>>> import datetime as dt

>>> n=dt.datetime.now()
>>> n
datetime.datetime(2014, 5, 29, 17, 44, 1, 248000)
>>> str(n)
'2014-05-29 17:44:01.248000'
>>> then='2014-05-27 16:00:10'

>>> dt.datetime.strptime(then,"%Y-%m-%d %H:%M:%S")
datetime.datetime(2014, 5, 27, 16, 0, 10)
>>> thendt=dt.datetime.strptime(then,"%Y-%m-%d %H:%M:%S")
>>> thendt
datetime.datetime(2014, 5, 27, 16, 0, 10)
>>> n
datetime.datetime(2014, 5, 29, 17, 44, 1, 248000)
>>> delta=thendt-n
>>> delta
datetime.timedelta(-3, 80168, 752000)
>>>
'''

