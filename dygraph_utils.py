import json
import csv
import numpy
import matplotlib.pyplot as plt
import re
import os
import webbrowser
from debug import *
#from plotutil import *
from datautils import *



'''
data map is an x-y struct where
the x coord is a key and the y coord
is a key. dataMapToDygraph converts to
series of x,y pairs which dygraphs can
render.
'''
def dataMapToDygraph(filename,xlabel,ylabel,datamap,chartTitle):
	length=len(datamap)
	stroke='strokeWidth: 1'
	f = open (filename,"wb")
	f.write("<html>\n<head>\n<script type=\"text/javascript\"src=\"dygraph-combined.js\"></script>\n")
	f.write("</head>\n<body>\n<div id=\"graphdiv\"></div><script type=\"text/javascript\">")
	f.write("  g = new Dygraph(\n\n	// containing div\n	  document.getElementById(\"graphdiv\"),")
	f.write('\" '+xlabel+','+ylabel+'\\n\"+')
	count=0
	'''
	we need to transform from '-' seperated to '/'
	seperated for date and from '-' to ':' seperation
	for time.
	'''
	for key in datamap:
		datekey,timekey=key.split(':')
		#xtime=re.sub('-',':',timekey)
		ftime=sarConvertTimeHyphenToColon(timekey)
		fdate=sarConvertDateHyphenToSlash(datekey)
		fdatetime=fdate + ' '+ ftime
		#hr,min,sec=xtime.split(':')
		if count==length-1:
			f.write('\" '+fdatetime+','+datamap[key]+'\\n\"')
		else:

			f.write('\" '+fdatetime+','+datamap[key]+'\\n\"+')
		count+=1
	f.write(',\n{' + chartTitle + ' , ' + stroke + '}\n')
	f.write(");")
	f.write("</script></body></html>	")
	f.close()

'''
take a dygraph and
render using web browser
'''
def  renderDyGraphWebPage(dygraph,new=''):
	cwd=os.getcwd()
	url='%s/%s' % (cwd,dygraph)
	if new:
		s=webbrowser.open(url)
		print "Rendering new web URL: %s " %dygraph
	else:
		print "Rendering as file: %s" % dygraph

def createDygraph(xlabel,ylabel,datamap,chartTitle):
	dygraphfile="dygraph-sar.html"
	title=' title:\' %s\''%chartTitle
	dataMapToDygraph(dygraphfile,xlabel,ylabel,datamap,title)
	renderDyGraphWebPage(dygraphfile)

'''
NOTE: works ONLY for SAR data where time series is year-month-day:hr-min-sec

from a series data array (array of array of series data)
plot a dygraph rendering using this series.
Series Data is an array of arrays.
array[0] is the time or X axis series
array[1..n] are the Y1-Yn Y axis series.
You need build a data formatter func to
convert data into this format.
'''
def createDygraphSeriesPlot(filename,seriesData,plotTitle,xlabel,ylabel):
	width=len(seriesData)
	length=len(seriesData[0])
	stroke='strokeWidth: 1'
	f = open (filename,"wb")
	f.write("<html>\n<head>\n<script type=\"text/javascript\"src=\"dygraph-combined.js\"></script>\n")
	f.write("<style>#graphdiv {\n  position: absolute; left: 20px; right: 120px; top: 80px; bottom: 40px;}</style>\n")
	f.write("</head>\n<body>\n<div id=\"graphdiv\"></div><script type=\"text/javascript\">")
	f.write("  g = new Dygraph(\n\n	// containing div\n	  document.getElementById(\"graphdiv\"),")

	''' create the dygraph data labels'''
	seriesLabel='X:,'
	for w in range(0,width-1):
		ynum='Y'+str(w)+','
		seriesLabel+=ynum

	f.write('\" '+seriesLabel+',\\n\"+')


	title='title: \'%s\'' % plotTitle
	dprint (3,'length=%s, width=%s' %(length,width))
	YLabel='ylabel: \'%s\'' % ylabel
	XLabel='xlabel: \'%s\'' % xlabel


	for i in range(0,length):
		dygraph_data=' '
		count=0
		''' build the dygraph x,y data items using length of time series (x axis)'''
		for j in range(0,width):
			if j==0:
				kdate,ktime=seriesData[j][i].split(':')
				ftime=sarConvertTimeHyphenToColon(ktime)
				fdate=sarConvertDateHyphenToSlash(kdate)
				fdatetime=fdate+' '+ftime

				dygraph_data= dygraph_data+ str(fdatetime)+ ' ,'
			else:
				'''not time series but y data'''
				data=seriesData[j][i]
				dygraph_data= dygraph_data+str(data)+ ' '
				if j!=width-1:
					dygraph_data= dygraph_data+','
		if j!=width-1:
			dygraph_data= dygraph_data+','
		dprint(3, 'iteration %s: %s\n' %(i,dygraph_data))
		if i==length-1:
			f.write('\" '+dygraph_data+'\\n\"')
		else:
			f.write('\" '+dygraph_data+',\\n\"+')
	count+=1

	f.write(',\n{' + title + ' , '+YLabel+','+XLabel+','+ stroke + '}\n')
	f.write(");")
	f.write("</script></body></html>	")
	f.close()


	pass


def sarConvertTimeHyphenToColon(time):
	xtime=re.sub('-',':',time)
	return xtime
	pass

def sarConvertDateHyphenToSlash(date):
	xdate=re.sub('-','/',date)
	return xdate
	pass

def dataSeriesToDygraph(filename,xlabel,ylabel,dataseries,chartTitle):
	length=len(dataseries)
	stroke='strokeWidth: 1'
	seriestype=type(dataseries)
	f = open (filename,"wb")
	f.write("<html>\n<head>\n<script type=\"text/javascript\"src=\"dygraph-combined.js\"></script>\n")
	f.write("</head>\n<body>\n<div id=\"graphdiv\"></div><script type=\"text/javascript\">")
	f.write("  g = new Dygraph(\n\n	// containing div\n	  document.getElementById(\"graphdiv\"),")
	f.write('\" '+xlabel+','+ylabel+'\\n\"+')
	count=0

	for key in dataseries:
		fdatetime=key

		#hr,min,sec=xtime.split(':')
		if count==length-1:
			f.write('\" '+str(fdatetime)+','+str(dataseries[key])+'\\n\"')
		else:

			f.write('\" '+str(fdatetime)+','+str(dataseries[key])+'\\n\"+')
		count+=1
	f.write(',\n{' + chartTitle + ' , ' + stroke + '}\n')
	f.write(");")
	f.write("</script></body></html>	")
	f.close()

'''
Useful for non-SAR related (just integers) data series
A series list is an array of array; array[0]=time series, array[1...n]=Y series
'''
def seriesListToDygraph(filename,xlabel,ylabel,dataseries,chartTitle,Ylabels):
	width=len(dataseries)
	length=len(dataseries[0])
	stroke='strokeWidth: 1'
	seriestype=type(dataseries)

	yTitle='ylabel:\'' + ylabel + '\''

	f = open (filename,"wb")
	f.write("<html>\n<head>\n<script type=\"text/javascript\"src=\"dygraph-combined.js\"></script>\n")
	f.write("<style>#graphdiv {\n  position: absolute; left: 120px; right: 120px; top: 80px; bottom: 40px;}</style>\n")
	f.write("</head>\n<body>\n<div id=\"graphdiv\"></div><script type=\"text/javascript\">")
	f.write("  g = new Dygraph(\n\n	// containing div\n	  document.getElementById(\"graphdiv\"),")
	#f.write('\" '+xlabel+','+ylabel+'\\n\"+')

	seriesLabel='X:,'
	for item in Ylabels:
		print "adding Y label: %s " % item
		ynum=str(item)+ ','
		seriesLabel+=ynum


	# ''' create the dygraph data labels'''
	# seriesLabel='X:,'
	# for w in range(0,width-1):
	# 	ynum='Y'+str(w)+','
	# 	seriesLabel+=ynum
	 #    print seriesLabel

	f.write('\" '+seriesLabel+'\\n\"+')
	count=0


	for i in range(0,length):
		dygraph_data=' '
		count=0
		''' build the dygraph x,y data items using length of time series (x axis)'''
		for j in range(0,width):
			if j==0:
				dygraph_data= dygraph_data+ str(dataseries[j][i])+ ','
			else:
				'''not time series but y data'''
				data=dataseries[j][i]
				dygraph_data= dygraph_data+str(data)+ ' '
				if j!=width-1:
					dygraph_data= dygraph_data+','
		if j!=width-1:
			dygraph_data= dygraph_data+','
		dprint (3,'iteration %s: %s\n' %(i,dygraph_data))
		if i==length-1:
			f.write('\" '+dygraph_data+'\\n\"')
		else:
			f.write('\" '+dygraph_data+'\\n\"+')
	count+=1

	f.write(',\n{title:\'' + chartTitle + '\'' + ',' + stroke + ','+ yTitle + '}\n')
	f.write(");")
	f.write("</script></body></html>	")
	f.close()


