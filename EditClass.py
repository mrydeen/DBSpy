#-----------------------------------------------------------------------------
# Name:        EditClass.py
# Purpose:     This is a simple class that allows the DB Spy to edit a 
#              particular DB row entry.
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx
import wx.grid

###############################################################################
# Class used to edit the parameters in the MSQL database
###############################################################################
class editClass(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: editClass.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_2 = wx.Panel(self, -1)
        self.sizer_15_staticbox = wx.StaticBox(self.panel_2, -1, "Edit DB Parameters")
        self.sizer_16_staticbox = wx.StaticBox(self.panel_2, 1, "")
        self.editGrid = wx.grid.Grid(self.panel_2, -1, size=(1, 1))
        self.editOkButton = wx.Button(self.panel_2, -1, "Ok")
        self.editCancelButton = wx.Button(self.panel_2, -1, "Cancel")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.editOkButtonCallBack, self.editOkButton)
        self.Bind(wx.EVT_BUTTON, self.editCancelButtonCallBack, self.editCancelButton)
        # end wxGlade
	self.initLocals()

    def __set_properties(self):
        # begin wxGlade: editClass.__set_properties
        self.SetTitle("Edit DB Parameters")
        self.editGrid.CreateGrid(1, 60)
        self.editGrid.SetColLabelSize(30)
        self.editGrid.SetMinSize((800, 70))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: editClass.__do_layout
        sizer_14 = wx.BoxSizer(wx.VERTICAL)
        sizer_15 = wx.StaticBoxSizer(self.sizer_15_staticbox, wx.VERTICAL)
        sizer_16 = wx.StaticBoxSizer(self.sizer_16_staticbox, wx.HORIZONTAL)
        sizer_15.Add(self.editGrid, 1, wx.EXPAND, 0)
        sizer_16.Add(self.editOkButton, 0, wx.LEFT|wx.TOP|wx.ADJUST_MINSIZE, 2)
        sizer_16.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizer_16.Add(self.editCancelButton, 0, wx.RIGHT|wx.TOP|wx.ADJUST_MINSIZE, 2)
        sizer_15.Add(sizer_16, 0, wx.ALIGN_RIGHT, 0)
        self.panel_2.SetAutoLayout(True)
        self.panel_2.SetSizer(sizer_15)
        sizer_15.Fit(self.panel_2)
        sizer_15.SetSizeHints(self.panel_2)
        sizer_14.Add(self.panel_2, 1, wx.EXPAND, 2)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_14)
        sizer_14.Fit(self)
        sizer_14.SetSizeHints(self)
        self.Layout()
        # end wxGlade

    def initLocals( self ):
        self.row = []
	self.columns = []
	self.selection = 0
	self.parent = ""
	self.cancelOk = False
	return

    def editOkButtonCallBack(self, event): # wxGlade: editClass.<event_handler>
        if ( self.cancelOk == False ): 
	    # Get all of the items in the row
	    row = []
	    for i in range( len(self.columns) ):
                row.append( self.editGrid.GetCellValue( 0, i ) )
	    self.parent.commitChanges( self.selection, row, self.row )
        self.Hide()
	return

    def editCancelButtonCallBack(self, event): # wxGlade: editClass.<event_handler>
        self.Hide()
	return

# end of class editClass
