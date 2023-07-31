#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        ElementGraphWindow.py
# Purpose:     This is the main WX container for the graphing component.  It
#              contains all of the graph controls that are passed into the
#              Graph.py component.
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History


import wx, sys, time, string, pydot, Graph, DataPlotter
from DisplayObject import *

################################################################################
# Class that contains the graph and controls for the graphs.
#
################################################################################
class ElementGraphWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "DB Graphing Tool", size=(673,506),
                          style=wx.DEFAULT_FRAME_STYLE | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE)

        # Graph
        self.graph = Graph.Graph( self, -1 )
        self.graph.dclickAction = Graph.DCLICK_EDIT

        # Menu Bar
        self.cavas_menubar = wx.MenuBar()
        self.SetMenuBar(self.cavas_menubar)

        # File Section
        self.File = wx.Menu()
        self.menuFind = wx.MenuItem(self.File, wx.NewId(), "Find Objects", "", wx.ITEM_NORMAL)
        self.File.Append(self.menuFind)
        self.File.AppendSeparator()
        self.menuFont = wx.MenuItem(self.File, wx.NewId(), "Select Font", "", wx.ITEM_NORMAL)
        self.File.Append(self.menuFont)
        self.menuSave = wx.MenuItem(self.File, wx.NewId(), "Save Image", "", wx.ITEM_NORMAL)
        self.File.Append(self.menuSave)
        #self.menuGraphEditor = wx.MenuItem(self.File, wx.NewId(), "Send to Graph Editor", "", wx.ITEM_NORMAL)
        #self.File.Append(self.menuGraphEditor)
        self.File.AppendSeparator()
        self.menuClose = wx.MenuItem(self.File, wx.NewId(), "Close", "", wx.ITEM_NORMAL)
        self.File.Append(self.menuClose)
        self.cavas_menubar.Append(self.File, "File")

        # View Section
        self.View = wx.Menu()
        self.View.AppendSeparator()
        self.menuShowAll = wx.MenuItem(self.View, wx.NewId(), "Show All", "", wx.ITEM_NORMAL)
        self.View.Append(self.menuShowAll)
        #self.menuShowDiskPartitions = wx.MenuItem(self.View, wx.NewId(), "Show Disk Partitions", "", wx.ITEM_NORMAL)
        #self.View.Append(self.menuShowDiskPartitions)
        #self.menuShowUnaccountedWorkloads = wx.MenuItem(self.View, wx.NewId(), "Show Internal Workloads", "", wx.ITEM_NORMAL)
        #self.View.Append(self.menuShowUnaccountedWorkloads)
        #self.menuHideLostElements = wx.MenuItem(self.View, wx.NewId(), "Hide Lost Elements", "", wx.ITEM_NORMAL)
        #self.View.Append(self.menuHideLostElements)
        self.menuHideSelected = wx.MenuItem(self.View, wx.NewId(), "Hide Selected", "", wx.ITEM_NORMAL)
        self.View.Append(self.menuHideSelected)
        self.View.AppendSeparator()
        self.menuZoomIn = wx.MenuItem(self.View, wx.NewId(), "Zoom In (4x)", "", wx.ITEM_NORMAL)
        self.View.Append(self.menuZoomIn)
        self.menuZoomOut = wx.MenuItem(self.View, wx.NewId(), "Zoom Out (4x)", "", wx.ITEM_NORMAL)
        self.View.Append(self.menuZoomOut)
        self.menuSetWidth = wx.MenuItem(self.View, wx.NewId(), "Set Width (" + str(self.graph.maxWidth) + ")", "", wx.ITEM_NORMAL)
        self.View.Append(self.menuSetWidth)
        self.menuSetHeight = wx.MenuItem(self.View, wx.NewId(), "Set Height (" + str(self.graph.maxHeight) + ")", "", wx.ITEM_NORMAL)
        self.View.Append(self.menuSetHeight)
        self.cavas_menubar.Append(self.View, "View")

        self.Help = wx.Menu()
        self.Help.AppendSeparator()
        self.menuHelpContext = wx.MenuItem(self.Help, wx.NewId(), "Help Context", "", wx.ITEM_NORMAL)
        self.Help.Append(self.menuHelpContext)
        self.cavas_menubar.Append(self.Help, "Help")

        # Menu Bar end

        self.SetTitle("DB Graphing Tool")
        self.SetSize((1000, 700))


        sizer_17 = wx.BoxSizer(wx.VERTICAL)
        sizer_17.Add(self.graph, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_17)
        self.Layout()

        self.Bind(wx.EVT_MENU, self.menuFindCallBack, self.menuFind)
        self.Bind(wx.EVT_MENU, self.menuFontCallBack, self.menuFont)
        self.Bind(wx.EVT_MENU, self.menuSaveCallBack, self.menuSave)
        self.Bind(wx.EVT_MENU, self.menuCloseCallBack, self.menuClose)
        self.Bind(wx.EVT_MENU, self.menuShowAllCallBack, self.menuShowAll)
        #self.Bind(wx.EVT_MENU, self.menuShowDiskPartitionsCallBack, self.menuShowDiskPartitions)
        #self.Bind(wx.EVT_MENU, self.menuShowUnaccountedWorkloadsCallBack, self.menuShowUnaccountedWorkloads)
        #self.Bind(wx.EVT_MENU, self.menuHideLostElementsCallBack, self.menuHideLostElements)
        self.Bind(wx.EVT_MENU, self.menuHideSelectedCallBack, self.menuHideSelected)
        self.Bind(wx.EVT_MENU, self.menuZoomInCallBack, self.menuZoomIn)
        self.Bind(wx.EVT_MENU, self.menuZoomOutCallBack, self.menuZoomOut)
        self.Bind(wx.EVT_MENU, self.menuSetWidthCallBack, self.menuSetWidth)
        self.Bind(wx.EVT_MENU, self.menuSetHeightCallBack, self.menuSetHeight)
        self.Bind(wx.EVT_MENU, self.menuHelpContextCallBack, self.menuHelpContext)
        # end wxGlade
        self.trendHour = 0

        return

    def setTitle( self, title ):
        self.SetTitle(title)
        return

    def menuSetWidthCallBack( self, event ):
        dlg = wx.TextEntryDialog( self, 
                                  "Please enter desired Width (" + str(self.graph.maxWidth) + ")",
                                  style=wx.OK|wx.CANCEL )
        retval = dlg.ShowModal()
        if ( retval == 5100 ):
            width = dlg.GetValue()
            if (width != "" ):
                self.graph.setWidth( width )
                self.menuSetWidth.SetText("Set Width (" + width + ")" )
        return

    def menuSetHeightCallBack( self, event ):
        dlg = wx.TextEntryDialog( self, 
                                  "Please enter desired Height (" + str(self.graph.maxHeight) + ")",
                                  style=wx.OK|wx.CANCEL )
        retval = dlg.ShowModal()
        if ( retval == 5100 ):
            height = dlg.GetValue()
            if (height != "" ):
                self.graph.setHeight( height )
                self.menuSetHeight.SetText("Set Height (" + height + ")")
        return

    def menuFindCallBack( self, event):
        self.graph.findObjects()
        return

    def menuHelpContextCallBack( self, event ):
        return

    def menuShowAllCallBack( self, event ):
        self.graph.showAll()
        return

    def menuShowDiskPartitionsCallBack( self, event ):
        self.graph.showDiskPartitions()
        return

    def menuShowUnaccountedWorkloadsCallBack( self, event ):
        self.graph.showUnaccountedWorkloads()
        return

    def menuHideSelectedCallBack( self, event ):
        self.graph.hideSelected()
        return

    def menuHideLostElementsCallBack( self, event ):
        self.graph.hideLostElements()
        return

    def menuZoomInCallBack( self, event ):
        self.graph.zoomIn()
        return

    def menuZoomOutCallBack( self, event ):
        self.graph.zoomOut()
        return

    def menuFontCallBack(self, event): # wxGlade: dbGrapher.<event_handler>
        dialog = wx.FontDialog( None, wx.FontData() )
        if ( dialog.ShowModal() == wx.ID_OK ):
            data = dialog.GetFontData()
            font = data.GetChosenFont()
            color = data.GetColour()
            self.graph.setFontAndColor( font, color )
        dialog.Destroy()
        return

    def menuSaveCallBack(self, event): # wxGlade: dbGrapher.<event_handler>
        # Ask the user for a filename
        filename = wx.FileSelector("Save to File")
        if ( not filename ):
            return
        try:
            self.graph.saveImage( filename )
        except:
            wx.MessageBox( "Failed to open file,  Permissions?" )
        return

    def menuCloseCallBack(self, event): # wxGlade: dbGrapher.<event_handler>
        self.Hide()
        self.graph.clearAll()
        return

    def addDisplayObject( self, type, text, id, data ):
        return self.graph.addDisplayObject( type, text, id, data )

    def connectDisplayObjects( self, objectId1, objectId2 ):
        return self.graph.connectDisplayObjects( objectId1, objectId2 )

    def scrollEvent( self, event ):
        self.refreshGraph( False )
        return

    def refreshGraph( self, draw ):
        self.graph.refreshGraph( draw )
        return

    def clearAll( self ):
        self.graph.clearAll()
        return

    def autoPlace( self ):
        self.graph.autoPlace()
        return

    def isConnected( self, objectId1, objectId2 ):
        return self.graph.isConnected( objectId1, objectId2 )

    def setParent( self, parent ):
        self.parent = parent
        self.graph.setParent( parent )
        if ( parent.version > 31 ):
            #self.menuShowDiskPartitions.Enable(  )
            nameDict[TYPE_ASG] = "Disk Group"
        self.graph.setParentWindow( self )
        return

    def exposeObject( self, objectId ):
        self.graph.exposeObject( objectId )
        return

    def saveSmallImage( self ):
        self.graph.saveSmallImage( "C:\small.bmp" )
        return

    def scrollWindow( self, position ):
        self.graph.scrollWindow( position )
        return

    def createTree(self, elementId, topType, tableName):
        self.graph.createTree( elementId, topType, tableName )
        return 
    
# end of class ElementGraphWindow


