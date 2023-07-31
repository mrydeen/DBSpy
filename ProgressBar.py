#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        ProgressBar.py
# Purpose:     Simple WX component to show a progress bar with status messages
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx

class ProgressBar(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: ProgressBar.__init__
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.STAY_ON_TOP|wx.SYSTEM_MENU|wx.RESIZE_BORDER|wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self.sizer_3_staticbox = wx.StaticBox(self.panel_1, -1, "")
        self.sizer_4_staticbox = wx.StaticBox(self.panel_1, -1, "")
        self.progressStatusLabel = wx.StaticText(self.panel_1, -1, "In Progress", style=wx.ALIGN_CENTRE)
        self.zeroLabel = wx.StaticText(self.panel_1, -1, "0 %", style=wx.ALIGN_CENTRE)
        self.gauge = wx.Gauge(self.panel_1, -1, 100)
        self.oneHundredLabel = wx.StaticText(self.panel_1, -1, "100%")
        self.okButton = wx.Button(self.panel_1, -1, "OK")
        self.cancelButton = wx.Button(self.panel_1, -1, "Cancel")

        self.__set_properties()
        self.__do_layout()
        self.SetSize((400, 160))
        self.cancelPressed = False
        self.cancelCallBackFunc = None
        self.okButton.Disable()

        self.Bind(wx.EVT_BUTTON, self.okButtonHandler, self.okButton)
        self.Bind(wx.EVT_BUTTON, self.cancelButtonHandler, self.cancelButton)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: ProgressBar.__set_properties
        self.SetTitle("Progress")
        self.progressStatusLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "MS Shell Dlg 2"))
        self.zeroLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "MS Shell Dlg 2"))
        self.oneHundredLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "MS Shell Dlg 2"))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ProgressBar.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.HORIZONTAL)
        self.sizer_3.Add(self.progressStatusLabel, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_4.Add(self.zeroLabel, 0, wx.LEFT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_4.Add((10, 20), 0, 0, 0)
        sizer_4.Add(self.gauge, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_4.Add((10, 20), 0, 0, 0)
        sizer_4.Add(self.oneHundredLabel, 0, wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.sizer_3.Add(sizer_4, 1, wx.EXPAND, 0)
        sizer_5.Add((20, 20), 1, 0, 0)
        sizer_5.Add(self.okButton, 0, wx.LEFT|wx.TOP, 10)
        sizer_5.Add(self.cancelButton, 0, wx.LEFT|wx.TOP, 10)
        self.sizer_3.Add(sizer_5, 1, wx.EXPAND, 0)
        self.panel_1.SetSizer(self.sizer_3)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def setCancelCallBack( self, cancelCallBackFunc ):
        self.cancelCallBackFunc = cancelCallBackFunc
        return

    def setProgressText(self, text ):
        self.progressStatusLabel.SetLabel(text)
        self.sizer_3.Layout()
        return

    def setProgressGauge( self, pos ):
        self.gauge.SetValue(pos)
        if ( pos == 100 ):
            self.okButton.Enable()
        return

    def okButtonHandler(self, event): # wxGlade: ProgressBar.<event_handler>
        self.Destroy()
        return

    def cancelButtonHandler(self, event): # wxGlade: ProgressBar.<event_handler>
        if ( self.cancelCallBackFunc != None ):
            self.cancelCallBackFunc()
        self.Destroy()
        return

# end of class ProgressBar


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = ProgressBar(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
