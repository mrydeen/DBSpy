#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        SoftwareLicenseAgreement.py
# Purpose:     A simple WX Component to verify license compliance.
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx, sys


class SoftwareAgreement(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: SoftwareAgreement.__init__
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.STAY_ON_TOP|wx.SYSTEM_MENU|wx.RESIZE_BORDER|wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self.bitmap_1 = wx.StaticBitmap(self.panel_1, -1, wx.Bitmap("images\\dbSpyImage.png", wx.BITMAP_TYPE_ANY))
        self.label_3 = wx.StaticText(self.panel_1, -1, "Please read the following License Agreement.  Press the PAGE DOWN key to see the rest of the agreement", style=wx.ALIGN_CENTRE)
        self.text_ctrl_1 = wx.TextCtrl(self.panel_1, -1, "<Put License Agreement Here?", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP|wx.TE_BESTWRAP)
        self.label_2 = wx.StaticText(self.panel_1, -1, "Do you accept all of the terms of the preceding License Agreement?  If you choose No, the application will close.", style=wx.ALIGN_CENTRE)
        self.button_1 = wx.Button(self.panel_1, -1, "Yes")
        self.button_2 = wx.Button(self.panel_1, -1, "No")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.yesButtonHandler, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.noButtonHandler, self.button_2)

        self.parent = None
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: SoftwareAgreement.__set_properties
        self.SetTitle("Software License Agreement")
        self.SetSize((644, 560))
        self.bitmap_1.SetMinSize((80, 62))
        self.text_ctrl_1.SetMinSize((619, 200))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: SoftwareAgreement.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(self.bitmap_1, 0, wx.LEFT|wx.RIGHT|wx.TOP, 10)
        sizer_3.Add(self.label_3, 0, wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 10)
        sizer_2.Add(sizer_3, 0, wx.EXPAND, 0)
        sizer_2.Add(self.text_ctrl_1, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        sizer_2.Add(self.label_2, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        sizer_4.Add(self.button_1, 0, wx.BOTTOM, 5)
        sizer_4.Add((10, 20), 0, 0, 0)
        sizer_4.Add(self.button_2, 0, wx.RIGHT|wx.TOP, 0)
        sizer_4.Add((10, 20), 0, 0, 0)
        sizer_2.Add(sizer_4, 0, wx.ALIGN_RIGHT, 0)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 1, 0, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def setParent(self, parent):
        self.parent = parent
        return

    def yesButtonHandler(self, event): # wxGlade: SoftwareAgreement.<event_handler>
        self.Hide()
        return

    def noButtonHandler(self, event): # wxGlade: SoftwareAgreement.<event_handler>
        print("Exiting")
        self.parent.hardExit()
        return


# end of class SoftwareAgreement


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    SoftwareAgreement = SoftwareAgreement(None, -1, "")
    app.SetTopWindow(SoftwareAgreement)
    SoftwareAgreement.Show()
    app.MainLoop()
