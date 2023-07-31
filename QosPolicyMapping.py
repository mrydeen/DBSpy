#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        QosPolicyMapping.py
# Purpose:     A Class to view a qos policy mappings 
#
# Author:      Michael Rydeen
#
# Created:     2017/10/11
# Copyright:   (c) 2017
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx

# begin wxGlade: dependencies
import gettext
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class QosPolicyMapping(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: QosPolicyMapping.__init__
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.qosLabel = wx.StaticText(self.panel_1, wx.ID_ANY, "QoS Policy")
        self.qosPolicyLabel = wx.StaticText(self.panel_1, wx.ID_ANY, "Name, values")
        self.qosValuesTable = wx.ListCtrl(self.panel_1, wx.ID_ANY, style=wx.BORDER_SUNKEN | wx.LC_REPORT)
        self.closeButton = wx.Button(self.panel_1, wx.ID_ANY, "Close")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.closeButtonHandler, self.closeButton)
        self.initLocals()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: QosPolicyMapping.__set_properties
        self.SetTitle("QoS Policy Mappings")
        self.SetSize((839, 463))
        self.qosLabel.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.qosPolicyLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: QosPolicyMapping.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.qosLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer_2.Add(self.qosPolicyLabel, 0, wx.ALL | wx.EXPAND, 5)
        sizer_2.Add(self.qosValuesTable, 2, wx.EXPAND, 0)
        sizer_3.Add((20, 20), 1, wx.ALIGN_RIGHT | wx.EXPAND, 0)
        sizer_3.Add(self.closeButton, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
        sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def initLocals( self ):
        self.parent = None
        self.qosPolicy = None
        self.columns = ["objid", "Type", "Name", "Size", "Size Used", "VserverId", "Last IOps value"]
        self.volumes = []
        self.luns = []
        self.files = []

        i = 0
        for col in self.columns:
            self.qosValuesTable.InsertColumn(i, col, wx.LIST_FORMAT_LEFT, 120)
            i = i + 1

        return

    def closeButtonHandler(self, event):  # wxGlade: QosPolicyMapping.<event_handler>
        self.Hide()
        return

    def setParent( self, parent ):
        self.parent = parent
        return

    def setQosPolicy( self, qosPolicy ):
        self.qosPolicy = qosPolicy

        # Set the qos policy label
        label = "     " + str(qosPolicy[5]) + ":   Max Thput [" + str(qosPolicy[9]) + "] | Min Thput [" + str(qosPolicy[10]) + "] |"
        if ( qosPolicy[11] == 1 ):
            label = label + " shared |"
        else:
            label = label + " not shared |"
        label = label + " " + str(qosPolicy[7])

        # Now need to walk all of the objects (volume, lun and file) to see which ones are in this policy
        self.volumes = self.parent.executeAll("SELECT * FROM netapp_model.volume where qosPolicyGroupId="+str(qosPolicy[0]))
        if ( self.parent.version >= 7.3 ):
            self.luns = self.parent.executeAll("SELECT * FROM netapp_model.lun where qosPolicyGroupId="+str(qosPolicy[0]))
            try:
                self.files = self.parent.executeAll("SELECT * FROM netapp_model.file where qosPolicyGroupId="+str(qosPolicy[0]), ignoreError=True)
            except:
                pass

        count = len(self.volumes)
        row = 0
        for index in range(0, count):
            vol = self.volumes[index]
            self.qosValuesTable.InsertStringItem(row, str(vol[0]))
            self.qosValuesTable.SetStringItem(row, 1, "volume") # Type
            self.qosValuesTable.SetStringItem(row, 2, vol[4])   # Name
            self.qosValuesTable.SetStringItem(row, 3, str(self.formatInt(vol[17]))) # Size
            self.qosValuesTable.SetStringItem(row, 4, str(self.formatInt(vol[18]))) # Size used
            self.qosValuesTable.SetStringItem(row, 5, str(vol[6]))  # VserverId
            self.qosValuesTable.SetStringItem(row, 6, str(0)) # IOPs
            row = row + 1

        count = len(self.luns)
        for index in range(0, count):
            lun = self.luns[index]
            self.qosValuesTable.InsertStringItem(row, str(lun[0]))
            self.qosValuesTable.SetStringItem(row, 1, "lun")
            self.qosValuesTable.SetStringItem(row, 2, lun[9])
            self.qosValuesTable.SetStringItem(row, 3, str(self.formatInt(lun[11])))
            self.qosValuesTable.SetStringItem(row, 4, str(self.formatInt(lun[12])))
            self.qosValuesTable.SetStringItem(row, 5, str(lun[6]))
            self.qosValuesTable.SetStringItem(row, 6, str(0))
            row = row + 1

        count = len(self.files)
        for index in range(0, count):
            f = self.files[index]
            self.qosValuesTable.InsertStringItem(row, str(f[0]))
            self.qosValuesTable.SetStringItem(row, 1, "file")
            self.qosValuesTable.SetStringItem(row, 2, f[2])
            self.qosValuesTable.SetStringItem(row, 3, "unknown")
            self.qosValuesTable.SetStringItem(row, 4, "unknown")
            self.qosValuesTable.SetStringItem(row, 5, str(f[5]))
            self.qosValuesTable.SetStringItem(row, 6, str(0))
            row = row + 1

        label = label + "      vols ("+str(len(self.volumes))+") luns ("+str(len(self.luns))+") files ("+str(len(self.files))+")"
        self.qosPolicyLabel.SetLabel(label)
        if ( len(self.volumes) == 0 and len(self.luns) == 0 and len(self.files) == 0 ):
            return False
        return True

    def formatInt(self, value):
        try:
            return "{:,}".format(value)
        except:
            return "Not provided"

# end of class QosPolicyMapping

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = QosPolicyMapping(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
