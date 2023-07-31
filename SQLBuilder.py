#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        SQLBuilder.py
# Purpose:     This WX component is used to create SQL queries on
#              the fly.  This allows you to create, save and open existing
#              programs.
#
# Author:      Michael Rydeen
#
# Created:     2019/10/23
# Copyright:   (c) 2019
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History


import wx, sys, traceback, os, time, threading
import wx.stc as stc
from StringIO import StringIO

# Variable to stop execution.
STOP = False

class Logger:
    def __init__( self, log ):
        self.out = log
        return

    def write( self, string ):
        self.out.AppendText(string)
        return

class Executor(threading.Thread):
    def __init__(self, parent, SQLCode):
        self.parent = parent
        self.SQLCode = SQLCode
        threading.Thread.__init__(self)
        return

    def run(self):
        try:
            sys.settrace(traceCalls)
	    buffer = Logger(self.parent.resultSQL)
	    sys.stdout = buffer
	    exec self.SQLCode
	    sys.stdout = sys.__stdout__
	    #if ( len(buffer.getvalue()) > 0 ):
	    #    self.resultSQL.SetValue( buffer.getvalue() )
            #else:
	    #    self.resultSQL.SetValue( "No output detected" )
            self.parent.finishedExecution()
	except Exception, exception: 
            sys.settrace(None)
	    buffer = StringIO()
	    sys.stderr = buffer
            if ( exception.message != "Stop Execution" ):
	        traceback.print_exc()
	        self.parent.resultSQL.SetValue( self.parent.resultSQL.GetValue() + "\n" + buffer.getvalue() + 
                                      "\n---------------------------------------------------------------------\n" )
            else:
	        self.parent.resultSQL.SetValue( self.parent.resultSQL.GetValue() + "\n" + buffer.getvalue() + 
                                      "\n-------------------------  STOPPED ----------------------------------\n" )
                self.parent.executeButton.Enable()
            self.parent.finishedExecution()
	    sys.stderr = sys.__stderr__
        return

#
# Need to trace the calls when the python script is running, that way
# we can interrupt the processing.
#
def traceCalls(frame, event, arg):
    global STOP
    if ( "SQLBuilder" not in frame.f_code.co_filename ): return
    if ( STOP == True ):
        raise Exception("Stop Execution")
    return

class SQLBuilder(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: SQLBuilder.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self.codeWindow = wx.SplitterWindow(self.panel_1, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.codeWindow.SetSashGravity(0.5)
        self.codeWindow.SetSashPosition(500)
        self.window_1_pane_2 = wx.Panel(self.codeWindow, -1)
        self.window_1_pane_1 = wx.Panel(self.codeWindow, -1)
        self.sizer_6_staticbox = wx.StaticBox(self.window_1_pane_2, -1, "")
        self.sizer_5_staticbox = wx.StaticBox(self.window_1_pane_2, -1, "Result")
        self.sizer_7_staticbox = wx.StaticBox(self.window_1_pane_1, -1, "SQL Window")

        # The SQL text area
        self.codeText = stc.StyledTextCtrl(self.window_1_pane_1, -1, style=wx.TE_PROCESS_ENTER)
	self.codeText.SetMarginType(1, stc.STC_MARGIN_NUMBER)
	self.codeText.SetMarginWidth(1, 30)
	font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier New')
	self.codeText.StyleSetFont(stc.STC_STYLE_DEFAULT, font)

        # This is the popup for the auto complete

        self.static_line_1 = wx.StaticLine(self.window_1_pane_1, -1)
        self.resultSQL = wx.ListCtrl(self.window_1_pane_2, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
	font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Swiss')
	self.resultSQL.SetFont(font)
	self.resultSQL.SetForegroundColour(wx.BLUE)
        self.executeButton = wx.Button(self.window_1_pane_2, -1, "Execute")
        
        # Menu Bar
        self.frame_1_menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.openMenu = wx.MenuItem(self.fileMenu, wx.NewId(), "Open", "", wx.ITEM_NORMAL)
        self.fileMenu.AppendItem(self.openMenu)
        self.saveMenu = wx.MenuItem(self.fileMenu, wx.NewId(), "Save", "", wx.ITEM_NORMAL)
        self.fileMenu.AppendItem(self.saveMenu)
        self.saveAsMenu = wx.MenuItem(self.fileMenu, wx.NewId(), "Save As...", "", wx.ITEM_NORMAL)
        self.fileMenu.AppendItem(self.saveAsMenu)
        self.exitMenu = wx.MenuItem(self.fileMenu, wx.NewId(), "Exit", "", wx.ITEM_NORMAL)
        self.fileMenu.AppendItem(self.exitMenu)
        self.frame_1_menubar.Append(self.fileMenu, "File")
        self.SetMenuBar(self.frame_1_menubar)
        # Menu Bar end

        self.__set_properties()
        self.__do_layout()
	self.init_locals()

        self.Bind(wx.EVT_BUTTON, self.executeButtonHandler, self.executeButton)
        self.Bind(wx.EVT_MENU, self.openMenuHandler, self.openMenu)
        self.Bind(wx.EVT_MENU, self.saveMenuHandler, self.saveMenu)
        self.Bind(wx.EVT_MENU, self.saveAsMenuHandler, self.saveAsMenu)
        self.Bind(wx.EVT_MENU, self.exitMenuHandler, self.exitMenu)
        self.Bind(stc.EVT_STC_CHANGE, self.codeTextChanged, self.codeText)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: SQLBuilder.__set_properties
        self.SetTitle("SQL Builder")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: SQLBuilder.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.StaticBoxSizer(self.sizer_5_staticbox, wx.VERTICAL)
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.HORIZONTAL)
        sizer_7 = wx.StaticBoxSizer(self.sizer_7_staticbox, wx.VERTICAL)
        sizer_7.Add(self.codeText, 1, wx.EXPAND, 0)
        sizer_7.Add(self.static_line_1, 0, wx.EXPAND, 0)
        self.window_1_pane_1.SetSizer(sizer_7)
        sizer_5.Add(self.resultSQL, 1, wx.EXPAND, 0)
        sizer_6.Add(self.executeButton, 0, 0, 0)
        sizer_5.Add(sizer_6, 0, wx.ALIGN_RIGHT, 0)
        self.window_1_pane_2.SetSizer(sizer_5)
        self.codeWindow.SplitHorizontally(self.window_1_pane_1, self.window_1_pane_2)
        sizer_2.Add(self.codeWindow, 1, wx.EXPAND, 0)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        self.Centre()
	self.SetSize((900, 800))
        # end wxGlade

    def init_locals(self):
        self.myparent = None
	self.filename = None
	self.dirname = "."
	self.changeMade = False
        self.executorThread = None

        self.codeText.SetText("")
        for i in range(0,20):
            self.resultSQL.InsertColumn(i, "col" + str(i), wx.LIST_FORMAT_LEFT, 230)
	return

    def setParent(self, parent):
        self.myparent = parent
        self.dbConnector = parent
        return

    ###########################################################################
    # Change handler
    ###########################################################################
    def codeTextChanged(self, event):
        self.changeMade = True;
	return

    ###########################################################################
    # Grab the code and run it.
    ###########################################################################
    def executeButtonHandler(self, event): # wxGlade: SQLBuilder.<event_handler>
        global STOP

        if ( self.executorThread == None ):
            self.resultSQL.ClearAll("")
            STOP = False 
            SQLCode = self.codeText.GetText()	
            self.executorThread = Executor(self, SQLCode)
            self.executorThread.start()
            self.executeButton.SetLabel("Stop")
        else:
            wx.MessageBox( "If your program is in a long wait, then the program will not exit until it comes out of that sleep" )
            STOP = True 
            self.executeButton.Disable()
            # Assume that it is running
            #self.executeButton.SetLabel("Execute")
            #sys.settrace(None)
            #self.executorThread = None

	return

    # Called when the execute has finished.
    def finishedExecution(self):
        global STOP
        STOP = False
        self.executeButton.SetLabel("Execute")
        self.executorThread = None

        return


    ###########################################################################
    # Open a file
    ###########################################################################
    def openMenuHandler(self, event): # wxGlade: SQLBuilder.<event_handler>
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.py", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()

            # Open the file, read the contents and set them into
            # the text edit window
            filehandle=open(os.path.join(self.dirname, self.filename),'r')
            self.codeText.SetText(filehandle.read())
            filehandle.close()

            # Report on name of latest file read
            self.SetTitle("SQL Builder - "+self.filename)
            # Later - could be enhanced to include a "changed" flag whenever
            # the text is actually changed, could also be altered on "save" ...
        dlg.Destroy()
	return

    ###########################################################################
    # Save a file
    ###########################################################################
    def saveMenuHandler(self, event): # wxGlade: SQLBuilder.<event_handler>
        # Save away the edited text
        # Open the file, do an RU sure check for an overwrite!
	if ( self.filename != None ):
            # Grab the content to be saved
            itcontains = self.codeText.GetText()
    
            # Open the file for write, write, close
            filehandle=open(os.path.join(self.dirname, self.filename),'w')
            filehandle.write(itcontains)
            filehandle.close()
	else:
            self.saveAsMenuHandler(event)
	return

    ###########################################################################
    # Prompt for a filename to save as
    ###########################################################################
    def saveAsMenuHandler(self, event): # wxGlade: SQLBuilder.<event_handler>
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.py", \
                wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            # Grab the content to be saved
            itcontains = self.codeText.GetText()

            # Open the file for write, write, close
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            filehandle=open(os.path.join(self.dirname, self.filename),'w')
            filehandle.write(itcontains)
            filehandle.close()
        # Get rid of the dialog to keep things tidy
        dlg.Destroy()
	return

    ###########################################################################
    # Exit handler
    ###########################################################################
    def exitMenuHandler(self, event): # wxGlade: SQLBuilder.<event_handler>
	if ( self.changeMade == True ):
            retval = wx.MessageBox( "Changes were made, are you sure you want to exit?", 
		                    style=wx.OK|wx.CANCEL)
	    if ( retval != 4 ):
	        return
	self.Hide()
	return


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = SQLBuilder(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
