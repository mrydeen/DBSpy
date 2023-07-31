#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        QosView.py
# Purpose:     A Class to view a volumes CDOT qos relationships with all the
#              related components.
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx, wx.grid, datetime, DataPlotter

class QosViewer(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        #self.panel_2 = wx.Panel(self, -1)
        self.panel_3 = wx.Panel(self, -1)
        #self.panel_4 = wx.Panel(self, -1)
        self.panel_5 = wx.Panel(self, -1)
        #self.sizer_7_staticbox = wx.StaticBox(self.panel_4, -1, "Qos Workload Details")
        #self.sizer_7_staticbox.SetForegroundColour(wx.BLUE)
        self.sizer_6_staticbox = wx.StaticBox(self.panel_3, -1, "Qos Service Centers")
        self.sizer_6_staticbox.SetForegroundColour(wx.BLUE)
        #self.sizer_4_staticbox = wx.StaticBox(self.panel_2, -1, "RelationShips To This Element")
        #self.sizer_4_staticbox.SetForegroundColour(wx.BLUE)
        self.sizer_3_staticbox = wx.StaticBox(self.panel_1, -1, "")
        self.sizer_2_staticbox = wx.StaticBox(self, -1, "")
        self.sizer_8_staticbox = wx.StaticBox(self.panel_5, -1, "Qos Volume Workload")
        self.sizer_8_staticbox.SetForegroundColour(wx.BLUE)
        self.qosVolumeWorkloadList = wx.ListCtrl(self.panel_5, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
        #self.qosWorkloadDetailsList = wx.ListCtrl(self.panel_4, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
        self.qosServiceCentersList = wx.ListCtrl(self.panel_3, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
        #self.toRelationShipList = wx.ListCtrl(self.panel_2, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
        self.Ok = wx.Button(self.panel_1, -1, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.okButtonCallback, self.Ok)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.qosVolumeWorkloadRightClickCallBack, self.qosVolumeWorkloadList)
        #self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.qosWorkloadDetailsRightClickCallBack, self.qosWorkloadDetailsList)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("Volume Qos Viewer")
        self.SetSize((1000, 600))
        self.qosVolumeWorkloadList.SetMinSize((772,65))
        #self.qosWorkloadDetailsList.SetMinSize((772,100))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.VERTICAL)
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.VERTICAL)
        #sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.VERTICAL)
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.VERTICAL)
        #sizer_7 = wx.StaticBoxSizer(self.sizer_7_staticbox, wx.VERTICAL)
        sizer_8 = wx.StaticBoxSizer(self.sizer_8_staticbox, wx.VERTICAL)
        sizer_8.Add(self.qosVolumeWorkloadList, 1, wx.EXPAND, 0)
        self.panel_5.SetAutoLayout(True)
        self.panel_5.SetSizer(sizer_8)
        sizer_8.Fit(self.panel_5)
        sizer_8.SetSizeHints(self.panel_5)
        sizer_2.Add(self.panel_5, 0, wx.EXPAND, 50)
        #sizer_7.Add(self.qosWorkloadDetailsList, 1, wx.EXPAND, 0)
        #self.panel_4.SetAutoLayout(True)
        #self.panel_4.SetSizer(sizer_7)
        #sizer_7.Fit(self.panel_4)
        #sizer_7.SetSizeHints(self.panel_4)
        #sizer_2.Add(self.panel_4, 1, wx.EXPAND, 0)
        sizer_6.Add(self.qosServiceCentersList, 1, wx.EXPAND, 0)
        self.panel_3.SetAutoLayout(True)
        self.panel_3.SetSizer(sizer_6)
        sizer_6.Fit(self.panel_3)
        sizer_6.SetSizeHints(self.panel_3)
        sizer_2.Add(self.panel_3, 1, wx.EXPAND, 0)
        #sizer_4.Add(self.toRelationShipList, 1, wx.EXPAND, 0)
        #self.panel_2.SetAutoLayout(True)
        #self.panel_2.SetSizer(sizer_4)
        #sizer_4.Fit(self.panel_2)
        #sizer_4.SetSizeHints(self.panel_2)
        #sizer_2.Add(self.panel_2, 1, wx.EXPAND, 0)
        sizer_3.Add(self.Ok, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 0)
        self.panel_1.SetAutoLayout(True)
        self.panel_1.SetSizer(sizer_3)
        sizer_3.Fit(self.panel_1)
        sizer_3.SetSizeHints(self.panel_1)
        sizer_2.Add(self.panel_1, 0, wx.EXPAND, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def okButtonCallback(self, event): # wxGlade: MyFrame.<event_handler>
        event.Skip()
        self.Hide()
        return

    ###########################################################################
    # Event callback for right mouse button
    ###########################################################################
    def qosVolumeWorkloadRightClickCallBack(self, event):
        self.qosWDMenu = wx.Menu()
        id = wx.NewId() 
        self.qosWDMenu.Append( id, "View Statistics" )
        wx.EVT_MENU( self.qosWDMenu, id, self.popUpMenuQosVolumeCallBack )

        pos = event.GetPosition()
        newpos = ()
        newpos = (pos[0], pos[1]+10)
        self.PopupMenu( self.qosWDMenu, newpos )
        return


    ###########################################################################
    # Event callback for right mouse button
    ###########################################################################
    def qosWorkloadDetailsRightClickCallBack(self, event):
        self.qosWDMenu = wx.Menu()
        id = wx.NewId() 
        self.qosWDMenu.Append( id, "View Statistics" )
        wx.EVT_MENU( self.qosWDMenu, id, self.popUpMenuQosWDCallBack )

        pos = event.GetPosition()
        newpos = ()
        newpos = (pos[0], pos[1]+100)
        self.PopupMenu( self.qosWDMenu, newpos )
        return

    ###########################################################################
    # Event callback for selection of the view statistics
    ###########################################################################
    def popUpMenuQosWDCallBack( self, event ):
        selected = self.qosWorkloadDetailsList.GetFirstSelected() 
        plot = DataPlotter.DataPlotter(None, -1, "Plot Data" )
        plot.setParent(self.parent)
        plot.setObject("netapp_model.qos_workload_detail", self.workloadDetails[selected] , self.parent.reformatColumns(self.workloadDetailsColumns))
        plot.Show()        
        return

    ###########################################################################
    # Event callback for selection of the view statistics
    ###########################################################################
    def popUpMenuQosVolumeCallBack( self, event ):
        selected = self.qosVolumeWorkloadList.GetFirstSelected() 

        plot = DataPlotter.DataPlotter(None, -1, "Plot Data" )
        plot.setParent(self.parent)
        if ( self.parent.version < 7.3 ):
            plot.setObject("netapp_model.qos_volume_workload", self.values , self.parent.reformatColumns(self.columns))
        else:
            plot.setObject("netapp_model.qos_workload", self.values , self.parent.reformatColumns(self.columns))
        plot.Show()        
        return

    def setParent( self, parent ):
        self.parent = parent
        return

    def setSelection( self, objId, objName, table ):
        self.table = table
        if ( "volume" in self.table ):
            self.SetTitle("Volume Qos Viewer - " + objName)
        elif ( "lun" in self.table ):
            self.SetTitle("LUN Qos Viewer - " + objName)
        else:
            self.SetTitle("File Qos Viewer - " + objName)

        # Given the object, get the qos workload
        if ( self.parent.version < 7.3 ):
            self.columns = self.parent.executeAll( "show columns from netapp_model.qos_volume_workload")
        else:
            self.columns = self.parent.executeAll( "show columns from netapp_model.qos_workload")
        try:
            if ( self.parent.version < 7.3 ):
                self.values = self.parent.executeAll( "select * from netapp_model.qos_volume_workload where volumeId="+str(objId) )[0]
            else:
                self.values = self.parent.executeAll( "select * from netapp_model.qos_workload where holderId="+str(objId) )[0]
        except:
            wx.MessageBox( "Object ("+objName+") does not have any Qos Workloads associated" )
            return False

        #
        # Fill in the qos workload List
        #
        # Fill in the columns
        for i in range(0, len(self.columns)):
            self.qosVolumeWorkloadList.InsertColumn( i, str(self.columns[i][0]), wx.LIST_FORMAT_LEFT, 150 )

        # Fill in the rows
        self.qosVolumeWorkloadList.InsertStringItem(0, str(self.values[0]))
        for i in range(0, len(self.values[1:])):
            item = str(self.values[i+1])
            if ( "time" in self.columns[i+1][0].lower() ):
                item = item + " (" + datetime.datetime.fromtimestamp(self.values[i+1]/1000).strftime('%m-%d-%Y %H:%M:%S') + ")"
            self.qosVolumeWorkloadList.SetStringItem(0, i+1, item)

        #
        # Get the column
        cmd = "show columns from netapp_model.qos_service_center"
        columns = self.parent.executeAll(cmd)
        for i in range(0, len(columns)):
            self.qosServiceCentersList.InsertColumn( i, str(columns[i][0]), wx.LIST_FORMAT_LEFT, 200 )

        # We need to get the service centers.  Todo this, we need to look up in the 
        # qos_workload_node_relationship table and get the node ids.  And once we have that,
        # we can look at the service centers.
        cmd = "SELECT nodeId from netapp_model.qos_workload_node_relationship where workloadId="+str(self.values[0])+" and objState='LIVE'"
        self.nodeIds = self.parent.executeAll(cmd)
        nodeIdList = []
        for node in self.nodeIds:
            nodeIdList.append(node[0]) 
            
        cmd = "SELECT * FROM netapp_model.qos_service_center where nodeId in "+str(tuple(nodeIdList))+" and objState='LIVE'"
        self.serviceCenters = self.parent.executeAll(cmd)

        # The list contains all the aggregates across this cluster so we only want to filter down to the
        # aggregate that we are attached to.
        volumeValues = self.parent.executeAll("select * from netapp_model.volume where objid="+str(objId))[0]
        volumeColumns = self.parent.executeAll("show columns from netapp_model.volume")
        aggregateIdIndex = self.parent.findColumnIndex("aggregateId", self.parent.reformatColumns(volumeColumns))
        aggregateId = volumeValues[aggregateIdIndex]
        # If this is a valid value, then we are good to go, otherwise this might be a flexgroup so have to grab the list of 
        # aggregates.
        aggregateNames = []
        if ( aggregateId != None ):
            aggregate = self.parent.executeAll("select * from netapp_model.aggregate where objId="+str(aggregateId))[0]
            aggregateNames.append(aggregate[4])
        else:
            # Need to find all of the constituents
            constituents = self.parent.executeAll("select objid from netapp_model.volume_flexgroup_constituent_relationship where flexgroupId="+str(objId))
            for c in constituents:
                volumeValues = self.parent.executeAll("select * from netapp_model.volume where objId="+str(c))[0]
                aggregateId = volumeValues[aggregateIdIndex]
                aggregate = self.parent.executeAll("select * from netapp_model.aggregate where objId="+str(aggregateId))[0]
                aggregateNames.append(aggregate[4])

        # Fill in the rows
        index = 0
        for sc in self.serviceCenters:
            col = 1
            # If this service center name has DISK, then make sure that this
            # workload is actually mapped to it.
            if ( "DISK" in sc[4] ):
                found = False
                for a in aggregateNames:
                    scAggrName = sc[4][9:-37]
                    if ( a == scAggrName or "OTHER" in sc[4] ): 
                        found = True
                        break
                if ( found == False ): continue
                    
            self.qosServiceCentersList.InsertStringItem(index, str(sc[0]))
            for item in sc[1:]:
                if ( "time" in columns[col][0].lower() ):
                    item = str(item) + " (" + datetime.datetime.fromtimestamp(item/1000).strftime('%m-%d-%Y %H:%M:%S') + ")"
                self.qosServiceCentersList.SetStringItem(index, col, str(item))
                col = col + 1
            index = index + 1

        return True

if __name__ == "__main__":
    temp = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    view = QosViewer(None, -1, "")
    temp.SetTopWindow(view)
    view.Show()
    temp.MainLoop()

