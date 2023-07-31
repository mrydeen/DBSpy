#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        LogViewer.py
# Purpose:     A WX component to grab the essential OPM log files and will
#              parse them and colorize them.  
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx, threading, pysftp, time
import wx.stc as stc
import wx.richtext as richtext

# begin wxGlade: extracode
# end wxGlade

class LogStyled(stc.StyledTextCtrl):
    """
    Subclass the StyledTextCtrl to provide  additions
    and initializations to make it useful as a log window.

    """
    def __init__(self, parent, style=wx.SIMPLE_BORDER):
        """
        Constructor
        
        """
        stc.StyledTextCtrl.__init__(self, parent, style=style)
        self._styles = [None]*32
        self._free = 1
        
    def getStyle(self, c='black'):
        """
        Returns a style for a given colour if one exists.  If no style
        exists for the colour, make a new style.
        
        If we run out of styles, (only 32 allowed here) we go to the top
        of the list and reuse previous styles.

        """
        free = self._free
        if c and isinstance(c, (str, unicode)):
            c = c.lower()
        else:
            c = 'black'
        
        try:
            style = self._styles.index(c)
            return style
            
        except ValueError:
            style = free
            self._styles[style] = c
            self.StyleSetForeground(style, wx.NamedColour(c))

            free += 1
            if free >31:
                free = 0
            self._free = free
            return style

    def write(self, text, c=None):
        """
        Add the text to the end of the control using colour c which
        should be suitable for feeding directly to wx.NamedColour.
        
        'text' should be a unicode string or contain only ascii data.
        """
        style = self.getStyle(c)
        lenText = len(text.encode('utf8'))
        end = self.GetLength()
        self.AddText(text)
        self.StartStyling(end, 31)
        self.SetStyling(lenText, style)
        self.EnsureCaretVisible()

class LogRich(richtext.RichTextCtrl):
    """
    Subclass the StyledTextCtrl to provide  additions
    and initializations to make it useful as a log window.

    """
    def __init__(self, parent, style=wx.SIMPLE_BORDER):
        """
        Constructor
        
        """
        richtext.RichTextCtrl.__init__(self, parent, style=style)
        self._styles = [None]*32
        self._free = 1

    def write(self, text, c='black'):
        self.BeginTextColour( c )
        self.EndTextColour()
        self.AppendText(text)

class LogViewer(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: LogViewer.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.mainPanel = wx.Panel(self, -1)
        self.tabManager = wx.Notebook(self.mainPanel, -1, style=0)
        self.tab1 = wx.Panel(self.tabManager, -1)
        self.tab2 = wx.Panel(self.tabManager, -1)
        self.tab3 = wx.Panel(self.tabManager, -1)
        self.tab4 = wx.Panel(self.tabManager, -1)
        self.tab5 = wx.Panel(self.tabManager, -1)

        self.sizer_3_staticbox = wx.StaticBox(self.tab1, -1, "")
        self.sizer_4_staticbox = wx.StaticBox(self.tab2, -1, "")
        self.sizer_5_staticbox = wx.StaticBox(self.tab3, -1, "")
        self.sizer_6_staticbox = wx.StaticBox(self.tab4, -1, "")
        self.sizer_7_staticbox = wx.StaticBox(self.tab5, -1, "")

        self.sizer_2_staticbox = wx.StaticBox(self.mainPanel, -1, "")
        self.serverLogFile =  wx.TextCtrl(self.tab1, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)
        self.serverLogFile.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier New'))
        self.auFile =  wx.TextCtrl(self.tab2, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)
        self.auFile.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier New'))
        self.serverMegaFile = wx.TextCtrl(self.tab3, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)
        self.serverMegaFile.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier New'))
        self.ocumServerFile = wx.TextCtrl(self.tab4, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)
        self.ocumServerFile.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier New'))
        self.ocumErrorFile = wx.TextCtrl(self.tab5, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)
        self.ocumErrorFile.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Courier New'))
        
        # Menu Bar
        self.frame_1_menubar = wx.MenuBar()
        self.file = wx.Menu()
        self.refreshMenu = self.file.Append(wx.NewId(), "Refresh", "", wx.ITEM_NORMAL)

        self.configMenu = wx.Menu()
        self.show100LinesCheck = self.configMenu.AppendRadioItem(-1, "Show last 100 lines" )
        self.show200LinesCheck = self.configMenu.AppendRadioItem(-1, "Show last 200 lines" )
        self.show500LinesCheck = self.configMenu.AppendRadioItem(-1, "Show last 500 lines" )
        self.show1000LinesCheck = self.configMenu.AppendRadioItem(-1, "Show last 1000 lines" )
        self.show2000LinesCheck = self.configMenu.AppendRadioItem(-1, "Show last 2000 lines" )
        self.show5000LinesCheck = self.configMenu.AppendRadioItem(-1, "Show last 5000 lines" )
        self.showAllLinesCheck = self.configMenu.AppendRadioItem(-1, "Show All lines" )
        self.file.AppendMenu(wx.NewId(), "Config", self.configMenu)

        self.exitMenu = self.file.Append(wx.NewId(), "Exit", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(self.file, "File")
        wxglade_tmp_menu = wx.Menu()
        self.debugCheck = wxglade_tmp_menu.Append(wx.NewId(), "DEBUG", "", wx.ITEM_CHECK)
        self.infoCheck = wxglade_tmp_menu.Append(wx.NewId(), "INFO", "", wx.ITEM_CHECK)
        self.warnCheck = wxglade_tmp_menu.Append(wx.NewId(), "WARN", "", wx.ITEM_CHECK)
        self.errorCheck = wxglade_tmp_menu.Append(wx.NewId(), "ERROR", "", wx.ITEM_CHECK)
        self.traceCheck = wxglade_tmp_menu.Append(wx.NewId(), "TRACE", "", wx.ITEM_CHECK)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "Filter Out")
        self.search = wx.Menu()
        self.findTextMenu = self.search.Append(wx.NewId(), "Find Text", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(self.search, "Search")
        
        self.SetMenuBar(self.frame_1_menubar)
        # Menu Bar end
        self.frame_1_statusbar = self.CreateStatusBar(1, 0)

        self.__set_properties()
        self.__do_layout()
        self.initLocals()

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.tabChangeHandler, self.tabManager)
        self.Bind(wx.EVT_MENU, self.refreshEventHandler, id=self.refreshMenu.GetId())
        self.Bind(wx.EVT_MENU, self.show100LinesEventHandler, id=self.show100LinesCheck.GetId())
        self.Bind(wx.EVT_MENU, self.show200LinesEventHandler, id=self.show200LinesCheck.GetId())
        self.Bind(wx.EVT_MENU, self.show500LinesEventHandler, id=self.show500LinesCheck.GetId())
        self.Bind(wx.EVT_MENU, self.show1000LinesEventHandler, id=self.show1000LinesCheck.GetId())
        self.Bind(wx.EVT_MENU, self.show2000LinesEventHandler, id=self.show2000LinesCheck.GetId())
        self.Bind(wx.EVT_MENU, self.show5000LinesEventHandler, id=self.show5000LinesCheck.GetId())
        self.Bind(wx.EVT_MENU, self.showAllLinesEventHandler, id=self.showAllLinesCheck.GetId())
        self.Bind(wx.EVT_MENU, self.exitEventHandler, id=self.exitMenu.GetId())

        self.Bind(wx.EVT_MENU, self.filterDebugEventHandler, id=self.debugCheck.GetId())
        self.Bind(wx.EVT_MENU, self.filterInfoEventHandler, id=self.infoCheck.GetId())
        self.Bind(wx.EVT_MENU, self.filterWarnEventHandler, id=self.warnCheck.GetId())
        self.Bind(wx.EVT_MENU, self.filterErrorEventHandler, id=self.errorCheck.GetId())
        self.Bind(wx.EVT_MENU, self.filterTraceEventHandler, id=self.traceCheck.GetId())
        self.Bind(wx.EVT_MENU, self.findTextEventHandler, id=self.findTextMenu.GetId())
        self.Bind(wx.EVT_FIND, self.onFindHandler)
        self.Bind(wx.EVT_FIND_NEXT, self.onFindHandler)
        self.Bind(wx.EVT_FIND_CLOSE, self.onFindCloseHandler)
       
        # end wxGlade

    def tabChangeHandler( self, event ):

        if ( self.pos != 0 ):
            self.currentTab.SetStyle(self.pos, self.pos+self.size, wx.TextAttr("black", "white"))

        if ( event.GetSelection() == 0 ):
            self.currentTab = self.serverLogFile
        elif ( event.GetSelection() == 1 ):
            self.currentTab = self.auFile
        elif ( event.GetSelection() == 2 ):
            self.currentTab = self.serverMegaFile
        elif ( event.GetSelection() == 3 ):
            self.currentTab = self.ocumServerFile
        elif ( event.GetSelection() == 4 ):
            self.currentTab = self.ocumErrorFile

        return

    def __set_properties(self):
        # begin wxGlade: LogViewer.__set_properties
        self.SetTitle("Log Viewer")
        self.SetSize((1058, 700))
        self.serverLogFile.SetSize((1058,700))
        self.frame_1_statusbar.SetStatusWidths([-1])
        # statusbar fields
        frame_1_statusbar_fields = ["Last Refresh:"]
        for i in range(len(frame_1_statusbar_fields)):
            self.frame_1_statusbar.SetStatusText(frame_1_statusbar_fields[i], i)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: LogViewer.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.HORIZONTAL)
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.HORIZONTAL)
        sizer_5 = wx.StaticBoxSizer(self.sizer_5_staticbox, wx.HORIZONTAL)
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.HORIZONTAL)
        sizer_7 = wx.StaticBoxSizer(self.sizer_7_staticbox, wx.HORIZONTAL)

        sizer_3.Add(self.serverLogFile, 1, wx.EXPAND, 0)
        self.tab1.SetSizer(sizer_3)
        sizer_4.Add(self.auFile, 1, wx.EXPAND, 0)
        self.tab2.SetSizer(sizer_4)
        sizer_5.Add(self.serverMegaFile, 1, wx.EXPAND, 0)
        self.tab3.SetSizer(sizer_5)
        sizer_6.Add(self.ocumServerFile, 1, wx.EXPAND, 0)
        self.tab4.SetSizer(sizer_6)
        sizer_7.Add(self.ocumErrorFile, 1, wx.EXPAND, 0)
        self.tab5.SetSizer(sizer_7)

        self.tabManager.AddPage(self.tab1, "server.log")
        self.tabManager.AddPage(self.tab2, "au.log")
        self.tabManager.AddPage(self.tab3, "server_mega.log")
        self.tabManager.AddPage(self.tab4, "ocumserver.log")
        self.tabManager.AddPage(self.tab5, "ocum-error.log")
        sizer_2.Add(self.tabManager, 1, wx.EXPAND, 0)
        self.mainPanel.SetSizer(sizer_2)
        sizer_1.Add(self.mainPanel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        self.SetSize((1058, 700))
        # end wxGlade

    def initLocals( self ):
        self.findData = wx.FindReplaceData()   # initializes and holds search parameters
        self.serverIp = ""
        self.password = ""
        self.filterDebug = False
        self.filterInfo = False
        self.filterWarn = False
        self.filterError = False
        self.filterTrace = False
        self.ctrlDown = False
        self.numLines = 100
        self.f = None
        self.parent = None
        self.currentTab = self.serverLogFile
        self.pos = 0
        self.oldpos = 0
        self.size = 0
        self.bundleDirectory = None
        return

    def setServerIp( self, serverIp ):
        self.serverIp = serverIp
        return

    def setParent( self, parent ):
        self.parent = parent
        self.bundleDirectory = self.parent.bundleDirectory
        return

    def run( self ):
        if ( self.parent.isBundleInUse == False ):
            # Get the password for the user specified
            dlg = wx.TextEntryDialog( None, 
                                      "Enter the root password for this server",
                                      "Password",
                                      "",
                                      style=wx.OK|wx.CANCEL|wx.TE_PASSWORD )
            retval = dlg.ShowModal()
            if ( retval == 5100 ):
                self.password = dlg.GetValue()
    
                self.f = FileLoader( self, self.serverIp, self.password, False, False )
                self.f.start()
        else:
            dlg = wx.MessageDialog( self,
                           "Note: Support bundle being used - Do you want to view the logs from that?",
                           "Extract File?",
                           wx.YES_NO | wx.ICON_QUESTION )
            answer = dlg.ShowModal() == wx.ID_YES
            if ( answer == False ):
                # Get the password for the user specified
                dlg = wx.TextEntryDialog( None, 
                                          "Enter the root password for this server",
                                          "Password",
                                          "",
                                          style=wx.OK|wx.CANCEL|wx.TE_PASSWORD )
                retval = dlg.ShowModal()
                if ( retval == 5100 ):
                    self.password = dlg.GetValue()
    
                    self.f = FileLoader( self, self.serverIp, self.password, False, False )
                    self.f.start()
            else:
                self.f = FileLoader( self, self.serverIp, self.password, False, True )
                self.f.start()

        return

    def refreshEventHandler(self, event):
        self.refreshLogs( False )
        return

    def refreshLogs( self, useCache ):
        # Make sure we are not currently loading
        if ( self.f != None and self.f.complete == False ):
            d = wx.MessageDialog(self, "Please wait for existing load to finish", "Wait", wx.OK|wx.ICON_INFORMATION)
            d.ShowModal()
            return

        if ( self.parent.isBundleInUse == False ):
            if ( self.password == "" ): 
                dlg = wx.TextEntryDialog( None, 
                                          "Enter the root password for this server",
                                          "Password",
                                          "",
                                          style=wx.OK|wx.CANCEL|wx.TE_PASSWORD )
                retval = dlg.ShowModal()
                if ( retval == 5100 ):
                    self.password = dlg.GetValue()

        self.serverLogFile.Clear()
        self.auFile.Clear()
        self.serverMegaFile.Clear()
        self.ocumServerFile.Clear()
        self.ocumErrorFile.Clear()
        self.f = FileLoader( self, self.serverIp, self.password, useCache, self.parent.isBundleInUse )
        self.f.start()
        return

    def show100LinesEventHandler( self, event ):
        self.numLines = 100
        self.f.stop()
        self.refreshLogs( True )
        return

    def show200LinesEventHandler( self, event ):
        self.numLines = 200
        self.f.stop()
        self.refreshLogs( True )
        return

    def show500LinesEventHandler( self, event ):
        self.numLines = 500
        self.f.stop()
        self.refreshLogs( True )
        return

    def show1000LinesEventHandler( self, event ):
        self.numLines = 1000
        self.f.stop()
        self.refreshLogs( True )
        return

    def show2000LinesEventHandler( self, event ):
        self.numLines = 2000
        self.f.stop()
        self.refreshLogs( True )
        return

    def show5000LinesEventHandler( self, event ):
        self.numLines = 5000
        self.f.stop()
        self.refreshLogs( True )
        return

    def showAllLinesEventHandler( self, event ):
        self.numLines = -1
        self.f.stop()
        self.refreshLogs( True )
        return

    def exitEventHandler(self, event):
        self.Hide()
        return

    def filterDebugEventHandler(self, event): # wxGlade: LogViewer.<event_handler>
        self.filterDebug = self.debugCheck.IsChecked()
        self.f.stop()
        self.refreshLogs( True )
        return

    def filterInfoEventHandler(self, event): # wxGlade: LogViewer.<event_handler>
        self.filterInfo = self.infoCheck.IsChecked()
        self.f.stop()
        self.refreshLogs( True )
        return

    def filterWarnEventHandler(self, event): # wxGlade: LogViewer.<event_handler>
        self.filterWarn = self.warnCheck.IsChecked()
        self.f.stop()
        self.refreshLogs( True )
        return

    def filterErrorEventHandler(self, event): # wxGlade: LogViewer.<event_handler>
        self.filterError = self.errorCheck.IsChecked()
        self.f.stop()
        self.refreshLogs( True )
        return

    def filterTraceEventHandler(self, event): # wxGlade: LogViewer.<event_handler>
        self.filterTrace = self.traceCheck.IsChecked()
        self.f.stop()
        self.refreshLogs( True )
        return

    def findTextEventHandler(self, event): # wxGlade: LogViewer.<event_handler>
        self.findTextMenu.Enable(False)
        self.dlg = wx.FindReplaceDialog(self.currentTab, self.findData, 'Find')
        self.dlg.Show()
        return

    def onFindCloseHandler( self, event ):
        event.GetDialog().Destroy()

        # Need to remove color around the text
        if ( self.pos != 0 ):
            self.currentTab.SetStyle(self.pos, self.pos+self.size, wx.TextAttr("black", "white"))

        self.findTextMenu.Enable(True)
        return

    def onFindHandler( self, event ):
        print("ON FIND or NEXT")
        
        # Get the information from the dialog
        fstring = self.findData.GetFindString()          # also from event.GetFindString()
        flags = self.findData.GetFlags()
        lookUp = True
        if ( flags & wx.FR_DOWN ):
            lookUp = False
        matchFullWord = False
        if ( flags & wx.FR_WHOLEWORD ):
            matchFullWord = True
        matchCase = False
        if ( flags & wx.FR_MATCHCASE ):
            matchCase = True

        print("lookUp = " + str(lookUp))
        print("Match Full Word: " + str(matchFullWord))
        print("Match Case: " + str(matchCase))
        print("pos before: " + str(self.pos))
        self.oldpos = self.pos

        if ( lookUp == True ):
            if ( self.pos == 0 ):
                self.pos = len(self.currentTab.GetValue())
            else:
                self.pos -= self.size
            if ( matchCase == False ):
                pos = self.currentTab.GetValue().lower().rfind(fstring, 0, self.pos)
            else:
                pos = self.currentTab.GetValue().rfind(fstring, 0, self.pos)
        elif ( lookUp == False ):
            if ( self.pos != 0 ):
                self.pos += self.size
            if ( matchCase == False ):
                pos = self.currentTab.GetValue().lower().find(fstring, self.pos)
            else:
                pos = self.currentTab.GetValue().find(fstring, self.pos)

        # If we did not find anything and we have not found anything before, then prompt a message
        if ( pos == -1 and self.pos == 0 ):
            d = wx.MessageDialog(self, "No match found", "Failed to find a match", wx.OK|wx.ICON_INFORMATION)
            d.ShowModal()
            self.pos = self.oldpos
            return
        elif ( pos == -1 and self.pos != 0 ):
            d = wx.MessageDialog(self, 
                             "No matches found, reverse direction to search", 
                             "Please select a different direction", 
                             wx.OK|wx.ICON_INFORMATION)
            d.ShowModal()
            self.pos = self.oldpos
            return
        self.pos = pos 
        print("pos after: " + str(self.pos))

        # If the pos is not zero, then we have already done one search
        if ( self.oldpos != 0 ):
            self.currentTab.SetStyle(self.oldpos, self.oldpos+self.size, wx.TextAttr("black", "white"))
            self.oldpos = 0

        self.size = len(fstring) 
        self.currentTab.SetStyle(self.pos, self.pos+self.size, wx.TextAttr("red", "yellow"))
        self.currentTab.ShowPosition(self.pos)
        self.currentTab.Refresh()
        self.currentTab.Refresh()
        return

# end of class LogViewer

class FileLoader( threading.Thread ):
    def __init__(self, parent, ip, password, loadFromCache, loadFromBundle):
        self.parent = parent
        self.ip = ip
        self.password = password
        self.loadFromCache = loadFromCache
        self.loadFromBundle = loadFromBundle
        threading.Thread.__init__(self)
        self.complete = False
        self.forceStop = False
        return

    # Force a stop of the loading
    def stop(self):
        self.forceStop = True
        time.sleep(1)
        self.complete = True
        return

    def run(self):

        self.parent.serverLogFile.Clear()
        self.parent.auFile.Clear()
        self.parent.serverMegaFile.Clear()
        self.parent.ocumServerFile.Clear()
        self.parent.ocumErrorFile.Clear()

        conn = None
        fail = False
        if ( self.loadFromCache == False and self.loadFromBundle == False ):
            try:
                cnopts = pysftp.CnOpts()
                cnopts.hostkeys = None
                self.parent.frame_1_statusbar.SetStatusText("Connecting to server", 0)
                conn = pysftp.Connection(host=self.ip, username="root", password=self.password, cnopts=cnopts)
            except Exception as exception:
                d = wx.MessageDialog(self.parent, 
                                 "An error occured communicating with the server: " + str(exception), 
                                 "Failure",
                                 wx.OK|wx.ICON_INFORMATION)
                d.ShowModal()
                if ( "Authentication failed" in str(exception) ):
                    self.parent.password = ""
                self.parent.frame_1_statusbar.SetStatusText("Failed grabbing log files", 0)
                return

        #############################################################################
        # Server Log file
        fail = False
        file = "server.log"
        if ( self.loadFromBundle == True ):
            file = self.parent.bundleDirectory + "\\jboss-logs-server.log"
        if ( self.loadFromCache == False and self.loadFromBundle == False ):
            try:
                self.parent.frame_1_statusbar.SetStatusText("Grabbing server.log file", 0)
                conn.get("/var/log/ocie/server.log")
            except Exception as exception:
                fail = True
                d = wx.MessageDialog(self.parent, 
                                 "An error occured grabbing the server.log file: " + str(exception), 
                                 "Failure",
                                 wx.OK|wx.ICON_INFORMATION)
                d.ShowModal()
                self.parent.frame_1_statusbar.SetStatusText("Failed grabbing server.log file", 0)
        if ( fail == False ):
            self.parent.frame_1_statusbar.SetStatusText("Loading server.log file", 0)
            self.loadFile( self.parent.serverLogFile, file )
        if ( self.forceStop == True ): return

        #############################################################################
        # au Log file
        fail = False
        file = "au.log"
        if ( self.loadFromBundle == True ):
            file = self.parent.bundleDirectory + "\\jboss-logs-au.log"
        if ( self.loadFromCache == False and self.loadFromBundle == False):
            try:
                self.parent.frame_1_statusbar.SetStatusText("Grabbing au.log file", 0)
                conn.get("/var/log/ocie/au.log")
            except Exception as exception:
                fail = True
                d = wx.MessageDialog(self.parent, 
                                 "An error occured grabbing the au.log file: " + str(exception), 
                                 "Failure",
                                 wx.OK|wx.ICON_INFORMATION)
                d.ShowModal()
                self.parent.frame_1_statusbar.SetStatusText("Failed grabbing au.log file", 0)
        if ( fail == False ):
            self.parent.frame_1_statusbar.SetStatusText("Loading au.log file", 0)
            self.loadFile( self.parent.auFile, file )
        if ( self.forceStop == True ): return

        #############################################################################
        # server_mega Log file
        fail = False
        file = "server_mega.log"
        if ( self.loadFromBundle == True ):
            file = self.parent.bundleDirectory + "\\oncommand-logs-server_mega.log"
        if ( self.loadFromCache == False and self.loadFromBundle == False ):
            try:
                self.parent.frame_1_statusbar.SetStatusText("Grabbing " + file + " file", 0)
                conn.get("/var/log/ocie/server_mega.log")
            except Exception as exception:
                fail = True
                d = wx.MessageDialog(self.parent, 
                                 "An error occured grabbing the " + file + " file: " + str(exception), 
                                 "Failure",
                                 wx.OK|wx.ICON_INFORMATION)
                d.ShowModal()
                self.parent.frame_1_statusbar.SetStatusText("Failed grabbing " + file + " file", 0)
        if ( fail == False ):
            self.parent.frame_1_statusbar.SetStatusText("Loading " + file + " file", 0)
            self.loadFile( self.parent.serverMegaFile, file )
        if ( self.forceStop == True ): return

        #############################################################################
        # ocumserver Log file
        fail = False
        file = "ocumserver.log"
        if ( self.loadFromBundle == True ):
            file = self.parent.bundleDirectory + "\\oncommand-logs-ocumserver.log"
        if ( self.loadFromCache == False and self.loadFromBundle == False ):
            try:
                self.parent.frame_1_statusbar.SetStatusText("Grabbing " + file + " file", 0)
                conn.get("/var/log/ocum/ocumserver.log")
            except Exception as exception:
                fail = True
                d = wx.MessageDialog(self.parent, 
                                 "An error occured grabbing the " + file + " file: " + str(exception), 
                                 "Failure",
                                 wx.OK|wx.ICON_INFORMATION)
                d.ShowModal()
                self.parent.frame_1_statusbar.SetStatusText("Failed grabbing " + file + " file", 0)
        if ( fail == False ):
            self.parent.frame_1_statusbar.SetStatusText("Loading " + file + " file", 0)
            self.loadFile( self.parent.ocumServerFile, file )
        if ( self.forceStop == True ): return

        #############################################################################
        # ocum error Log file
        fail = False
        file = "ocum-error.log"
        if ( self.loadFromBundle == True ):
            file = self.parent.bundleDirectory + "\\oncommand-logs-ocum-error.log"
        if ( self.loadFromCache == False and self.loadFromBundle == False):
            try:
                self.parent.frame_1_statusbar.SetStatusText("Grabbing ocum-error.log file", 0)
                conn.get("/var/log/ocum/ocum-error.log")
            except Exception as exception:
                fail = True
                d = wx.MessageDialog(self.parent, 
                                 "An error occured grabbing the ocum-error.log file: " + str(exception), 
                                 "Failure",
                                 wx.OK|wx.ICON_INFORMATION)
                d.ShowModal()
                self.parent.frame_1_statusbar.SetStatusText("Failed grabbing ocum-error.log file", 0)
        if ( fail == False ):
            self.parent.frame_1_statusbar.SetStatusText("Loading ocum-error.log file", 0)
            self.loadFile( self.parent.ocumErrorFile, file )
        if ( self.forceStop == True ): return


        self.parent.frame_1_statusbar.SetStatusText("Refreshed at: " + time.asctime(time.localtime(time.time())), 0)

        self.complete = True

        return


    def loadFile( self, textbox, localFileName ):
        # Now load up the text files
        lines = open(localFileName, "r").readlines()
        linecount = len(lines)
        count = 1
        lineColor = "black"
        filterIt = False

        # If the file is larger than the number of requested lines, cut it down
        #
        #print(linecount)
        #print(self.parent.numLines)
        if ( linecount > self.parent.numLines ):
            revCount = (linecount - self.parent.numLines)
            lines = lines[revCount:]
        #print(len(lines))
        for line in lines:
            if ( self.forceStop == True ): return
            if ( " ERROR " in line ):
                if ( self.parent.filterError == True ):
                    filterIt = True
                    count = count + 1
                    continue
                lineColor = "red"
                filterIt = False
            elif ( " WARN " in line ):
                if ( self.parent.filterWarn == True ):
                    filterIt = True
                    count = count + 1
                    continue
                lineColor = "GOLD"
                filterIt = False
            elif ( " INFO " in line ):
                if ( self.parent.filterInfo == True ):
                    filterIt = True
                    count = count + 1
                    continue
                lineColor = "black"
                filterIt = False
            elif ( " DEBUG " in line ):
                if ( self.parent.filterDebug == True ):
                    filterIt = True
                    count = count + 1
                    continue
                lineColor = "black"
                filterIt = False
            elif ( " TRACE " in line ):
                if ( self.parent.filterTrace == True ):
                    filterIt = True
                    count = count + 1
                    continue
                lineColor = "black"
                filterIt = False
            elif ( filterIt == True ):
                count = count + 1
                continue

            textbox.SetDefaultStyle(wx.TextAttr(lineColor))
            textbox.AppendText(line)
            percent = (count * 100)/linecount
            self.parent.frame_1_statusbar.SetStatusText("Loading " + localFileName + " file: " + str(percent) + "%", 0)
            count = count + 1

        textbox.Refresh()
        textbox.ScrollLines(-1)
        textbox.Refresh()
        return




if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = LogViewer(None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    frame_1.setServerIp("10.97.148.254")
    frame_1.run()
    app.MainLoop()
