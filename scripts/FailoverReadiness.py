###############################################################################
# This script is a sample script showing access to the database and
# producing a graph with matplotlib.
###############################################################################

import numpy
import mysql.connector, wx, os, time, datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

#
# Server Parameters
#
# TODO: Fill in server/user/password information
#
SERVER = "" 
USER = "" 
PASSWORD = "" 

###############################################################################
# Connect to the server
###############################################################################
dbConn = mysql.connector.connect( host=SERVER,
                                  user=USER, 
                                  passwd=PASSWORD, 
                                  db="" )
dbWorker = dbConn.cursor()

###############################################################################
# Grab the data I need
###############################################################################
dbWorker.execute("select * from netapp_model.node")
nodes = dbWorker.fetchall()
currentTime = time.time() * 1000
threeDaysBack = currentTime - (3 * 24 * 60 * 60 * 1000)
nodeMap = {}
for node in nodes:
    # Grab the statistics for the nodes.
    cmd = "select cpuBusy, time from netapp_performance.sample_node where objid=" + str(node[0]) + " and time >= " + str(threeDaysBack)
    dbWorker.execute(cmd)
    stats = dbWorker.fetchall()
    # Now average all of the stats.
    avg = 0.0
    nodeMap[node[4]] = [avg, stats]

###############################################################################
# 72 hour stack chart
###############################################################################
nodeList = nodeMap.keys()
y = []
x = []
for node in nodeList:
    stats = nodeMap[node][1]
    s = []
    t = []
    for stat in stats:
        s.append(stat[0])
        t.append(long(stat[1]/1000))
    y.append(s)
    x = t
# this call to 'cumsum' (cumulative sum), passing in your y data, 
# is necessary to avoid having to manually order the datasets
y_stack = numpy.cumsum(y, axis=0)

plt.title('Failover Readiness for 72 hours')
plt.ylabel('CPU %')
plt.xlabel('Date')
fig = plt.figure(1)
ax1 = fig.add_subplot(111)
ax1.fill_between(x, 0, y_stack[0,:], facecolor="#CC6666", alpha=.7)
ax1.fill_between(x, y_stack[0,:], y_stack[1,:], facecolor="#1DACD6", alpha=.7)

N = len(x)
# Format the x axis date
def format_date(dx, pos=None):
    import numpy, datetime
    global N, x
    thisind = numpy.clip(int(dx+0.5), 0, N-1)
    return datetime.datetime.fromtimestamp(x[thisind]).strftime('%Y-%m-%d %H:%M:%S')
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
fig.autofmt_xdate()

# Draw the 100% line 
line = plt.axhline(y=100.0, xmin=0, xmax=x[-1], linewidth=2, color="r")
line.set_dashes([8,4,2,4,2,4])

p1 = plt.Rectangle((0, 0), 1, 1, facecolor="#CC6666")
p2 = plt.Rectangle((0, 0), 1, 1, facecolor="#1DACD6")
plt.legend([p1, p2], nodeList)


###############################################################################
# Simple wx python class to display the saved picture.
###############################################################################
class PhotoCtrl(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.frame = wx.Frame(None, title='Image Viewer')
 
        self.panel = wx.Panel(self.frame)
        self.PhotoMaxSize = 900
        self.createWidgets()
        self.frame.Show()
 
    def createWidgets(self):
        img = wx.EmptyImage(1000,800)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, 
                                         wx.BitmapFromImage(img))
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.EXPAND, 5)
        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self.frame)
        self.panel.Layout()
 
    def SetImage(self, filepath):
        img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = self.PhotoMaxSize
            NewH = self.PhotoMaxSize * H / W
        else:
            NewH = self.PhotoMaxSize
            NewW = self.PhotoMaxSize * W / H
        img = img.Scale(NewW,NewH)
 
        self.imageCtrl.SetBitmap(wx.BitmapFromImage(img))
        self.panel.Refresh()
 
###############################################################################
# Main starting point 
###############################################################################
if __name__ == '__main__':
    # This is being run as a script by itself so show the matplot UI
    plt.show()
else:
    # This is being launched in the WX context so show an image 
    plt.savefig('nodeperf.png', bbox_inches='tight')
    app = PhotoCtrl()
    app.SetImage('./nodeperf.png')
    app.MainLoop()


