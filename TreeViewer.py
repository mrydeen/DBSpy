#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        TreeViewer.py
# Purpose:     A generic WX tree viewer with some instruction to pull in 
#              DB data.
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx

class TreeViewer(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: TreeView.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self.panel_2 = wx.Panel(self.panel_1, -1)
        self.sizer_2_staticbox = wx.StaticBox(self.panel_1, -1, "")
        self.sizer_3_staticbox = wx.StaticBox(self.panel_2, -1, "")
        self.treeWindow = wx.TreeCtrl(self.panel_1, -1, style=wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.TR_EDIT_LABELS|wx.TR_MULTIPLE|wx.TR_MULTIPLE|wx.TR_EXTENDED|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.okButton = wx.Button(self.panel_2, -1, "Ok")
        
        # Menu Bar
        #self.AkDbTreeView_menubar = wx.MenuBar()
        #self.SetMenuBar(self.AkDbTreeView_menubar)
        #self.treeMenu = wx.Menu()
        #self.expandAll = wx.MenuItem(self.treeMenu, wx.NewId(), "Expand All", "", wx.ITEM_NORMAL)
        #self.treeMenu.AppendItem(self.expandAll)
        #self.collapseAll = wx.MenuItem(self.treeMenu, wx.NewId(), "Collapse All", "Collapse All ", wx.ITEM_NORMAL)
        #self.treeMenu.AppendItem(self.collapseAll)
        #self.AkDbTreeView_menubar.Append(self.treeMenu, "Tree")
        # Menu Bar end

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TREE_KEY_DOWN, self.keyDownHandler, self.treeWindow)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.selChangingHandler, self.treeWindow)
        self.Bind(wx.EVT_TREE_SET_INFO, self.setInfoHandler, self.treeWindow)
        self.Bind(wx.EVT_TREE_END_DRAG, self.endDragHandler, self.treeWindow)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.selChangedHandler, self.treeWindow)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.itemExpandingHandler, self.treeWindow)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.itemActivedHandler, self.treeWindow)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.beginDragHandler, self.treeWindow)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.itemCollapsingHandler, self.treeWindow)
        self.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.itemGetToolTipHandler, self.treeWindow)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.itemExpandedHandler, self.treeWindow)
        self.Bind(wx.EVT_TREE_GET_INFO, self.getInfoHandler, self.treeWindow)
        self.Bind(wx.EVT_BUTTON, self.okButtonHandler, self.okButton)
        #self.Bind(wx.EVT_MENU, self.expandAllHandler, self.expandAll)
        #self.Bind(wx.EVT_MENU, self.collapseAllHandler, self.collapseAll)
        # end wxGlade
        self.setLocals()

    def __set_properties(self):
        # begin wxGlade: TreeView.__set_properties
        self.SetTitle("Tree View")
        self.SetSize((600, 600))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: TreeView.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.VERTICAL)
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.treeWindow, 1, wx.EXPAND, 0)
        sizer_4.Add((20, 20), 1, wx.ADJUST_MINSIZE, 0)
        sizer_4.Add(self.okButton, 0, wx.RIGHT|wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 5)
        sizer_3.Add(sizer_4, 1, wx.EXPAND, 0)
        self.panel_2.SetAutoLayout(True)
        self.panel_2.SetSizer(sizer_3)
        sizer_3.Fit(self.panel_2)
        sizer_3.SetSizeHints(self.panel_2)
        sizer_2.Add(self.panel_2, 0, wx.EXPAND, 0)
        self.panel_1.SetAutoLayout(True)
        self.panel_1.SetSizer(sizer_2)
        sizer_2.Fit(self.panel_1)
        sizer_2.SetSizeHints(self.panel_1)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def setLocals( self ):
        self.parent = None
        self.root = None
        self.dataBase = None
        return

    def endRDragHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `endRDragHandler' not implemented!"
        event.Skip()

    def itemGetToolTipHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `itemGetToolTipHandler' not implemented!"
        event.Skip()

    def keyDownHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `keyDownHandler' not implemented!"
        event.Skip()

    def selChangingHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `selChangingHandler' not implemented!"
        event.Skip()

    def setInfoHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `setInfoHandler' not implemented!"
        event.Skip()

    def endDragHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `endDragHandler' not implemented!"
        event.Skip()

    def beginRDragHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `beginRDragHandler' not implemented!"
        event.Skip()

    def selChangedHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `selChangedHandler' not implemented!"
        event.Skip()

    def itemExpandingHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `itemExpandingHandler' not implemented!"
        event.Skip()

    def itemActivedHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `itemActivedHandler' not implemented!"
        event.Skip()

    def beginDragHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `beginDragHandler' not implemented!"
        event.Skip()

    def itemCollapsingHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `itemCollapsingHandler' not implemented!"
        event.Skip()

    def itemcollapsedhandler(self, event): # wxglade: treeview.<event_handler>
        #print "Event handler `itemCollapsedHandler' not implemented!"
        event.Skip()

    def itemExpandedHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `itemExpandedHandler' not implemented!"
        event.Skip()

    def getInfoHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `getInfoHandler' not implemented!"
        event.Skip()

    def okButtonHandler(self, event): # wxGlade: TreeView.<event_handler>
        self.Hide()
        event.Skip()
        return

    def expandAllHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `expandAllHandler' not implemented"
        event.Skip()

    def collapseAllHandler(self, event): # wxGlade: TreeView.<event_handler>
        #print "Event handler `collapseAllHandler' not implemented"
        event.Skip()
        return

    def setTitle(self, title):
        self.SetTitle(title)
        return

    def setParent(self, parent):
        self.parent = parent
        return

    def setDataBase( self, dataBase ):
        self.dataBase = dataBase
        print(self.dataBase)
        return

    def createTree(self):
        
        if ( self.parent.sqLiteSelected == False ):
            self.setTitle("Table Descriptions - " + self.parent.ip + " : [" + self.parent.versionString + "]")
        else:
            self.setTitle("Table Descriptions - " + self.parent.sqLiteMysqlFileName + " : [" + self.parent.versionString + "]")

        # Collect the Table Information
        tableList = self.parent.executeAll( "show tables from " + self.dataBase)
        tables = []
        for table in tableList:
            tables.append( table[0] )
        
        # Create the root
        self.root = self.treeWindow.AddRoot("Tables")

        # Now walk all tables and add to root and their values
        for table in tables:
            node = self.treeWindow.AppendItem( self.root, table )
            if ( self.parent.sqLiteSelected == False ):
                tableDesc = self.parent.executeAll( "describe " + self.dataBase + "." + table )
            else:
                tableDesc = self.parent.executeAll( ".schema " + self.dataBase + "." + table )
            for tb in tableDesc:
                columnNode = self.treeWindow.AppendItem( node, tb[0] )
                typeNode = self.treeWindow.AppendItem( columnNode, "Type" )
                self.treeWindow.AppendItem( typeNode, str(tb[1]) )
                nullNode = self.treeWindow.AppendItem( columnNode, "Null" )
                self.treeWindow.AppendItem( nullNode, str(tb[2]) )
                keyNode = self.treeWindow.AppendItem( columnNode, "Key" )
                self.treeWindow.AppendItem( keyNode, str(tb[3]) )
                defNode = self.treeWindow.AppendItem( columnNode, "Default" )
                self.treeWindow.AppendItem( defNode, str(tb[4]) )
                extraNode = self.treeWindow.AppendItem( columnNode, "Extra" )
                self.treeWindow.AppendItem( extraNode, str(tb[5]) )
        
        self.treeWindow.Expand( self.root )

        return

# end of class TreeView

if __name__ == "__main__":
    temp = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    view = TreeViewer(None, -1, "")
    temp.SetTopWindow(view)
    #view.createTree( 0, 0 )
    view.Show()
    temp.MainLoop()
