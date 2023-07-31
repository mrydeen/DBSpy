#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        VolumeViewer.py
# Purpose:     A more complex WX component that will create a grid of volumes
#              information including sparkline charts
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx, wx.grid, sparkplot, os, time, threading, DataPlotter, QosView
import ElementGraphWindow

# begin wxGlade: extracode
# end wxGlade

class VolumeLoader(threading.Thread):
    def __init__(self, parent):
        self.parent = parent
        threading.Thread.__init__(self)
        self.stop = False
        return

    def run(self):

        current = long(time.time() * 1000)
        daysPast = current - ((3 * 24 * 60 * 60 * 1000))
        row = 0
        for volume in self.parent.volumes:
            if ( self.stop ): break
            # Does this volume have a workload?
            cmd = "select objid from netapp_model.qos_volume_workload where volumeId="+str(volume[0])
            if ( self.parent.parent.version >= 7.3 ):
                cmd = "select objid from netapp_model.qos_workload where holderId="+str(volume[0])
            result = self.parent.parent.executeAll( cmd )
            workloadId = 0
            if ( len(result) != 0 ):
                workloadId = result[0][0]
            hasWorkload = True 
            if ( workloadId == 0 ):
                hasWorkload = False 

            cmd = "select avgLatency, totalOps, writeOps, readOps from netapp_performance.sample_volume_"+str(volume[3])+" where objid="+str(volume[0])+ " and time > "+str(daysPast)
            if ( self.parent.parent.version >= 7.3 ):
                cmd = "select latency, ops, writeOps, readOps from netapp_performance.sample_qos_volume_workload_"+str(volume[2])+" where objid="+str(workloadId)+ " and time > "+str(daysPast)
            try:
                stats = self.parent.parent.executeAll( cmd )
            except:
                wx.MessageBox("Failed to find statistics for volume: " + volume[1])
                continue

            iopsSpark, writeIopsSpark, readIopsSpark, latencySpark = self.createSparks( volume, stats )
            self.parent.grid.SetCellValue(row, 0, self.parent.nameMap[volume[2]])   
            self.parent.grid.SetCellValue(row, 1, self.parent.nameMap[volume[3]])    
            if ( volume[4] != None ):
                self.parent.grid.SetCellValue(row, 2, self.parent.nameMap[volume[4]])    
            else:
                self.parent.grid.SetCellValue(row, 2, "None")    
            self.parent.grid.SetCellValue(row, 3, str(volume[1]))    
            self.parent.grid.SetCellValue(row, 4, str(hasWorkload))    

            img = ImageRenderer(iopsSpark)
            self.parent.grid.SetCellRenderer(row, 5, img)    
            self.parent.grid.SetColSize(5, img.img.GetWidth()+2)
            self.parent.grid.SetRowSize(row, img.img.GetHeight()+2)

            img = ImageRenderer(writeIopsSpark)
            self.parent.grid.SetCellRenderer(row, 6, img)    
            self.parent.grid.SetColSize(6, img.img.GetWidth()+2)
            self.parent.grid.SetRowSize(row, img.img.GetHeight()+2)

            img = ImageRenderer(readIopsSpark)
            self.parent.grid.SetCellRenderer(row, 7, img)    
            self.parent.grid.SetColSize(7, img.img.GetWidth()+2)
            self.parent.grid.SetRowSize(row, img.img.GetHeight()+2)

            img = ImageRenderer(latencySpark)
            self.parent.grid.SetCellRenderer(row, 8, img)    
            self.parent.grid.SetColSize(8, img.img.GetWidth()+2)
            self.parent.grid.SetRowSize(row, img.img.GetHeight()+2)
            row = row + 1
            self.parent.countUpLabel.SetLabel(str(row))
            pos = (row * 100)/len(self.parent.volumes)
            self.parent.gauge_1.SetValue(pos)
        return

    def createSparks(self, volume, stats):
        simplifiedLatency = ""
        simplifiedOps = ""
        simplifiedWriteOps = ""
        simplifiedReadOps = ""
        for stat in stats:
            s = ""
            if ( stat[0] != None ):
                s = "%.2f" % stat[0]
            else:
                s = "%.2f" % 0.0
            if ( simplifiedLatency == "" ):
                simplifiedLatency = s
            else:
                simplifiedLatency = simplifiedLatency + "," + s
  
            s = ""
            if ( stat[1] != None ):
                s = "%.2f" % stat[1]
            else:
                s = "%.2f" % 0.0
            if ( simplifiedOps == "" ):
                simplifiedOps = s
            else:
                simplifiedOps = simplifiedOps + "," + s
 
            s = ""
            if ( stat[2] != None ):
                s = "%.2f" % stat[2]
            else:
                s = "%.2f" % 0.0
            if ( simplifiedWriteOps == "" ):
                simplifiedWriteOps = s
            else:
                simplifiedWriteOps = simplifiedWriteOps + "," + s
 
            s = ""
            if ( stat[3] != None ):
                s = "%.2f" % stat[3]
            else:
                s = "%.2f" % 0.0
            if ( simplifiedReadOps == "" ):
                simplifiedReadOps = s
            else:
                simplifiedReadOps = simplifiedReadOps + "," + s
 
        try:
            os.remove("spark"+str(volume[0])+"Lat.png")
            os.remove("spark"+str(volume[0])+"Iops.png")
            os.remove("spark"+str(volume[0])+"WriteIops.png")
            os.remove("spark"+str(volume[0])+"WriteReadIops.png")
        except:
            pass
      
        sp = None
        sp = sparkplot.Sparkplot( input_data=simplifiedLatency,
                                     label_first_value=True,
                                     label_last_value=True,
                                     plot_max=True,
                                     label_max=True,
                                     output_file="spark"+str(volume[0])+"Lat.png")
        sp.plot_sparkline()
  
        sp = sparkplot.Sparkplot( input_data=simplifiedOps,
                                     label_first_value=True,
                                     label_last_value=True,
                                     plot_max=True,
                                     label_max=True,
                                     output_file="spark"+str(volume[0])+"Iops.png")
        sp.plot_sparkline()
 
        sp = sparkplot.Sparkplot( input_data=simplifiedWriteOps,
                                     label_first_value=True,
                                     label_last_value=True,
                                     plot_max=True,
                                     label_max=True,
                                     output_file="spark"+str(volume[0])+"WriteIops.png")
        sp.plot_sparkline()

        sp = sparkplot.Sparkplot( input_data=simplifiedReadOps,
                                     label_first_value=True,
                                     label_last_value=True,
                                     plot_max=True,
                                     label_max=True,
                                     output_file="spark"+str(volume[0])+"ReadIops.png")
        sp.plot_sparkline()
 
        sparkLatImage = wx.Bitmap("spark"+str(volume[0])+"Lat.png", wx.BITMAP_TYPE_ANY)
        sparkIopsImage = wx.Bitmap("spark"+str(volume[0])+"Iops.png", wx.BITMAP_TYPE_ANY)
        sparkWriteIopsImage = wx.Bitmap("spark"+str(volume[0])+"WriteIops.png", wx.BITMAP_TYPE_ANY)
        sparkReadIopsImage = wx.Bitmap("spark"+str(volume[0])+"ReadIops.png", wx.BITMAP_TYPE_ANY)

        os.remove("spark"+str(volume[0])+"Lat.png")
        os.remove("spark"+str(volume[0])+"Iops.png")
        os.remove("spark"+str(volume[0])+"WriteIops.png")
        os.remove("spark"+str(volume[0])+"ReadIops.png")

        return (sparkIopsImage, sparkWriteIopsImage, sparkReadIopsImage, sparkLatImage)


class VolumeViewer(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: VolumeViewer.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self.panel_2 = wx.Panel(self.panel_1, -1)
        self.panel_5 = wx.Panel(self.panel_1, -1)
        self.sizer_5_staticbox = wx.StaticBox(self.panel_1, -1, "")
        self.progressSizer_staticbox = wx.StaticBox(self.panel_5, -1, "Progress")
        self.countUpLabel = wx.StaticText(self.panel_5, -1, "0")
        self.label_1 = wx.StaticText(self.panel_5, -1, "of")
        self.totalCountLabel = wx.StaticText(self.panel_5, -1, "0")
        self.label_2 = wx.StaticText(self.panel_5, -1, "0 %")
        self.gauge_1 = wx.Gauge(self.panel_5, -1, 100 )
        self.label_3 = wx.StaticText(self.panel_5, -1, "100 %")
        self.grid = wx.grid.Grid(self.panel_1, -1, size=(1, 1))
        self.panel_3 = wx.Panel(self.panel_2, -1)
        self.cancelButton = wx.Button(self.panel_2, -1, "Cancel")
        self.panel_4 = wx.Panel(self.panel_2, -1)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.cancelButtonHandler, self.cancelButton)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.rightClickHandler, self.grid)
        self.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.rightClickHandler, self.grid)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: VolumeViewer.__set_properties
        self.SetTitle("Volume Viewer - Last 72 hours worth of data")
        self.gauge_1.SetMinSize((200, -1))
        self.grid.CreateGrid(2000, 9)
        self.grid.EnableEditing(1)
        self.grid.SetColLabelValue(0, "Cluster")
        self.grid.SetColLabelValue(1, "VServer")
        self.grid.SetColLabelValue(2, "Aggregate")
        self.grid.SetColLabelValue(3, "Volume")
        self.grid.SetColLabelValue(4, "Workload?")
        self.grid.SetColLabelValue(5, "Total Ops")
        self.grid.SetColLabelValue(6, "Write Ops")
        self.grid.SetColLabelValue(7, "Read Ops")
        self.grid.SetColLabelValue(8, "Average Latency")
        self.grid.SetMinSize((1005, 475))
        # end wxGlade
        self.initLocals()

    def __do_layout(self):
        # begin wxGlade: VolumeViewer.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.StaticBoxSizer(self.sizer_5_staticbox, wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        progressSizer = wx.StaticBoxSizer(self.progressSizer_staticbox, wx.HORIZONTAL)
        progressSizer.Add((20, 20), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        progressSizer.Add(self.countUpLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 40)
        progressSizer.Add(self.label_1, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
        progressSizer.Add(self.totalCountLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 40)
        progressSizer.Add(self.label_2, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        progressSizer.Add(self.gauge_1, 0, 0, 0)
        progressSizer.Add(self.label_3, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        progressSizer.Add((20, 20), 0, 0, 0)
        sizer_4.Add(progressSizer, 0, wx.LEFT|wx.EXPAND, 5)     
        self.panel_5.SetSizer(sizer_4)
        sizer_2.Add(self.panel_5, 0, 0, 0)
        sizer_5.Add(self.grid, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_5, 1, wx.EXPAND, 0)
        sizer_3.Add(self.panel_3, 0, 0, 0)
        sizer_3.Add(self.cancelButton, 0, wx.TOP|wx.BOTTOM, 5)
        sizer_3.Add(self.panel_4, 0, 0, 0)
        self.panel_2.SetSizer(sizer_3)
        sizer_2.Add(self.panel_2, 0, 0, 0)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def initLocals(self):
        self.parent = None
        self.volumes = None
        return

    def popUpMenuCallBack(self, event):
        menu = self.menuDict[event.GetId()]
        selected = self.grid.GetSelectedRows()[0]
        volume = self.volumes[selected]

        if ( menu == "View Statistics" ):
            self.viewStatisticsCB( volume )
        elif ( menu == "View Qos Detail" ):
            self.viewVolumesQosDetail( volume )
        elif ( menu == "View Qos Visit Topology" ):
            self.viewVolumesVisitTopology( volume )
        return

    def rightClickHandler(self, event):

        selected = self.grid.GetSelectedRows()
        if ( len(selected) == 0 ):
            wx.MessageBox("You must select a row before using the right mouse button")
            return

        menu = wx.Menu()
        id = wx.NewId() 
        self.menuDict = {}
        menu.Append( id, "View Statistics" )
        self.menuDict[id] = "View Statistics"
        wx.EVT_MENU( menu, id, self.popUpMenuCallBack )

        version = eval(self.parent.opm_version.split(".")[0])
        #if ( version != 2 ):
        if ( False ):
            id = wx.NewId() 
            menu.Append( id, "View Qos Detail" )
            self.menuDict[id] = "View Qos Detail"
            wx.EVT_MENU( menu, id, self.popUpMenuCallBack )
                
            # Add the qos visit Topology
            id = wx.NewId() 
            menu.Append( id, "View Qos Visit Topology" )
            self.menuDict[id] = "View Qos Visit Topology"
            wx.EVT_MENU( menu, id, self.popUpMenuCallBack )
        
        pos =  event.GetPosition()
        newpos = (pos[0], pos[1])
        self.PopupMenu( menu, newpos )

        return

    ###########################################################################
    # Callback to graph the visit tree 
    ###########################################################################
    def viewVolumesVisitTopology(self, volume ):

        tv = ElementGraphWindow.ElementGraphWindow(None)
        tv.setParent(self.parent)
        tv.setTitle( "Topology QoS Visit Graph For Volume: " + volume[1] )
        tv.createTree( volume[0], "VISIT", "volume" )
        tv.Show()
        return

    ###########################################################################
    # Callback to view the volumes qos details
    ###########################################################################
    def viewVolumesQosDetail(self, volume):
        # Need to find the index for the column so we can pull the id.
        idToQuery = volume[0]
        name = volume[1]

        ev = QosView.QosViewer(self, -1, "")
        ev.setParent(self.parent)
        if ( ev.setSelection( idToQuery, name ) ):
            ev.Show()
        return

    def viewStatisticsCB(self, volume):

        plot = DataPlotter.DataPlotter(None, -1, "Plot Data" )
        plot.setParent(self.parent)

        columns = self.parent.executeAll("show columns from netapp_model.volume")
        columns = self.parent.reformatColumns(columns)
        selection = self.parent.executeAll("select * from netapp_model.volume where objid="+str(volume[0]))[0]
        
        plot.setObject("netapp_model.volume", selection, columns)
        plot.Show()
        return


    def cancelButtonHandler(self, event): # wxGlade: VolumeViewer.<event_handler>
        self.volumeLoader.stop = True
        time.sleep(1)
        self.Destroy()
        return

    def setParent( self, parent ):
        self.parent = parent
        return

    def initData(self):
        # Query for all of the volumes.
        self.volumes = self.parent.executeAll("select objid, name, clusterId, vserverId, aggregateId from netapp_model.volume")
        self.totalCountLabel.SetLabel(str(len(self.volumes)))

        # Need to sort the volumes by cluster and vserver and aggregate.  We also want to get the names
        # for the cluster, vserver and aggregate
        cMap = {}
        self.nameMap = {}
        for volume in self.volumes:
            # Cluster name?
            if ( not self.nameMap.has_key(volume[2]) ):
                clusterName = self.parent.executeAll("select name from netapp_model.cluster where objid="+str(volume[2]))[0][0]
                self.nameMap[volume[2]] = clusterName
            # Vserver name?
            if ( not self.nameMap.has_key(volume[3]) ):
                vserverName = self.parent.executeAll("select name from netapp_model.vserver where objid="+str(volume[3]))[0][0]
                self.nameMap[volume[3]] = vserverName
            # Aggregate name?
            if ( not self.nameMap.has_key(volume[4]) and volume[4] != None ):
                aggrName = self.parent.executeAll("select name from netapp_model.aggregate where objid="+str(volume[4]))[0][0]
                self.nameMap[volume[4]] = aggrName

            # In cMap?
            if ( not cMap.has_key(volume[2]) ):
                aMap = {}
                aMap[volume[4]] = [volume]
                cMap[volume[2]] = aMap
            else:
                aMap = cMap[volume[2]]
                if ( not aMap.has_key(volume[4]) ):
                    aMap[volume[4]] = [volume]
                else:
                    aMap[volume[4]].append(volume)
                    
        # Now create a new ordered list.
        vols = []
        for ckey in cMap.keys():
            for akey in cMap[ckey]:
                vols = vols + cMap[ckey][akey]
            
        self.volumes = vols

        self.volumeLoader = VolumeLoader( self )
        self.volumeLoader.start()
        return

# end of class VolumeViewer

class ImageRenderer(wx.grid.PyGridCellRenderer):
    def __init__(self, img):
        wx.grid.PyGridCellRenderer.__init__(self)
        self.img = img
    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        image = wx.MemoryDC()
        image.SelectObject(self.img)
        dc.SetBackgroundMode(wx.SOLID)
        if isSelected:
            dc.SetBrush(wx.Brush(wx.BLUE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.BLUE, 1, wx.SOLID))
        else:
            dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.WHITE, 1, wx.SOLID))
        dc.DrawRectangleRect(rect)
        width, height = self.img.GetWidth(), self.img.GetHeight()
        if width > rect.width-2:
            width = rect.width-2
        if height > rect.height-2:
            height = rect.height-2
        dc.Blit(rect.x+1, rect.y+1, width, height, image, 0, 0, wx.COPY, True)
        return


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    VolumeViewer = VolumeViewer(None, -1, "")
    app.SetTopWindow(VolumeViewer)
    VolumeViewer.Show()
    app.MainLoop()
