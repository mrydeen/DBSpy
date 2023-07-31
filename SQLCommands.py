#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        SQLCommands.py
# Purpose:     This WX component is used to issue seperate SQL commands 
#
# Author:      Michael Rydeen
#
# Created:     2017/05/11
# Copyright:   (c) 2017
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx, os, ast

# begin wxGlade: dependencies
import gettext
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class SQLCommands(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: SQLCommands.__init__
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.panel_2 = wx.Panel(self.panel_1, wx.ID_ANY)
        self.sqlCommandTextBox = wx.ComboBox(self.panel_2, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER    )
        self.button_1 = wx.Button(self.panel_2, wx.ID_ANY, "Execute")
        self.sqlCommandOutputText = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.HSCROLL | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.sqlCommandOutputText.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier New'))
        self.sqlCommandOkButton = wx.Button(self.panel_1, wx.ID_ANY, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT_ENTER, self.sqlCommandTextEnter, self.sqlCommandTextBox)
        self.Bind(wx.EVT_BUTTON, self.sqlCommandExecuteButton, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.sqlCommandOkButtonHandler, self.sqlCommandOkButton)
        self.initLocals()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: SQLCommands.__set_properties
        self.SetTitle("SQL Commands")
        self.SetSize((1000, 500))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: SQLCommands.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(self.panel_1, wx.ID_ANY, ""), wx.HORIZONTAL)
        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self.panel_2, wx.ID_ANY, "SQL Command"), wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(self.sqlCommandTextBox, 1, wx.EXPAND, 0)
        sizer_5.Add((5, 20), 0, 0, 0)
        sizer_5.Add(self.button_1, 0, 0, 0)
        sizer_3.Add(sizer_5, 1, 0, 0)
        self.panel_2.SetSizer(sizer_3)
        sizer_2.Add(self.panel_2, 0, wx.EXPAND, 0)
        sizer_4.Add(self.sqlCommandOutputText, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)
        sizer_6.Add((20, 20), 1, wx.EXPAND, 0)
        sizer_6.Add(self.sqlCommandOkButton, 0, wx.BOTTOM | wx.RIGHT | wx.TOP, 5)
        sizer_2.Add(sizer_6, 0, wx.EXPAND, 0)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade
        return

    def initLocals(self):
        self.parent = None
        self.sqlCommandHistoryFileName = os.environ["APPDATA"] + "\\UMSQLCommandHistory.txt"
        self.sqlCommandHistory = []

        try:
            file = open(self.sqlCommandHistoryFileName, "r")
            for line in file.readlines():
                self.sqlCommandHistory.append(line)
            file.close()
        except:
            file = open(self.sqlCommandHistoryFileName, "w")
            file.close()

        self.sqlCommandTextBox.AppendItems(self.sqlCommandHistory)
        self.sqlCommandTextBox.SetFocus()
        return

    def setParent(self, parent):
        self.parent = parent
        return

    def sqlCommandTextEnter(self, event):  # wxGlade: SQLCommands.<event_handler>
        self.sqlCommandExecuteButton(None)
        return

    def reformatData(self, data):
            # Assume a tuple is being handed in, need to loop over the data and 
            # create a new output and remove the unicode
            output = []
            for d in data:
                if ( type(d) == type(str('')) ):
                    output.append( str(d) )
                else:
                    output.append(d)
            return tuple(output)


    def sqlCommandExecuteButton(self, event):  # wxGlade: SQLCommands.<event_handler>
        self.sqlCommandOutputText.SetValue("")

        # Grab the sql command, execute it and see if we need to save it off.

        cmd = self.sqlCommandTextBox.GetValue()
        if ( cmd == "" ):
            wx.MessageBox( "Please enter in a valid SQL command" )
            return

        result = None
        if ("update " in cmd or 
            "UPDATE " in cmd or
            "delete " in cmd or
            "DELETE " in cmd or
            "set " in cmd or
            "SET " in cmd):
            self.parent.executeNoResult(cmd)
        else:
            result = self.parent.executeAll(cmd)
        print(result)
        if ( result != None and "Error" not in result ):
            for item in result:
                self.sqlCommandOutputText.AppendText(str(self.reformatData(item))+"\n")
    
            if ( cmd not in self.sqlCommandHistory ):
                self.sqlCommandHistory.append(cmd)
                file = open(self.sqlCommandHistoryFileName, "a")
                file.write(cmd+"\n")
                file.close()
        return

    def sqlCommandOkButtonHandler(self, event):  # wxGlade: SQLCommands.<event_handler>
        self.Hide()
        return

# end of class SQLCommands
if __name__ == "__main__":

    main = wx.App(0)
    SQLC = SQLCommands(None, -1, "")
    main.SetTopWindow(SQLC)
    SQLC.Show()
    main.MainLoop()


