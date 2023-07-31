#!/usr/bin/env python
# -*- coding: CP1252 -*-
#
# generated by wxGlade 0.7.2 on Tue Nov 21 07:29:50 2017
#

import wx

# begin wxGlade: dependencies
import gettext
# end wxGlade

# begin wxGlade: extracode
# end wxGlade
import wx.lib.mixins.listctrl  as  listmix
 
########################################################################
class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    ''' TextEditMixin allows any column to be edited. '''
 
    #----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)

class ViewAndEditFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: ViewAndEditFrame.__init__
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.objectLabel = wx.StaticText(self.panel_1, wx.ID_ANY, "Object 1")
        self.dataList = EditableListCtrl(self.panel_1, wx.ID_ANY, style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.okSaveButton = wx.Button(self.panel_1, wx.ID_ANY, "Save")
        self.cancelButton = wx.Button(self.panel_1, wx.ID_ANY, "Cancel")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.dataListEditBeginHandler, self.dataList)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.dataListEditEndHandler, self.dataList)
        self.Bind(wx.EVT_BUTTON, self.okSaveButtonHandler, self.okSaveButton)
        self.Bind(wx.EVT_BUTTON, self.cancelButtonHandler, self.cancelButton)
        self.initLocals()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: ViewAndEditFrame.__set_properties
        self.SetTitle("View & Edit")
        self.SetSize((700, 800))
        self.objectLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ViewAndEditFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.objectLabel, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer_2.Add(self.dataList, 1, wx.ALL | wx.EXPAND, 5)

        sizer_3.Add((20, 20), 1, wx.BOTTOM | wx.EXPAND, 5)
        sizer_3.Add(self.okSaveButton, 0, wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, 5)
        sizer_3.Add(self.cancelButton, 0, wx.ALIGN_RIGHT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)

        sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def initLocals( self ):
        self.values = []
        self.labels = []
        self.selection = 0
        self.parent = ""
        self.cancelOk = False
        self.index = 0
        self.allowSave = False
        return

    def setParent( self, parent ):
        self.parent = parent
        return

    def SetStringItem( self, item, value, bgcolor="white", fgcolor="black" ):
        self.dataList.InsertItem( self.index, item )
        self.dataList.SetItem( self.index, 1, str(value) )
        self.dataList.SetItemBackgroundColour( self.index, bgcolor)
        self.dataList.SetItemTextColour( self.index, fgcolor)
        self.index=self.index+1
        return

    def setValues( self, title, labels, values, selection, allowSave ):
        self.index = 0
        self.allowSave = allowSave
        if ( self.allowSave ):
            self.SetTitle("View & Edit")
        else:
            self.SetTitle("View")
        self.objectLabel.SetLabel(title)
        self.okSaveButton.Disable()
        self.labels = labels
        self.values = values
        self.selection = selection
        self.dataList.ClearAll()

        self.dataList.InsertColumn(0, "Column", wx.LIST_FORMAT_LEFT, 200)
        self.dataList.InsertColumn(1, "Value", wx.LIST_FORMAT_LEFT, 500)

        for i in range(0, len(self.labels)):
            self.SetStringItem( self.labels[i], str(self.values[i]) )

        self.Show()
        return

    def dataListEditBeginHandler(self, event):  # wxGlade: ViewAndEditFrame.<event_handler>
        if ( event.GetColumn() != 1 ):
            event.Veto()
            return

        if ( self.allowSave ):
            self.okSaveButton.Enable()
        return

    def dataListEditEndHandler(self, event):  # wxGlade: ViewAndEditFrame.<event_handler>
        self.dataList.Select(event.Item.Id) # force the list to select the event item
        row_id = event.GetIndex() #Get the current row
        col_id = event.GetColumn () #Get the current column
        if col_id < 0: # ---- Changed ------
            col_id = 0 # ---- Changed ------
        new_data = event.GetText() #Get the changed data

        # Only allow the second colume to be editable
        if ( col_id != 1 ):
            return

        # If the value has changed, mark in red
        if ( str(new_data) != str(self.values[row_id]) ):
            self.dataList.SetItemBackgroundColour( row_id, "red" )
        else:
            self.dataList.SetItemBackgroundColour( row_id, "white" )
        return

    def okSaveButtonHandler(self, event):  # wxGlade: ViewAndEditFrame.<event_handler>
        # Get all of the items in the row
        values = []
        for i in range( len(self.labels) ):
            values.append( self.dataList.GetItemText( i, 1 ) )
        self.parent.commitChanges( self.selection, values, self.values )
        self.Hide()
        return

    def cancelButtonHandler(self, event):  # wxGlade: ViewAndEditFrame.<event_handler>
        self.Hide()
        return

# end of class ViewAndEditFram

if __name__ == "__main__":

    main = wx.App(0)
    SQLC = ViewAndEditFrame(None, -1, "")
    main.SetTopWindow(SQLC)
    SQLC.Show()
    main.MainLoop()

