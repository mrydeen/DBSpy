#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        TextBox.py
# Purpose:     This WX component is used to display standard text output
#
# Author:      Michael Rydeen
#
# Created:     2015/02/25
# Copyright:   (c) 2015
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx
import gettext

class TextBox(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.textBox = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_WORDWRAP)
        self.panel_2 = wx.Panel(self.panel_1, wx.ID_ANY)
        self.okButton = wx.Button(self.panel_2, wx.ID_ANY, "OK")
        self.sizer_3_staticbox = wx.StaticBox(self.panel_2, wx.ID_ANY, "")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.okButtonHandler, self.okButton)
        return

    def __set_properties(self):
        self.SetTitle("Text Output")
        self.textBox.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Courier"))
        return

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_3_staticbox.Lower()
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.HORIZONTAL)
        sizer_2.Add(self.textBox, 2, wx.ALL | wx.EXPAND, 1)
        sizer_3.Add((20, 20), 1, wx.EXPAND | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(self.okButton, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add((20, 20), 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        self.panel_2.SetSizer(sizer_3)
        sizer_2.Add(self.panel_2, 0, wx.EXPAND, 0)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        self.SetSize((700,600))
        return

    def disableOkButton(self):
        self.okButton.Disable()
        return

    def enableOkButton(self):
        self.okButton.Enable()
        return

    def okButtonHandler(self, event):
        self.Hide()
        return

    def setTitle( self, title ):
        self.SetTitle((title))
        return

    def setText(self, text):
        self.textBox.AppendText( text )
        return

    def setTextArray( self, array ):
        for s in array:
            self.setText( s )
        return

        

# end of class TextBox
if __name__ == "__main__":
    gettext.install("app") # replace with the appropriate catalog name

    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    TextBox = TextBox(None, wx.ID_ANY, "")
    app.SetTopWindow(TextBox)
    TextBox.Show()
    app.MainLoop()
