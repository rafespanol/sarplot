import os
from time import *

from sarplot import *


import fileinput


setdebug(0)
getdebug()


#>>> closePlot()
#>>> checkPlot()
#('None', [], [])
#loadJson('network.json')
#>>> plot('network_json.rxpck')
#addPlot('network_json.txkB','2014/06/03 23:01:12')
#addPlot('network_json.rxkB','2014/06/03 23:01:12',1)

#raw_input('Demonstrating checkPlot() call; press enter to continue:')
#checkPlot()

#raw_input('Demonstrating closePlot() call; press enter to continue:')
#closePlot()

#raw_input('Demonstrating checkPlot() call again...; press enter to continue:')
#checkPlot()


#exit(0)




raw_input('Demonstrating LoadJson() call; press enter to continue:')
loadJson('network.json')


raw_input('Demonstrating plot(\'network_json.rxpck\') call; press enter to continue:')
plot('network_json.rxpck')

raw_input('Demonstrating addPlot(\'network_json.txkB\',\'2014/06/03 23:01:12\') call;press enter to continue:')
addPlot('network_json.txkB','2014/06/03 23:01:12')

raw_input('Demonstrating addPlot(\'network_json.rxkB\',\'2014/06/03 23:01:12\',1) call; press enter to continue:')
addPlot('network_json.rxkB','2014/06/03 23:01:12',1)

raw_input('Demonstrating addPlot(\'network_json.txpck\',\'2014/06/03 23:01:12\',1) call; press enter to continue:')
addPlot('network_json.txpck','2014/06/03 23:01:12',1)

#raw_input('Demonstrating plotSarMovingAvg(\'io3_json.wtps\',2) call; press enter to continue:')
#plotSarMovingAvg('io3_json.wtps',2)


#raw_input('Demonstrating savePlot(\'newplot\') call; press enter to continue:')
#savePlot('newplot')

#raw_input('Demonstrating getPlotInfo(\'newplot.db\',\'currentplot\') call; press enter to continue:')
#plot=getPlotInfo('newplot.db','currentplot')
#print "Printing plot data contents:" 
#print plot

#raw_input('Demonstrating seriesListToDygraph(\'newplot.html\',\'sar time stamp\',\'wtps\\,rtps\',plot,\'New SAR wtps plot\') call; press enter to continue:')
#seriesListToDygraph('newplot.html','sar time stamp','wtps\,rtps',plot,'New SAR wtps plot')

#raw_input('Demonstrating renderDyGraphWebPage(\'newplot.html\') call; press enter to continue:')
#renderDyGraphWebPage('newplot.html')

#raw_input('Demonstrating closePlot(\'mysavedplot.html\') call; press enter to continue:')
#closePlot('mysavedplot.html')
