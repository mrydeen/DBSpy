#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        EventOccurrenceView.py
# Purpose:     A WX component that will visually show an event occurrence and
#              all of its components.
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History


import wx, wx.grid, datetime, operator, QosView, ElementGraphWindow, DataPlotter
from Constants import *

class EventOccurrenceView(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        #self.panel_2 = wx.Panel(self, -1)
        self.panel_3 = wx.Panel(self, -1)
        self.panel_4 = wx.Panel(self, -1)
        self.panel_5 = wx.Panel(self, -1)
        self.sizer_7_staticbox = wx.StaticBox(self.panel_4, -1, "Event Participants")
        self.sizer_7_staticbox.SetForegroundColour(wx.BLUE)
        self.sizer_6_staticbox = wx.StaticBox(self.panel_3, -1, "Related Event Occurrences")
        self.sizer_6_staticbox.SetForegroundColour(wx.BLUE)
        self.sizer_3_staticbox = wx.StaticBox(self.panel_1, -1, "")
        self.sizer_2_staticbox = wx.StaticBox(self, -1, "")
        self.sizer_8_staticbox = wx.StaticBox(self.panel_5, -1, "Event Occurrence Detail")
        self.sizer_8_staticbox.SetForegroundColour(wx.BLUE)
        self.eventOccurrenceList = wx.ListCtrl(self.panel_5, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
        self.eventParticipantsList = wx.ListCtrl(self.panel_4, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
        self.relatedEventOccurrencesList = wx.ListCtrl(self.panel_3, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
        #self.toRelationShipList = wx.ListCtrl(self.panel_2, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
        self.Ok = wx.Button(self.panel_1, -1, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.okButtonCallback, self.Ok)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.eventParticipantColClick, self.eventParticipantsList)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.relatedEventsColClick, self.relatedEventOccurrencesList)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.relatedEventParticipantsRightClickCallBack, self.eventParticipantsList)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.relatedEventOccurrencesRightClickCallBack, self.relatedEventOccurrencesList)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("Event Occurrence Details - ")
        self.SetSize((1000, 600))
        self.eventOccurrenceList.SetMinSize((772,65))
        self.eventParticipantsList.SetMinSize((772,100))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.VERTICAL)
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.VERTICAL)
        #sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.VERTICAL)
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.VERTICAL)
        sizer_7 = wx.StaticBoxSizer(self.sizer_7_staticbox, wx.VERTICAL)
        sizer_8 = wx.StaticBoxSizer(self.sizer_8_staticbox, wx.VERTICAL)
        sizer_8.Add(self.eventOccurrenceList, 1, wx.EXPAND, 0)
        self.panel_5.SetAutoLayout(True)
        self.panel_5.SetSizer(sizer_8)
        sizer_8.Fit(self.panel_5)
        sizer_8.SetSizeHints(self.panel_5)
        sizer_2.Add(self.panel_5, 0, wx.EXPAND, 50)
        sizer_7.Add(self.eventParticipantsList, 1, wx.EXPAND, 0)
        self.panel_4.SetAutoLayout(True)
        self.panel_4.SetSizer(sizer_7)
        sizer_7.Fit(self.panel_4)
        sizer_7.SetSizeHints(self.panel_4)
        sizer_2.Add(self.panel_4, 1, wx.EXPAND, 0)
        sizer_6.Add(self.relatedEventOccurrencesList, 1, wx.EXPAND, 0)
        self.panel_3.SetAutoLayout(True)
        self.panel_3.SetSizer(sizer_6)
        sizer_6.Fit(self.panel_3)
        sizer_6.SetSizeHints(self.panel_3)
        sizer_2.Add(self.panel_3, 1, wx.EXPAND, 0)
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

    def relatedEventsColClick( self, event ):
        column = event.GetColumn()
        self.relatedEventOccurrencesList.DeleteAllItems()
        self.relatedEvents = sorted( self.relatedEvents, key=operator.itemgetter(column) )
        # Fill in the rows
        index = 0
        for re in self.relatedEvents:
            col = 1
            self.relatedEventOccurrencesList.InsertStringItem(index, str(re[0]))
            for item in re[1:]:
                try:
                    item = self.decodeColumnValue( item, "opm.continuous_event_occurrence", self.columns[col][0].lower() )
                except:
                    item = self.decodeColumnValue( item, "opm.event_occurrence", self.columns[col][0].lower() )
                self.relatedEventOccurrencesList.SetStringItem(index, col, str(item) )
                col = col + 1
            index = index + 1
        return

    def eventParticipantColClick(self, event ):
        column = event.GetColumn()
        self.eventParticipantsList.DeleteAllItems()
        self.eventParticipants = sorted( self.eventParticipants, key=operator.itemgetter(column) )
        # Fill in the rows
        index = 0
        for ep in self.eventParticipants:
            col = 1
            self.eventParticipantsList.InsertStringItem(index, str(ep[0]))
            for item in ep[1:]:
                try:
                    item = self.decodeColumnValue( item, "opm.continuous_event_participant", (self.eventParticipantColumns[col][0]).lower() )
                except:
                    item = self.decodeColumnValue( item, "opm.event_participant", (self.eventParticipantColumns[col][0]).lower() )
                self.eventParticipantsList.SetStringItem(index, col, str(item))
                col = col + 1
            index = index + 1
        
        return

    def okButtonCallback(self, event): # wxGlade: MyFrame.<event_handler>
        event.Skip()
        self.Hide()
        return

    ###########################################################################
    # Event callback for right mouse button on the event participants
    ###########################################################################
    def relatedEventParticipantsRightClickCallBack(self, event):
        selected = self.eventParticipantsList.GetFirstSelected() 
        #print self.eventParticipants[selected]
        selection = self.eventParticipants[selected]

        self.participantMenu = wx.Menu()

        id = wx.NewId()
        self.participantMenu.Append( id, "View Statistics" )
        wx.EVT_MENU( self.participantMenu, id, self.showStatisticsCallBack )

        version = eval(self.parent.opm_version.split(".")[0])
        if ( selection[3] == ELEMENT_VOLUME and version != True ): 
            id = wx.NewId()
            self.participantMenu.Append( id, "View Qos Detail" )
            wx.EVT_MENU( self.participantMenu, id, self.showVisitQosDetailCallBack )

            # Add the qos visit Topology
            id = wx.NewId()
            self.participantMenu.Append( id, "View Qos Visit Topology" )
            wx.EVT_MENU( self.participantMenu, id, self.showQosVisitTopologyCallBack )

        pos = event.GetPosition()
        newpos = ()
        newpos = (pos[0]+5, pos[1]+90)
        self.PopupMenu( self.participantMenu, newpos )
        return


    ###########################################################################
    # View the statistics for a particular particpnt.
    ###########################################################################
    def showStatisticsCallBack( self, event ):
        selected = self.eventParticipantsList.GetFirstSelected() 
        selection = self.eventParticipants[selected]

        participantId = selection[2]
        participantType = selection[3]

        # The participant type is an OPM element type.  Need to convert to 
        # a resource type.
        resourceType = ELEMENT_TO_RESOURCE_MAP[participantType]
        tableName = getDBTableNameFromResource( resourceType )

        columns = self.parent.executeAll( "show columns from " + tableName )
        values = self.parent.executeAll( "select * from " + tableName + " where objid = " + str(participantId) )[0]
        columns = self.parent.reformatColumns( columns )

        plot = DataPlotter.DataPlotter(None, -1, "Plot Data")
        plot.setParent( self.parent )
        plot.setObject( tableName, values, columns )
        plot.Show()
        return

    ###########################################################################
    # Event callback for selection of the view statistics
    ###########################################################################
    def showVisitQosDetailCallBack( self, event ):
        selected = self.eventParticipantsList.GetFirstSelected() 
        selection = self.eventParticipants[selected]

        volume = self.parent.executeAll( "select * from netapp_model.volume where objid=" + str(selection[2]))[0]
        print(volume)

        ev = QosView.QosViewer(self, -1, "")
        ev.setParent(self.parent)
        if ( ev.setSelection( selection[2], volume[4] ) ):
            ev.Show()
        return

    ###########################################################################
    # Event callback for selection of the view statistics
    ###########################################################################
    def showQosVisitTopologyCallBack( self, event ):
        selected = self.eventParticipantsList.GetFirstSelected() 
        selection = self.eventParticipants[selected]

        volume = self.parent.executeAll( "select * from netapp_model.volume where objid=" + str(selection[2]))[0]

        tv = ElementGraphWindow.ElementGraphWindow(None)
        tv.setParent(self.parent)
        tv.setTitle( "Topology QoS Visit Graph For Volume: " + volume[4] )
        tv.createTree( selection[2], "VISIT", "volume" )
        tv.Show()

        return


    ###########################################################################
    # Event callback for right mouse button
    ###########################################################################
    def relatedEventOccurrencesRightClickCallBack(self, event):
        self.relatedEventMenu = wx.Menu()
        id = wx.NewId() 
        self.relatedEventMenu.Append( id, "Open Event" )
        wx.EVT_MENU( self.relatedEventMenu, id, self.popUpMenuEventOccurrenceCallBack )

        pos = event.GetPosition()
        newpos = ()
        newpos = (pos[0], pos[1]+330)
        self.PopupMenu( self.relatedEventMenu, newpos )
        return


    ###########################################################################
    # Event callback for selection of the view statistics
    ###########################################################################
    def popUpMenuEventOccurrenceCallBack( self, event ):
        selected = self.relatedEventOccurrencesList.GetFirstSelected() 
        print(self.relatedEvents[selected])

        ev = EventOccurrenceView(None, -1, "")
        ev.setParent(self.parent)
        ev.setSelection( self.relatedEvents[selected][0] )
        ev.Show()        
        return

    def setParent( self, parent ):
        self.parent = parent
        return

    def setSelection( self, eventOccurrenceId ):

        self.SetTitle("Event Occurrence Details - " + str(eventOccurrenceId))

        # Given the eventOccurrenceId, get all of the information
        try: 
            self.columns = self.parent.executeAll( "show columns from opm.continuous_event_occurrence")
            self.values = self.parent.executeAll( "select * from opm.continuous_event_occurrence where id="+str(eventOccurrenceId) )[0]
        except:
            self.columns = self.parent.executeAll( "show columns from opm.event_occurrence")
            self.values = self.parent.executeAll( "select * from opm.event_occurrence where id="+str(eventOccurrenceId) )[0]

        #
        # Fill in the event occurrence first
        #
        # Fill in the columns
        for i in range(0, len(self.columns)):
            self.eventOccurrenceList.InsertColumn( i, str(self.columns[i][0]), wx.LIST_FORMAT_LEFT, 150 )

        # Fill in the rows
        self.eventOccurrenceList.InsertStringItem(0, str(self.values[0]))
        for i in range(0, len(self.values[1:])):
            item = self.values[i+1]
            try: 
                item = self.decodeColumnValue( item, "opm.continuous_event_occurrence", self.columns[i+1][0].lower() )
            except:
                item = self.decodeColumnValue( item, "opm.event_occurrence", self.columns[i+1][0].lower() )
            self.eventOccurrenceList.SetStringItem(0, i+1, str(item))

        #
        # Now collect the participant list
        #
        # Get the columns
        try:
            cmd = "show columns from opm.continuous_event_participant"
            self.eventParticipantColumns = self.parent.executeAll(cmd)
        except:
            cmd = "show columns from opm.event_participant"
            self.eventParticipantColumns = self.parent.executeAll(cmd)
        for i in range(0, len(self.eventParticipantColumns)):
            self.eventParticipantsList.InsertColumn( i, str(self.eventParticipantColumns[i][0]), wx.LIST_FORMAT_LEFT, 150 )

        try:
            cmd = "select * from opm.continuous_event_participant where occurrenceId=" + str(eventOccurrenceId)
            self.eventParticipants = self.parent.executeAll(cmd)
        except:
            cmd = "select * from opm.event_participant where occurrenceId=" + str(eventOccurrenceId)
            self.eventParticipants = self.parent.executeAll(cmd)
        self.sizer_7_staticbox.SetLabel("Event Participants (" + str(len(self.eventParticipants)) + ")")

        # Fill in the rows
        index = 0
        for ep in self.eventParticipants:
            col = 1
            self.eventParticipantsList.InsertStringItem(index, str(ep[0]))
            for item in ep[1:]:
                try:
                    item = self.decodeColumnValue( item, "opm.continuous_event_participant", (self.eventParticipantColumns[col][0]).lower() )
                except:
                    item = self.decodeColumnValue( item, "opm.event_participant", (self.eventParticipantColumns[col][0]).lower() )
                self.eventParticipantsList.SetStringItem(index, col, str(item))
                col = col + 1
            index = index + 1
        
        #
        # Now Fill in the related event occurrences 
        #
        # Get the columns
        for i in range(0, len(self.columns)):
            self.relatedEventOccurrencesList.InsertColumn( i, str(self.columns[i][0]), wx.LIST_FORMAT_LEFT, 200 )

        
        # Now get all of the related event occurrences based on the targetId
        try:
            cmd = "select * from opm.continuous_event_occurrence where targetId = " + str(self.values[3]) + " and id != " + str(self.values[0]) + " and targetId != -1"
            self.relatedEvents = self.parent.executeAll(cmd)
        except:
            cmd = "select * from opm.event_occurrence where targetId = " + str(self.values[3]) + " and id != " + str(self.values[0])
            self.relatedEvents = self.parent.executeAll(cmd)
        self.sizer_6_staticbox.SetLabel("Related Event Occurrences (" + str(len(self.relatedEvents)) + ")")

        # Fill in the rows
        index = 0
        for re in self.relatedEvents:
            col = 1
            self.relatedEventOccurrencesList.InsertStringItem(index, str(re[0]))
            for item in re[1:]:
                try:
                    item = self.decodeColumnValue( item, "opm.continuous_event_occurrence", self.columns[col][0].lower() )
                except:
                    item = self.decodeColumnValue( item, "opm.event_occurrence", self.columns[col][0].lower() )
                self.relatedEventOccurrencesList.SetStringItem(index, col, str(item) )
                col = col + 1
            index = index + 1

        return True

    def decodeColumnValue( self, item, ltable, lcolumn ):
        import UmDbSpy
        return UmDbSpy.decodeColumnValue( self.parent, item, ltable, lcolumn )

if __name__ == "__main__":
    temp = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    view = QosViewer(None, -1, "")
    temp.SetTopWindow(view)
    view.Show()
    temp.MainLoop()

