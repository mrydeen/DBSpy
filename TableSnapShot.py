#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        TableSnapShot.py
# Purpose:     A simple WX Component grid to show a snap shot of a db table
#
# Author:      Michael Rydeen
#
# Created:     2018/03/03
# Copyright:   (c) 2018
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx, wx.grid, datetime, operator

class TableSnapShot(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self.panel_5 = wx.Panel(self, -1)
        self.sizer_3_staticbox = wx.StaticBox(self.panel_1, -1, "")
        self.sizer_2_staticbox = wx.StaticBox(self, -1, "")
        self.sizer_8_staticbox = wx.StaticBox(self.panel_5, -1, "Object")
        self.sizer_8_staticbox.SetForegroundColour(wx.BLUE)
        self.elementList = wx.ListCtrl(self.panel_5, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
        self.Ok = wx.Button(self.panel_1, -1, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.okButtonCallback, self.Ok)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.colClickCallBack, self.elementList)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("Table Snap Shot")
        self.SetSize((1000, 500))
        #self.elementList.SetMinSize((772,70))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.VERTICAL)
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.VERTICAL)
        sizer_8 = wx.StaticBoxSizer(self.sizer_8_staticbox, wx.VERTICAL)
        sizer_8.Add(self.elementList, 1, wx.EXPAND, 0)
        self.panel_5.SetAutoLayout(True)
        self.panel_5.SetSizer(sizer_8)
        sizer_8.Fit(self.panel_5)
        sizer_8.SetSizeHints(self.panel_5)
        sizer_2.Add(self.panel_5, 1, wx.EXPAND, 10)
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

    def colClickCallBack(self, event):
        import UmDbSpy
        column = event.GetColumn()

        listObject = self.elementList
        # Now reset the rows.
        self.elementList.DeleteAllItems()
        # Setup the rows
        self.rows = sorted( self.rows, key=operator.itemgetter(column))
        index = 0
        ltable = self.tableName.lower()
        for value in self.rows:
            col = 1
            listObject.InsertStringItem( index, str(value[0]) )
            for item in value[1:]:
                setitem = item
                lcolumn = str(self.columns[col]).lower()
                setitem = UmDbSpy.decodeColumnValue( self, setitem, ltable, lcolumn )

                try:
                    listObject.SetStringItem( index, col, str(setitem) )
                except Exception as inst:
                    pass
                    #print("failed on " + str(setitem))
                    #print(inst)
                col = col + 1
            index = index + 1
        return

    def setParent( self, parent ):
        self.parent = parent
        return

    def setSelection( self, tableName, columns, rows ):
        import UmDbSpy
        self.tableName = tableName
        self.columns = columns
        self.rows = tuple(reversed(rows))
        print(self.tableName)
        print(self.columns)
        print(self.rows)

        self.SetTitle( "Snap shot of: " + tableName[0].upper() + tableName[1:] + " table")
        self.sizer_8_staticbox.SetLabel(tableName)
        #
        # Fill in the Element List
        #
        elementTypeIdIndex = 0
        # Fill in the columns
        for i in range(0, len(self.columns)):
            self.elementList.InsertColumn( i, self.columns[i], wx.LIST_FORMAT_LEFT, 150 )

        # Fill in the rows
        for row in self.rows:
            setitem = UmDbSpy.decodeColumnValue( self.parent, row[0], tableName.lower(), self.columns[0].lower() )
            self.elementList.InsertStringItem(0, str(setitem))
            col = 1
            for item in row[1:]:
                setitem = item
                lcolumn = str(self.columns[col]).lower()
                setitem = UmDbSpy.decodeColumnValue( self.parent, item, tableName.lower(), self.columns[col].lower() )
                self.elementList.SetStringItem(0, col, str(setitem))
                col = col + 1

        return

if __name__ == "__main__":
    temp = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    view = TableSnapShot(None, -1, "")
    temp.SetTopWindow(view)
    view.Show()
    temp.MainLoop()

