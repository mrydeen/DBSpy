#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        DataPlotter.py
# Purpose:     The main file that will plot statistical information on 
#              particlar domain objects.
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import wx, datetime, time, CheckTree, struct, sys, os
from plot import *
from Constants import *
import TimeRangeSelector

###############################################################################
# Globals
###############################################################################

# This will setup the object and its tables.
TABLEMAP = { "netapp_model.cluster": {"opm": ["acquisition_info"], 
                                      "netapp_performance": ["sample_cluster", "summary_cluster" ],
                                      "ocum": ["clusterhistorymonth", "clusterhistoryweek", "clusterhistoryyear"]},
             "netapp_model.node": {"opm": ["acquisition_info"],
                                   "netapp_performance": ["sample_node", "summary_node", "sample_opm_headroom_cpu", "summary_opm_headroom_cpu", "sample_resource_headroom_cpu", "summary_resource_headroom_cpu"],
                                   "ocum": ["clusternodehistorymonth", "clusternodehistoryweek", "clusternodehistoryyear"] },
             "netapp_model.vserver": {"opm": ["acquisition_info"],
                                       "netapp_performance": ["sample_vserver", "summary_vserver", "sample_cifsvserver", "summary_cifsvserver", "sample_fcplifvserver", "summary_fcplifvserver", "sample_iscsilifvserver", "summary_iscsilifvserver", "sample_networklifvserver", "summary_networklifvserver", "sample_nfsv3", "summary_nfsv3", "sample_nfsv4", "summary_nfsv4", "sample_nfsv41", "summary_nfsv41", "sample_nvmffclifvserver", "summary_nvmffclifserver" ]},
             "netapp_model.processor": { "opm": ["acquisition_info"],
                                         "netapp_performance": ["sample_processor", "summary_processor"]},
             "netapp_model.network_port": { "opm": ["acquisition_info"],
                                            "netapp_performance": ["sample_nic", "summary_nic"]},
             "netapp_model.fcp_lif": { "opm": ["acquisition_info"],
                                       "netapp_performance": ["sample_fcplif", "summary_fcplif"]},
             "netapp_model.fcp_port": { "opm": ["acquisition_info"],
                                        "netapp_performance": ["sample_fcpport", "summary_fcpport"]},
             "netapp_model.network_lif": { "opm": ["acquisition_info"],
                                           "netapp_performance": ["sample_networklif", "summary_networklif", "sample_iscsilif", "summary_iscsilif"]},
             "netapp_model.nvmf_fc_lif": { "opm": ["acquisition_info"],
                                           "netapp_performance": ["sample_nvmffclif", "summary_nvmffclif"]},
             "netapp_model.fcpport": { "opm": ["acquisition_info"],
                                       "netapp_performance": ["sample_fcpport", "summary_fcpport"]},
             "netapp_model.iscsilif": { "opm": ["acquisition_info"],
                                        "netapp_performance": ["sample_iscsilif", "summary_iscsilif"]},
             "netapp_model.aggregate": { "opm": ["acquisition_info"],
                                         "netapp_performance": ["sample_aggregate_", "summary_aggregate_", "sample_opm_headroom_aggr_", "summary_opm_headroom_aggr_", "sample_resource_headroom_aggr_", "summary_resource_headroom_aggr_"],
                                         "ocum": ["aggregatehistorymonth", "aggregatehistoryweek", "aggregatehistoryyear"]},
             "netapp_model.disk": { "opm": ["acquisition_info"],
                                    "netapp_performance": ["sample_disk_", "summary_disk_"]},
             "netapp_model.volume": { "opm": ["acquisition_info"],
                                      "netapp_performance": ["sample_qos_volume_workload_",
                                                            "summary_qos_volume_workload_",
                                                            "summary_daily_qos_volume_workload_", 
                                                            "sample_qos_workload_queue_dblade_",
                                                            "summary_qos_workload_queue_dblade_",
                                                            "sample_qos_workload_queue_nblade_",
                                                            "summary_qos_workload_queue_nblade_",
                                                            "sample_volume_objectstore_",
                                                            "summary_volume_objectstore_"],
                                     "ocum": ["volumehistorymonth", "volumehistoryweek", "volumehistoryyear"]},
             "netapp_model.lun": { "opm": ["acquisition_info"],
                                   "netapp_performance": ["sample_lun_", "summary_lun_", "sample_qos_lun_workload_", "summary_qos_lun_workload_"],
                                  "ocum": ["lunhistorymonth", "lunhistoryweek", "lunhistoryyear"]},
             "netapp_model.file": { "opm": ["acquisition_info"],
                                    "netapp_performance": ["sample_qos_file_workload_", "summary_qos_file_workload_"]},
             "netapp_model.namespace": { "opm": ["acquisition_info"],
                                         "netapp_performance": ["sample_namespace_", "summary_namespace_", "summary_daily_namespace_"]},
             "netapp_model.qos_volume_workload": { "opm": ["acquisition_info"],
                                  "netapp_performance": ["sample_qos_volume_workload_", "summary_qos_volume_workload_" ],
                                  "ocum": ["volumehistorymonth", "volumehistoryweek", "volumehistoryyear"]},
             "netapp_model.qos_workload_constituent": { "opm": ["acquisition_info"],
                                                        "netapp_performance": ["sample_qos_workload_constituent_"]},
             "netapp_model.qos_workload_detail": { "opm": ["acquisition_info"],
                                                   "netapp_performance": ["sample_qos_workload_queue_nblade_", "sample_qos_workload_queue_dblade_", "summary_qos_workload_queue_nblade_", "summary_qos_workload_queue_dblade_"]}
           }
# Defines the grouping of statistics.
IDGROUPMAP = { "netapp_model.aggregate": ["clusterId"],
               "netapp_model.disk": ["clusterId"],
               "netapp_model.volume": ["clusterId"],
               "netapp_model.lun": ["clusterId"],
               "netapp_model.file": ["clusterId"],
               "netapp_model.namespace": ["clusterId"],
               "netapp_model.qos_volume_workload": ["clusterId"],
               "netapp_model.qos_workload": ["clusterId"],
               "netapp_model.qos_workload_constituent": ["clusterId"],
               "netapp_model.qos_workload_detail": ["clusterId"],
             }

plotColours = [ 'green', 'red', 'blue', 'purple', 'orange', 'Yellow', 'brown', 'grey', 'sea green', 'dark green', 'lime green', 'dark slate blue', 'green yellow', 'sky blue', 'steel blue' ]
markerColours = [ 'green', 'red', 'blue', 'purple', 'orange', 'Yellow', 'brown', 'grey', 'sea green', 'dark green', 'lime green', 'dark slate blue', 'green yellow', 'sky blue', 'steel blue' ]
plotMarkers = [ 'circle', 'square', 'plus', 'triangle', 'triangle_down', 'cross', 'circle', 'square', 'plus', 'triangle', 'triangle_down', 'cross','circle', 'square', 'plus' ]
MAX_PLOTS = 15

DAYS_IN_MONTH = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
def is_leap( year ): # 1 if leap year, else 0
    if year % 4 != 0: return 0
    if year % 400 == 0: return 1
    return year % 100 != 0

def days_in_month( month, year ): # number of days in month of year
    if month == 2 and is_leap(year): return 29
    return DAYS_IN_MONTH[month-1]

class DataPlotter(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.SYSTEM_MENU|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.mainPanel = wx.Panel(self, -1)

        self.timeRangeStaticBox = wx.StaticBox(self.mainPanel, -1, "Time Range")
        self.timeRangeStaticBox.SetForegroundColour( wx.BLUE )
        self.optionsStaticBox = wx.StaticBox(self.mainPanel, -1, "Options")
        self.optionsStaticBox.SetForegroundColour( wx.BLUE )
        self.topControlStaticBox = wx.StaticBox(self.mainPanel, -1, "Data/Plot Control")
        self.topControlStaticBox.SetForegroundColour( wx.BLUE )
        
        # Menu Bar start
        self.frame_1_menubar = wx.MenuBar()
        self.SetMenuBar(self.frame_1_menubar)
        self.CreateStatusBar(True)

        wxglade_tmp_menu = wx.Menu()
        exitId = wx.NewId()
        wxglade_tmp_menu.Append(exitId, "Exit", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "File")

        wxglade_tmp_menu = wx.Menu()
        redrawId = wx.NewId()
        wxglade_tmp_menu.Append(redrawId, "Redraw", "", wx.ITEM_NORMAL)
        resetId = wx.NewId()
        wxglade_tmp_menu.Append(resetId, "Reset", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "Plot")

        analysisMenu = wx.Menu()
        addMetric = wx.NewId()
        analysisMenu.Append(addMetric, "Add Metric", "", wx.ITEM_NORMAL)
        editMetric = wx.NewId()
        analysisMenu.Append(addMetric, "Edit Metric", "", wx.ITEM_NORMAL)
        removeMetric = wx.NewId()
        analysisMenu.Append(removeMetric, "Remove Metric", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(analysisMenu, "Analyze")

        wxglade_tmp_menu = wx.Menu()
        alaskaTZ = wx.NewId()
        wxglade_tmp_menu.Append(alaskaTZ, "Alaska Standard Time (-9)", "", wx.ITEM_RADIO)
        pacificTZ = wx.NewId()
        wxglade_tmp_menu.Append(pacificTZ, "Pacific Standard Time (-8)", "", wx.ITEM_RADIO)
        mountainTZ = wx.NewId()
        wxglade_tmp_menu.Append(mountainTZ, "Mountain Standard Time (-7)", "", wx.ITEM_RADIO)
        centralTZ = wx.NewId()
        wxglade_tmp_menu.Append(centralTZ, "Central Standard Time (-6)", "", wx.ITEM_RADIO)
        easternTZ = wx.NewId()
        wxglade_tmp_menu.Append(easternTZ, "Eastern Standard Time (-5)", "", wx.ITEM_RADIO)
        atlanticTZ = wx.NewId()
        wxglade_tmp_menu.Append(atlanticTZ, "Atlantic Standard Time (-4)", "", wx.ITEM_RADIO)
        greenwichTZ = wx.NewId()
        wxglade_tmp_menu.Append(greenwichTZ, "Greenwich Mean Time (0)", "", wx.ITEM_RADIO)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "TimeZone")
        wxglade_tmp_menu.Check( easternTZ, True )

        wxglade_tmp_menu = wx.Menu()
        helpId = wx.NewId()
        wxglade_tmp_menu.Append(helpId, "Content", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "Help")
        # Menu Bar end

        self.staticLineBtwMenuAndPlotControl = wx.StaticLine(self, -1)
        self.fromTimeRangeSelectText = wx.TextCtrl(self.mainPanel, wx.ID_ANY, "")
        self.label_1 = wx.StaticText(self.mainPanel, wx.ID_ANY, "to")
        self.toTimeRangeSelectionText = wx.TextCtrl(self.mainPanel, wx.ID_ANY, "")
        self.timeRangeButton = wx.BitmapButton(self.mainPanel, wx.ID_ANY, wx.Bitmap("images\\timeRange.png", wx.BITMAP_TYPE_ANY))

        self.zoomCheckBox = wx.CheckBox(self.mainPanel, -1, "Zoom")
        self.dragCheckBox = wx.CheckBox(self.mainPanel, -1, "Drag")
        self.gridCheckBox = wx.CheckBox(self.mainPanel, -1, "Grid")
        self.pointLabelCheckBox = wx.CheckBox(self.mainPanel, -1, "Point Label")
        #self.pancakeCheckBox = wx.CheckBox(self.mainPanel, -1, "Pancake")
        self.staticLineBtwPlotControlAndPlot = wx.StaticLine(self.mainPanel, -1)
        self.staticLineBtwPlotAndBottom = wx.StaticLine(self.mainPanel, -1)

        self.splitWindow = wx.SplitterWindow(self.mainPanel, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.splitWindowPaneOne = wx.Panel(self.splitWindow, -1)
        self.splitWindowPaneTwo = wx.Panel(self.splitWindow, -1)

        # Check Tree 
        self.tree = CheckTree.CheckTreeCtrl( self.splitWindowPaneOne, -1, size=(350,-1), style=CheckTree.CT_AUTO_CHECK_CHILD|wx.TR_DEFAULT_STYLE )
        #self.Bind( wx.EVT_TREE_SEL_CHANGED, self.treeSelChangedCallback, self.tree )
        self.Bind( CheckTree.EVT_CHECKTREECTRL, self.treeSelChangedCallback, self.tree )

        # Main Canvas for which to write.
        self.plot = PlotCanvas(self.splitWindowPaneTwo, -1)
        self.plot.SetPointLabelFunc( self.DrawPointLabel )
        # Create mouse event for showing cursor coords in status bar
        self.plot.canvas.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.plot.canvas.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        # Show closest point when enabled
        self.plot.canvas.Bind(wx.EVT_MOTION, self.OnMotion)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_MENU, self.menuFileExit, id=exitId)
        self.Bind(wx.EVT_MENU, self.menuPlotRedraw, id=redrawId)
        self.Bind(wx.EVT_MENU, self.menuPlotReset, id=resetId)
        self.Bind(wx.EVT_MENU, self.menuAddMetric, id=addMetric)
        self.Bind(wx.EVT_MENU, self.menuEditMetric, id=editMetric)
        self.Bind(wx.EVT_MENU, self.menuRemoveMetric, id=removeMetric)
        self.Bind(wx.EVT_CHECKBOX, self.zoomCheckBoxCallBack, self.zoomCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.dragCheckBoxCallBack, self.dragCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.gridCheckBoxCallBack, self.gridCheckBox)
        self.Bind(wx.EVT_CHECKBOX, self.pointLabelCheckBoxCallBack, self.pointLabelCheckBox)
        #self.Bind(wx.EVT_CHECKBOX, self.pancakeCheckBoxCallBack, self.pancakeCheckBox)

        self.Bind(wx.EVT_MENU, self.alaskaTZCallBack, id=alaskaTZ)
        self.Bind(wx.EVT_MENU, self.pacificTZCallBack, id=pacificTZ)
        self.Bind(wx.EVT_MENU, self.mountainTZCallBack, id=mountainTZ)
        self.Bind(wx.EVT_MENU, self.centralTZCallBack, id=centralTZ)
        self.Bind(wx.EVT_MENU, self.easternTZCallBack, id=easternTZ)
        self.Bind(wx.EVT_MENU, self.atlanticTZCallBack, id=atlanticTZ)
        self.Bind(wx.EVT_MENU, self.greenwichTZCallBack, id=greenwichTZ)

        self.Bind(wx.EVT_BUTTON, self.timeRangeButtonHandler, self.timeRangeButton)

        self.initLocals()
        return

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.SetTitle("Data Plotter")
        self.SetSize((1250, 600))
        self.fromTimeRangeSelectText.SetSize((200, -1))
        self.toTimeRangeSelectionText.SetSize((200, -1))
        self.timeRangeButton.SetSize(self.timeRangeButton.GetBestSize())
        return

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.staticLineBtwMenuAndPlotControl, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)


        insideTopControlSizer = wx.StaticBoxSizer(self.topControlStaticBox, wx.HORIZONTAL)

        # Time Range Box Layout
        insideTimeRangeSizer = wx.StaticBoxSizer(self.timeRangeStaticBox, wx.HORIZONTAL)
        insideTimeRangeSizer.Add(self.fromTimeRangeSelectText, 0, 0, 0)
        insideTimeRangeSizer.Add(self.label_1, 0, wx.LEFT | wx.RIGHT | wx.TOP, 4)
        insideTimeRangeSizer.Add(self.toTimeRangeSelectionText, 0, 0, 0)
        insideTimeRangeSizer.Add(self.timeRangeButton, 0, wx.LEFT, 2)
        insideTopControlSizer.Add(insideTimeRangeSizer, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 4)

        # Options Layout 
        insideOptionsSizer = wx.StaticBoxSizer(self.optionsStaticBox, wx.HORIZONTAL)
        optionsSizer = wx.BoxSizer(wx.HORIZONTAL)
        optionsSizer.Add(self.zoomCheckBox, 0, wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 4)
        optionsSizer.Add(self.dragCheckBox, 0, wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 4)
        optionsSizer.Add(self.gridCheckBox, 0, wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 4)
        optionsSizer.Add(self.pointLabelCheckBox, 0, wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 4)
        #optionsSizer.Add(self.pancakeCheckBox, 0, wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 4)
        insideOptionsSizer.Add(optionsSizer, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        insideTopControlSizer.Add(insideOptionsSizer, 0, wx.LEFT|wx.RIGHT|wx.EXPAND|wx.ADJUST_MINSIZE, 4)

        veryTopSizer = wx.BoxSizer(wx.VERTICAL)
        veryTopSizer.Add(insideTopControlSizer, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.ADJUST_MINSIZE, 4)

        # Layout for static line between plot control and the plot
        veryTopSizer.Add(self.staticLineBtwPlotControlAndPlot, 0, wx.EXPAND, 0)

        # Adding the plot and tree
        treeSizer = wx.BoxSizer(wx.HORIZONTAL)
        treeSizer.Add(self.tree, 0, wx.ALIGN_BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 1)
        self.splitWindowPaneOne.SetSizer(treeSizer)
        plotSizer = wx.BoxSizer(wx.HORIZONTAL)
        plotSizer.Add(self.plot, 1, wx.LEFT|wx.EXPAND|wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT, 1)
        self.splitWindowPaneTwo.SetSizer(plotSizer)
        veryTopSizer.Add(self.splitWindow, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 1)

        # Layout for static line between plot and bottom 
        veryTopSizer.Add(self.staticLineBtwPlotAndBottom, 0, wx.EXPAND, 0)

        self.splitWindow.SplitVertically(self.splitWindowPaneOne, self.splitWindowPaneTwo)
        self.splitWindow.SetSashPosition( 350 )
        self.mainPanel.SetAutoLayout(True)
        self.mainPanel.SetSizer(veryTopSizer)
        veryTopSizer.Fit(self.mainPanel)
        veryTopSizer.SetSizeHints(self.mainPanel)

        mainSizer.Add(self.mainPanel, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        self.SetAutoLayout(True)
        self.SetSizer(mainSizer)
        self.Layout()
        # end wxGlade
        return

    def initLocals( self ):
        self.isScaleMonitor = False
        self.currentTime = time.time()
        dt = wx.DateTime.Now()
        self.fromTimeRangeSelectText.SetValue( str(dt) )
        self.toTimeRangeSelectionText.SetValue( str(dt) )
        threeDaysBackInSeconds = 3 * 24 * 60 * 60
        fromTime = int(self.currentTime - threeDaysBackInSeconds) 
        date = datetime.datetime.fromtimestamp(fromTime).strftime("%m/%d/%Y")
        fromTime = self.fromTimeRangeSelectText.GetValue().split()[1:]
        newTime = " "
        newTime = newTime.join(fromTime)
        # Strip off the times and place together
        self.fromTimeRangeSelectText.SetValue( date + " " + newTime )

        self.plot.SetEnableLegend(True)
        self.colorIndexs = [ False, False, False, False, False, False, False, False, False, False, False, False, False, False, False ]
        self.parent = None
        self.tables = []
        self.pancake = True
        #self.pancakeCheckBox.SetValue(True)
        self.pointLabelCheckBox.SetValue(True)
        self.plot.SetEnablePointLabel(True)
        self.edit = False
        self.plots = {}
        self.timeDiff = 0 # Eastern Standard Time

        self.objectName = None
        self.objectId = None
        self.objectType = None
        self.containerId = None
        self.objectName2 = None
        self.objectId2 = None
        self.objectType2 = None
        self.containerId2 = None
        self.sourceType = None

        self.currentDataPoint = None
        self.currentPlot = None
        self.lockPoint = False

        self.policies = {}
        self.thresholdsByPolicyId = {}
        self.thresholds = {}
        self.root = None
        self.analysisNode = None

        self.metrics = {}

        return

    def alaskaTZCallBack( self, event ):
        print("alaskaTZCallBack")
        self.timeDiff = -9
        return
    def pacificTZCallBack( self, event ): 
        print("pacific callback ")
        self.timeDiff = -8
        return
    def mountainTZCallBack( self, event ):
        print("mountain callback")
        self.timeDiff = -7
        return
    def centralTZCallBack( self, event ):
        print("central callback")
        self.timeDiff = -6
        return
    def easternTZCallBack( self, event ):
        print("eastern callback")
        self.timeDiff = -5
        return
    def atlanticTZCallBack( self, event ):
        print("atlantic callback")
        self.timeDiff = -4
        return
    def greenwichTZCallBack( self, event ):
        print("greenwich callback")
        self.timeDiff = 0
        return
    
    def rightDownEvent( self, event ):
        print("Right Down Event")
        return

    def timeRangeButtonHandler(self, event):  # wxGlade: MyFrame1.<event_handler>
        trs = TimeRangeSelector.TimeRangeSelector(None, wx.ID_ANY, "")
        trs.setApplyCallback( self.timeSelectApplyCallback )
        trs.setCancelCallback( self.timeSelectCancelCallback )
        trs.Show()
        self.Disable()
        return

    def timeSelectApplyCallback( self, fromTime, toTime ):
        self.fromTimeRangeSelectText.SetValue(fromTime)
        self.toTimeRangeSelectionText.SetValue(toTime)
        self.Enable()
        # Now need to redraw each plot.
        self.refreshAllItems()
        return

    def timeSelectCancelCallback( self ):
        self.Enable()
        return


    #
    # When a checkbox has been modified (selected/deselected), this callback is called.
    # 
    def treeSelChangedCallback( self, event ):

        item = None
        try: 
            item = event.GetItem()
        except:
            item = event

        removeItem = False
        if ( not self.tree.IsItemChecked(item) ):
            removeItem = True

        # Make sure only 8 items are checked.
        if ( removeItem == False and len(self.plots.values()) == MAX_PLOTS ):
            wx.MessageBox("Only " + str(MAX_PLOTS) + " plots allowed" )
            self.tree.CheckItem( item, checked=False)
            return

        columnOrAttribute = self.tree.GetItemText(item)
        # If the columnOrAttribute is really a table, just ignore
        if ( "sample" in columnOrAttribute or "summary" in columnOrAttribute or "Scale" in columnOrAttribute ):
            return
        parent = self.tree.GetItemParent(item)
        table = self.tree.GetItemText(parent)

        # See if there is a comment on the end
        type = None
        dbTable = table
        objId = self.objectId
        if ( "(" in table ):
            tokens = table.split(" ")
            dbTable = tokens[0]
            if ( ":" not in tokens[1] ):
                db = tokens[1][1:-1]
            else:
                db = tokens[1][1:-1].split(":")[0]
                objId = tokens[1][1:-1].split(":")[2]
            dbTable = db + "." + dbTable

        if ( removeItem == False ):
            cmd = ""
            if ( not self.isScaleMonitor ):
                # Figure out the time column
                stime = "time"
                if ( "summary" in dbTable ):
                    stime = "fromtime"
                elif ( "history" in dbTable ):
                    stime = "periodEndTime"

                # Figure out the id string
                idStr = "objid"
                tmpColumn = columnOrAttribute
                print(self.objectTableName)
                if ( "cluster" in self.objectTableName and "sample_cluster" not in table and "summary_cluster" not in table):
                    idStr = "clusterId"
                    if ( columnOrAttribute == "Minutes between collections" ):
                        tmpColumn = "success"
                elif ("history" in table):
                    if ("Sum" in tmpColumn):
                        tmpColumn = tmpColumn + "/sampleCount"

                    if ("volume" in self.objectTableName):
                        idStr = "volumeId"
                    elif ("clusternode" in self.objectTableName):
                        idStr = "clusterNodeId"
                    elif ("cluster" in self.objectTableName):
                        idStr = "clusterId"
                    elif ("lun" in self.objectTableName):
                        idStr = "lunId"
                    elif ("aggregate" in self.objectTableName):
                        idStr = "aggregateId"
                elif ("acquisition_info" in table):
                    idStr = "clusterId"

                cmd = "select " + tmpColumn + ", " + stime + " from " + dbTable + " where " + idStr + "=" + str(objId)
                if ( ("workload" in dbTable and "nblade" not in dbTable and "dblade" not in dbTable) and self.workloadId != None ):
                    cmd = "select " + tmpColumn + ", " + stime + " from " + dbTable + " where " + idStr + "=" + str(self.workloadId)
                elif ("headroom_aggr" in dbTable):
                    cmd = "select " + tmpColumn + ", " + stime + " from " + dbTable + " where " + idStr + "=" + str(self.resourceAggrId)
                elif ("history" in dbTable):
                    cmd = "select " + tmpColumn + ", (UNIX_TIMESTAMP(" + stime + ")*1000) from " + dbTable + " where " + idStr + "=" + str(objId)
                elif ("objectstore" in dbTable):
                    cmd = "select " + tmpColumn + ", " + stime + " from " + dbTable + " where " + idStr + "=" + str(self.volumeObjectStoreMappingId)
                elif ("acquisition_info" in dbTable):
                    cmd = "select " + tmpColumn + ", " + stime + " from " + dbTable + " where " + idStr + "=" + str(self.clusterId)
    
                # Performance stats have an empty column we need to look for
                if ( "summary" not in cmd and "acquisition_info" not in cmd and "history" not in cmd):
                    cmd += " and `empty`=0 "

                # This handles the general performance stats format with time which is a seconds
                fromTime = datetime.datetime.strptime(self.fromTimeRangeSelectText.GetValue(), "%m/%d/%Y %I:%M:%S %p")
                toTime = datetime.datetime.strptime(self.toTimeRangeSelectionText.GetValue(), "%m/%d/%Y %I:%M:%S %p")
                if ( "history" not in cmd ):
                    cmd += " and " + stime + " >= " + str(int(time.mktime(fromTime.timetuple())*1000)) + " and " + stime + " <= " + str(int(time.mktime(toTime.timetuple())*1000)) + " order by " + stime + " desc"
                else:
                    cmd += " and " + stime + " >= \'" + str(fromTime) + "\' and " + stime + " <= \'" + str(toTime) + "\' order by " + stime + " desc"
            else:
                fromTime = datetime.datetime.strptime(self.fromTimeRangeSelectText.GetValue(), "%m/%d/%Y %I:%M:%S %p")
                toTime = datetime.datetime.strptime(self.toTimeRangeSelectionText.GetValue(), "%m/%d/%Y %I:%M:%S %p")
                cmd = "select v.value, s.timestamp from scalemonitor.sample s, scalemonitor.attribute a, scalemonitor.value v where s.id=v.sample_id and a.id=v.attribute_id and a.name=\'" + columnOrAttribute.split()[0] + "\' and s.timestamp >= " + str(int(time.mktime(fromTime.timetuple())*1000)) + " and s.timestamp <= " + str(int(time.mktime(toTime.timetuple())*1000)) + " order by s.timestamp desc"
                #print(cmd)
    
            self.plotCharts(cmd, table, columnOrAttribute, item)

        else:
            #print("Removing Column = " + columnOrAttribute)
            if ( table != "Policy Thresholds" and table != "Metrics" ):
                # Need to remove all of the metrics for that one metric.
                keys = list(self.plots)
                for key in keys:
                    if ( columnOrAttribute in key ):
                        plot = self.plots.pop( key )
                        self.colorIndexs[ plot.colorIndex ] = False

            elif ( table == "Metrics" ):
                # Need to remove all of the metrics for that one metric.
                keys = list(self.plots)
                for key in keys:
                    if ( columnOrAttribute in key ):
                        plot = self.plots.pop( key )
                        self.colorIndexs[ plot.colorIndex ] = False
            else:
                # Need to pull both plots off the grid for the policy
                policyName = columnOrAttribute.split(":")[0]
                plot = self.plots.pop( policyName + " - min:"+table )
                self.colorIndexs[ plot.colorIndex ] = False
                plot = self.plots.pop( policyName + " - max:"+table )
                self.colorIndexs[ plot.colorIndex ] = False

            try:
                self.plot.Draw( self.produceGraph( "" ) )
            except:
                pass
        return

    # This is called when a new time has been selected.
    def refreshAllItems(self):
        selectedItems = []
        keys = list(self.plots)
        for key in keys:
            plot = self.plots.pop( key )
            selectedItems.append(plot.item)
            self.colorIndexs[ plot.colorIndex ] = False

        try:
            self.plot.Draw( self.produceGraph( "" ) )
        except:
            pass

        # Now redraw based on the new data.
        for checkBox in selectedItems:
            self.treeSelChangedCallback( checkBox )
        return


    def setParent( self, parent ):
        self.parent = parent
        return

    def setScaleMonitorViewing(self):
        self.isScaleMonitor = True

        self.SetTitle("Data Plotter: UM Scale Monitor Metrics")
        # Grab all of the scale monitor attributes
        self.scaleMonitorAttributes = self.parent.executeAll("select * from scalemonitor.attribute")

        # Now walk the tables and add them and the columns to the tree
        self.root = self.tree.AddRoot("Unified Manager", image=-1 )
        node = self.tree.AppendItem(self.root, "Scale Monitor Attributes", image=-1 )
        for attrib in self.scaleMonitorAttributes:
            label = attrib[1]
            if ( attrib[2] != "" ):
                label = label + " (" + attrib[2] + ")"
            leaf = self.tree.AppendItem(node, label)

        self.analysisNode = self.tree.AppendItem(self.root, "Metrics", image=-1 )
        self.averageItem = self.tree.AppendItem(self.analysisNode, "Average" )
        self.maxItem  = self.tree.AppendItem(self.analysisNode, "Max" )
        self.minItem = self.tree.AppendItem(self.analysisNode, "Min" )
        self.tree.Expand(self.root)

        return

    def setObject( self, objectTableName, selection, columns ):

        self.objectTableName = objectTableName
        self.columns = columns
        self.values = selection
        self.workloadId = None
        self.resourceAggrId = None
        self.volumeObjectStoreMappingId = None
        self.workloadNodeRelationships = []

        if ( self.objectTableName == "netapp_model.volume" or
             (self.objectTableName == "netapp_model.lun" and self.parent.version >= 7.3) or
             (self.objectTableName == "netapp_model.file" and self.parent.version >= 7.3)):
            #print("Volume Id = " + str(self.values[0]))
            try:
                if ( self.parent.version < 7.3 ):
                    self.workloadId = self.parent.executeAll("select objid from netapp_model.qos_volume_workload where volumeId=" + str(self.values[0]))[0][0]
                    ids = self.parent.executeAll("select objid from netapp_model.qos_workload_node_relationship where workloadId="+str(self.workloadId))
                else:
                    self.workloadId = self.parent.executeAll("select objid from netapp_model.qos_workload where holderId=" + str(self.values[0]))[0][0]
                    ids = self.parent.executeAll("select objid from netapp_model.qos_workload_node_relationship where workloadId="+str(self.workloadId))
                for id in ids:
                    self.workloadNodeRelationships.append( id[0] )
            except:
                pass

            # If this is a volume, see if it has a mapping to a FabricPool.
            if (self.objectTableName == "netapp_model.volume"):
                mappings = self.parent.executeAll("select objid from netapp_model.volume_objectstore_config_mapping where volumeId = " + str(self.values[0]))
                if (len(mappings) != 0):
                    self.volumeObjectStoreMappingId = mappings[0][0]

            #print(self.workloadId)
            #forecast = self.parent.executeAll("select data from opm.forecast where objId=" + str(vwld))
            #print(forecast)
            #fcast = forecast[0][-1]
            #print(fcast)
            #print(struct.unpack('f', fcast))
        elif (self.objectTableName == "netapp_model.aggregate"):
            self.resourceAggrId = self.parent.executeAll("select objid from netapp_model.resource_aggregate where aggregateId = " + str(self.values[0]))[0][0]

        nameIndex = self.parent.findColumnIndex( "name", self.columns )
        if ( nameIndex == -1 ):
            if ( self.objectTableName == "netapp_model.lun" or self.objectTableName == "netapp_model.namespace" ):
                nameIndex = self.parent.findColumnIndex( "path", self.columns )
            else:
                nameIndex = self.parent.findColumnIndex( "uuid", self.columns )
        self.objectName = self.values[nameIndex]
        self.objectId = self.values[0]

        groupIndex = -1
        self.groupId = None
        self.clusterId = None
        if ( self.objectTableName in IDGROUPMAP.keys() ):
            groupIndex = self.parent.findColumnIndex( IDGROUPMAP[self.objectTableName][0], self.columns )
            self.groupId = self.values[groupIndex]
            clusterIdIndex = self.parent.findColumnIndex( "clusterId", self.columns )
            self.clusterId = self.values[clusterIdIndex]
        elif (self.objectTableName == "netapp_model.cluster"):
            self.clusterId = self.objectId

        self.SetTitle("Data Plotter: " + self.objectName + " (" + str(self.objectId) + ")")
        #print(groupIndex)
        #print(self.groupId)

        # Now find out what the tables will be.
        dbs = TABLEMAP[self.objectTableName]

        # Now walk the tables and add them and the columns to the tree
        self.root = self.tree.AddRoot(self.objectName, image=-1 )
        for db in dbs.keys():
            tables = dbs[db]
            for table in tables:

                # If this is a volume and the volume does not have an object store mapping id, then
                # do not show the objectstore stats tables
                if (self.objectTableName == "netapp_model.volume" and "objectstore" in table and self.volumeObjectStoreMappingId == None):
                    print("NOT ADDING")
                    continue

                tableName = table

                # Need to exclude the capacity history tables because they are not sharded.
                if ( self.groupId != None and "history" not in tableName and "acquisition" not in tableName):
                    if ( "workload" in tableName ):
                        tableName = tableName + str(self.clusterId)
                    else:
                        tableName = tableName + str(self.groupId)
                # In the case of the volume, we want to be able to show the regular volume
                # stats, the volume workload stats, and the queue statistics from the
                # nblade and dblade.  So we need to tag some more information on the 
                # name to be able to parse the information.
                if ( "queue" not in tableName ):
                    branchName = tableName + " (" + db + ")"

                    # Get the columns
                    cmd = "show columns from " + db + "." + tableName
                    try:
                        columns = self.parent.executeAll(cmd, ignoreError=True )
                        if ( "Error" in columns ):
                            # Table does not exist
                            continue
                    except:
                        print("Failed to execute: " + cmd)
                        continue

                    node = self.tree.AppendItem(self.root, branchName, image=-1 )

                    # If the object is the cluster, we want to see the collection gaps
                    if ( self.objectTableName == "netapp_model.cluster" and "acquisition_info" in tableName ):
                        leaf = self.tree.AppendItem(node, "Minutes between collections" )

                    for column in columns:
                        if ( "Id" not in column[0] and 
                             "id" not in column[0] and 
                             column[0] != "time" and 
                             column[0] != "fromtime" and 
                             column[0] != "totime" and 
                             column[0] != "empty" and 
                             column[0] != "objType" and 
                             column[0] != "sampleCount" and 
                             column[0] != "periodEndTime" and 
                             column[0] != "forecastType" and 
                             "type" not in column[0] and 
                             "objectType" not in column[0] and 
                             "timestamp" not in column[0] ):
                            leaf = self.tree.AppendItem(node, column[0] )
                else:        
                    # This is one of the workload queue Xblade statistics.  Each workload
                    # has statitsics per node so we need to create a tree for each
                    # node which was found earlier and stored in the workloadNodeRelationships
                    # array
                    for wnr in self.workloadNodeRelationships:
                        # Lets get the node name.
                        cmd = "select nodeId from netapp_model.qos_workload_node_relationship where objid="+str(wnr)
                        nodeId = self.parent.executeAll(cmd)[0][0]
                        cmd = "select name from netapp_model.node where objid="+str(nodeId)
                        nodeName = self.parent.executeAll(cmd)[0][0]

                        branchName = tableName + " (" + db + ":" + nodeName + ":" + str(wnr) + ")"

                        node = self.tree.AppendItem(self.root, branchName, image=-1 )

                        # Get the columns
                        cmd = "show columns from " + db + "." + tableName
                        try:
                            columns = self.parent.executeAll(cmd)
                        except:
                            print("Failed to execute: " + cmd)
                            continue

                        # If the object is the cluster, we want to see the collection gaps
                        if ( self.objectTableName == "netapp_model.cluster" and "acquisition_info" in tableName ):
                            leaf = self.tree.AppendItem(node, "Minutes between collections" )
    
                        for column in columns:
                            if ( "Id" not in column[0] and 
                                 "id" not in column[0] and 
                                 column[0] != "time" and 
                                 column[0] != "fromtime" and 
                                 column[0] != "totime" and 
                                 column[0] != "empty" and 
                                 column[0] != "objType" and 
                                 column[0] != "forecastType" and 
                                 "type" not in column[0] and 
                                 "objectType" not in column[0] and 
                                 "timestamp" not in column[0] ):
                                leaf = self.tree.AppendItem(node, column[0] )

        self.analysisNode = self.tree.AppendItem(self.root, "Metrics", image=-1 )
        self.averageItem = self.tree.AppendItem(self.analysisNode, "Average" )
        self.maxItem  = self.tree.AppendItem(self.analysisNode, "Max" )
        self.minItem = self.tree.AppendItem(self.analysisNode, "Min" )


        # Now we need to see if this object has any policies that we want to show, but
        # only do this for 2.x versions
        if ( self.parent.opm_version != "" ):
            version = eval(self.parent.opm_version.split(".")[0])
            if ( version >= 2 ):
                cmd = "select * from opm.threshold_policy_mapping where objectId = " + str(self.objectId) + " and endTime IS null"
                self.policyMappings = self.parent.executeAll( cmd )
                self.policies = {}
                self.thresholdsByPolicyId = {}
                self.thresholds = {}

                for map in self.policyMappings:
                    cmd = "select * from opm.threshold_policy where id = " + str(map[1])
                    policy = self.parent.executeAll( cmd )[0]
                    self.policies[policy[0]] = policy
                    cmd = "select * from opm.threshold where policyId = " + str(map[1])
                    threshold = self.parent.executeAll( cmd )[0]
                    self.thresholds[threshold[0]] = threshold
                    self.thresholdsByPolicyId[policy[0]] = threshold
 
                if ( len(self.policyMappings) > 0 ):
                    node = self.tree.AppendItem(self.root, "Policy Thresholds", image=-1 )
                    for key in self.policies.keys():
                        policy = self.policies[key]
                        threshold = self.thresholdsByPolicyId[policy[0]]
                        name = policy[1] + ": (" + str(threshold[7]) + " / " + str(threshold[8]) + ")"
                        leaf = self.tree.AppendItem(node, name)
    
        self.tree.Expand(self.root)

        return

    def DrawPointLabel(self, dc, mDataDict):
        if ( self.lockPoint == True ): return

        dc.SetPen(wx.Pen(wx.BLACK))
        dc.SetBrush(wx.Brush( wx.BLACK, wx.SOLID ) )
        
        sx, sy = mDataDict["scaledXY"] #scaled x,y of closest point
        dc.DrawRectangle( sx-5,sy-5, 10, 10)  #10by10 square centered on point
        px,py = mDataDict["pointXY"]
        cNum = mDataDict["curveNum"]
        pntIn = mDataDict["pIndex"]
        legend = mDataDict["legend"]

        # Need to look through the current plots and look at the dataPoints
        # PX (Plot X) should be the date
        # make a string to display
        s = ""
        print("PX,PY = " + str((px,py)))
        print("pntIn = " + str(pntIn))
        for plot in self.plots.values():
            # the PX should be the index into the data plot.
            if ( px not in plot.dataPoints.keys() ): continue
            data = plot.dataPoints[px]
            #print(str(data))
            if (data.value == py):
                displayValue = py
                if ( data.displayValue == -1 ):
                    displayValue = "missing"
                try:
                    s = "  " + str(displayValue) + " (" + data.timestamp.ctime() + ") " + plot.tableColumn
                except:
                    s = "  " + str(displayValue) + " (" + data.timestamp + ") " + plot.tableColumn
                self.currentDataPoint = data
                self.currentPlot = plot
                break
        print(s)
        dc.DrawText(s, sx , sy+1)
        self.SetStatusText(s)
        return

    def OnMouseLeftDown(self,event):
        s= "Value At Point: (%.4f, %.4f)" % self.plot.GetXY(event)
        self.SetStatusText(s)
        event.Skip()            #allows plotCanvas OnMouseLeftDown to be called
        return

    def OnMouseRightDown(self,event):
        if self.plot.GetEnablePointLabel() == True:
            self.menu = wx.Menu()

            id = wx.NewId() 
            self.menu.Append( id, "Set As Start Time" )
            wx.EVT_MENU( self.menu, id, self.setAsStartTimeCb )

            id = wx.NewId() 
            self.menu.Append( id, "Set As End Time" )
            wx.EVT_MENU( self.menu, id, self.setAsEndTimeCb )

            id = wx.NewId() 
            self.menu.Append( id, "Copy to Clipboard" )
            wx.EVT_MENU( self.menu, id, self.copyToClipboardCb )

            id = wx.NewId() 
            self.menu.Append( id, "Edit Statistic" )
            wx.EVT_MENU( self.menu, id, self.editStatisticsCb )

            pos = event.GetPosition()
            newpos = (pos[0]+355, pos[1]-10)
            self.PopupMenu( self.menu, newpos )
        event.Skip()            #allows plotCanvas OnMouseLeftDown to be called
        return

    ###########################################################################
    # Copy the current value to the clipboard
    ###########################################################################
    def copyToClipboardCb( self, event ):
        self.lockPoint = True
        os.system( "echo " + str(self.currentDataPoint.value) + " | clip" )
        self.lockPoint = False
        return


    ###########################################################################
    # Set the current point as the end time 
    ###########################################################################
    def setAsEndTimeCb( self, event ):
        self.lockPoint = True
        mdate = datetime.datetime.fromtimestamp(self.currentDataPoint.trueDate/1000).strftime("%m/%d/%Y %I:%M:%S %p")
        self.toTimeRangeSelectionText.SetValue(mdate)
        self.lockPoint = False
        return

    ###########################################################################
    # Set the current point as the start time 
    ###########################################################################
    def setAsStartTimeCb( self, event ):
        self.lockPoint = True
        mdate = datetime.datetime.fromtimestamp(self.currentDataPoint.trueDate/1000).strftime("%m/%d/%Y %I:%M:%S %p")
        self.fromTimeRangeSelectText.SetValue(mdate)
        self.lockPoint = False
        return


    ###########################################################################
    # Edit the statistic that is currently selected
    ###########################################################################
    def editStatisticsCb( self, event ):
        self.lockPoint = True
        dlg = wx.TextEntryDialog( self, 
                                  "Please enter in new value",
                                  "Modify " + self.currentPlot.tableColumn + " Statistic",
                                  str(self.currentDataPoint.value),
                                  style=wx.OK|wx.CANCEL )
        retval = dlg.ShowModal()
        if ( retval == 5100 ):
            newValue = dlg.GetValue()
            # Update the values
            if ( eval(newValue) != self.currentDataPoint.value ):
                self.currentDataPoint.value = eval(newValue)
                index = int(self.currentDataPoint.index) - 1
                pp = self.currentPlot.plotPoints[index]
                pp2 = (pp[0], float(eval(newValue)))
                self.currentPlot.plotPoints[index] = pp2
                self.plot.Draw( self.produceGraph( "" ) )
                # Now write to DB.
                tableLabel = self.currentPlot.table
                db = tableLabel.split()[1][1:-1]
                table = self.currentPlot.table.split()[0]
                objId = self.objectId
                if ( "workload" in table ):
                    objId = self.workloadId
                elif ("objectstore" in table):
                    objId = self.volumeObjectStoreMappingId
                if ( ":" in db ):
                    db = tableLabel.split()[1][1:-1].split(":")[0]
                    objId = tableLabel.split()[1][1:-1].split(":")[2]
                timeColumn = "time"
                if ("history" in table):
                    timeColumn = "periodEndTime"
                cmd = "update " + db + "." + table + " set " + self.currentPlot.tableColumn + "=" + str(newValue) + " where objid=" + str(objId) + " and " + timeColumn + "=" + str(self.currentDataPoint.trueDate)
                self.parent.executeNoResult( cmd )

        self.lockPoint = False
        return

    def OnMotion(self, event):
        # If not plots, nothing to do.
        if ( len(self.plots.values()) == 0 ): return

        #show closest point (when enbled)
        if self.plot.GetEnablePointLabel() == True:

            #make up dict with info for the pointLabe
            #I've decided to mark the closest point on the closest curve
            dlsts = self.plot.GetClosestPoints( self.plot.GetXY(event), pointScaled= True)
            print(dlsts)
            dlst= self.plot.GetClosetPoint( self.plot.GetXY(event), pointScaled= True)
            if dlst != []:    #returns [] if none
                curveNum, legend, pIndex, pointXY, scaledXY, distance = dlst
                #make up dictionary to pass to my user function (see DrawPointLabel) 
                mDataDict= {"curveNum":curveNum, "legend":legend, "pIndex":pIndex,\
                            "pointXY":pointXY, "scaledXY":scaledXY}
                #pass dict to update the pointLabel
                self.plot.UpdatePointLabel(mDataDict)
        event.Skip()           #go to next handler
        return

    def zoomCheckBoxCallBack(self, event): # wxGlade: MyFrame.<event_handler>
        if ( self.dragCheckBox.IsChecked() ):
            self.dragCheckBox.SetValue(False)
            self.plot.SetEnableDrag(False)
        self.plot.SetEnableZoom(event.IsChecked())
        event.Skip()
        return

    def dragCheckBoxCallBack(self, event): # wxGlade: MyFrame.<event_handler>
        if ( self.zoomCheckBox.IsChecked() ):
            self.zoomCheckBox.SetValue(False)
            self.plot.SetEnableZoom(False)
        self.plot.SetEnableDrag(event.IsChecked())
        event.Skip()
        return

    def gridCheckBoxCallBack(self, event): # wxGlade: MyFrame.<event_handler>
        self.plot.SetEnableGrid(event.IsChecked())
        event.Skip()
        return

    def pointLabelCheckBoxCallBack(self, event): # wxGlade: MyFrame.<event_handler>
        self.plot.SetEnablePointLabel(event.IsChecked())
        event.Skip()
        return

    def pancakeCheckBoxCallBack(self, event): # wxGlade: MyFrame.<event_handler>
        self.pancake = event.IsChecked()
        event.Skip()
        return

    def menuFileExit(self, event): # wxGlade: MyFrame.<event_handler>
        self.Close()
        event.Skip()
        return

    def menuPlotReset(self, event): # wxGlade: MyFrame.<event_handler>
        self.plot.Reset()
        event.Skip()
        return

    def menuPlotRedraw(self, event): # wxGlade: MyFrame.<event_handler>
        self.plot.Redraw()
        event.Skip()
        return

    #########################################################################################
    # Add an analysis metric
    #########################################################################################
    def menuAddMetric( self, event ):
        if ( self.analysisNode == None ):
            self.analysisNode = self.tree.AppendItem(self.root, "Metrics", image=-1 )

        dlg = wx.TextEntryDialog( self, 
                                  "Enter in a unique analysis metric name",
                                  "Modify " + self.currentPlot.tableColumn + " Statistic",
                                  "",
                                  style=wx.OK|wx.CANCEL )
        retval = dlg.ShowModal()
        if ( retval == 5100 ):
            name = dlg.GetValue()
            if ( name in self.metrics.keys() ):
                wx.MessageBox("Metric with that name already exists")
                return
        
        return

    #########################################################################################
    # Edit an analysis metric
    #########################################################################################
    def menuEditMetric( self, event ):
        print("not yet")
        return

    #########################################################################################
    # Remove an analysis metric
    #########################################################################################
    def menuRemoveMetric( self, event ):
        print("remove metric")
        return

    def menuHelpContent(self, event): # wxGlade: MyFrame.<event_handler>
        #from wx.lib.dialogs import ScrolledMessageDialog
        #about = ScrolledMessageDialog( self, __doc__, "Version 1.0" )
        #about.ShowModal()
        event.Skip()
        return

    ###########################################################################
    # This is where the main guts occur.  Must check all of the fields to make
    # sure that the user has setup all of the fields
    ###########################################################################
    def plotCharts(self, cmd, table, column, item): # wxGlade: MyFrame.<event_handler>

        fromTime = datetime.datetime.strptime(self.fromTimeRangeSelectText.GetValue(), "%m/%d/%Y %I:%M:%S %p")
        toTime = datetime.datetime.strptime(self.toTimeRangeSelectionText.GetValue(), "%m/%d/%Y %I:%M:%S %p")
        fromTime = float(time.mktime(fromTime.timetuple()))
        toTime = float(time.mktime(toTime.timetuple()))
 
        if ( table != "Policy Thresholds" and table != "Metrics" ):
            plotPoints, dataPoints, missingPoints = self.getDataPoints( cmd, table, column )
            if ( not dataPoints ): 
                self.tree.CheckItem( item, checked=False)
                return
            plot = self.plotLines( plotPoints, dataPoints, missingPoints, cmd, table, column, item )
            # If any Metric is checked, need to create for this line
            if ( self.tree.IsItemChecked(self.averageItem) ):
                sumValue = 0
                for data in plot.plotPoints:
                    sumValue = sumValue + data[1]
                avg = sumValue/len(plot.plotPoints)

                # Create the start point
                plotPoints = [ (fromTime, avg), (toTime, avg) ]
                dataPoints = {}
                dataPoints[ fromTime ] = DataPoint(avg, time.ctime(fromTime), 0.0, avg, fromTime) 
                dataPoints[ toTime ] = DataPoint(avg, time.ctime(toTime), 1.0, avg, toTime) 
                self.plotLines( plotPoints, dataPoints, [], cmd, table, plot.tableColumn + " - Average", item )
            if ( self.tree.IsItemChecked(self.maxItem) ):
                max = 0
                for data in plot.plotPoints:
                    if ( data[1] > max ):
                        max = data[1]

                # Create the start point
                plotPoints = [ (fromTime, max), (toTime, max) ]
                dataPoints = {}
                dataPoints[ fromTime ] = DataPoint(max, time.ctime(fromTime), 0.0, max, fromTime)
                dataPoints[ toTime ] = DataPoint(max, time.ctime(toTime), 1.0, max, toTime) 
                self.plotLines( plotPoints, dataPoints, [], cmd, table, plot.tableColumn + " - Max", item )
            if ( self.tree.IsItemChecked(self.minItem) ):
                min = sys.maxint
                for data in plot.plotPoints:
                    if ( data[1] < min ):
                        min = data[1]

                # Create the start point
                plotPoints = [ (fromTime, min), (toTime, min) ]
                dataPoints = {}
                dataPoints[ fromTime ] = DataPoint(min, time.ctime(fromTime), 0.0, min, fromTime) 
                dataPoints[ toTime ] = DataPoint(min, time.ctime(toTime), 1.0, min, toTime) 
                self.plotLines( plotPoints, dataPoints, [], cmd, table, plot.tableColumn + " - Min", item )


        elif ( table == "Metrics" ):
            # Need to find out what metric this is and then plot it based on all of the 
            # current plots
            # If there are no stats selected, warn user
            if ( len(self.plots) == 0 ):
                wx.MessageBox("No statistic selected, please select one first." )
                self.tree.CheckItem( item, checked=False)
                return

            for key in self.plots.keys():
                plot = self.plots[key]
                if ( column == "Average" ):
                    if ( "Max" in key or "Min" in key ): continue
                    sumValue = 0
                    for data in plot.plotPoints:
                        sumValue = sumValue + data[1]
                    avg = sumValue/len(plot.plotPoints)

                    # Create the start point
                    plotPoints = [ (fromTime, avg), (toTime, avg) ]
                    dataPoints = {}
                    dataPoints[ fromTime ] = DataPoint(avg, time.ctime(fromTime), 0.0, avg, fromTime) 
                    dataPoints[ toTime ] = DataPoint(avg, time.ctime(toTime), 1.0, avg, toTime) 
                    self.plotLines( plotPoints, dataPoints, [], cmd, table, plot.tableColumn + " - Average", item )

                elif ( column == "Max" ):
                    if ( "Average" in key or "Min" in key ): continue
                    max = 0
                    for data in plot.plotPoints:
                        if ( data[1] > max ):
                            max = data[1]

                    # Create the start point
                    plotPoints = [ (fromTime, max), (toTime, max) ]
                    dataPoints = {}
                    dataPoints[ fromTime ] = DataPoint(max, time.ctime(fromTime), 0.0, max, fromTime)
                    dataPoints[ toTime ] = DataPoint(max, time.ctime(toTime), 1.0, max, toTime) 
                    self.plotLines( plotPoints, dataPoints, [], cmd, table, plot.tableColumn + " - Max", item )
                elif ( column == "Min" ):
                    if ( "Average" in key or "Max" in key ): continue
                    min = sys.maxint
                    for data in plot.plotPoints:
                        if ( data[1] < min ):
                            min = data[1]

                    # Create the start point
                    plotPoints = [ (fromTime, min), (toTime, min) ]
                    dataPoints = {}
                    dataPoints[ fromTime ] = DataPoint(min, time.ctime(fromTime), 0.0, min, fromTime) 
                    dataPoints[ toTime ] = DataPoint(min, time.ctime(toTime), 1.0, min, toTime) 
                    self.plotLines( plotPoints, dataPoints, [], cmd, table, plot.tableColumn + " - Min", item )

                else:
                    print("Unknown metric type")
        else:
            # A Policy Threshold has 2 lines, max and min so need to create 2 data sets
            #
            # Find the policy based on the name.
            policy = None
            policyName = column.split(":")[0]
            for p in self.policies.values():
                if ( p[1] == policyName ):
                    policy = p
                    break
            if ( policy == None ):
                self.tree.CheckItem( item, checked=False)
                wx.MessageBox("Failed to find policy")
                return

            # Now find the threshold and mapping
            threshold = self.thresholdsByPolicyId[policy[0]]
            mapping = None
            for m in self.policyMappings:
                if ( m[1] == policy[0] ):
                    mapping = m
                    break
            if ( mapping == None ):
                self.tree.CheckItem( item, checked=False)
                wx.MessageBox("Failed to find mapping")
                return
  
            # Create min threshold line
            currTime = time.time()
            # Mapping 5 - start time
            # Threshold 7 - min threshold
            # Threshold 8 - max threshold
            plotPoints = [ (float(mapping[5]/1000), threshold[7]), (currTime, threshold[7]) ]
            dataPoints = {}
            newt = time.ctime(float(mapping[5]/1000))
            dataPoints[ float(mapping[5]/1000) ] = DataPoint(threshold[7], newt, 0.0, threshold[7], float(mapping[5]/1000)) 
            curr_newt = time.ctime(currTime)
            dataPoints[ currTime ] = DataPoint(threshold[8], curr_newt, 1.0, threshold[8], currTime) 
            missingPoints = []
            self.plotLines( plotPoints, dataPoints, missingPoints, cmd, table, policyName + " - min", item )

            # Now Create max threshold line
            plotPoints = [ (float(mapping[5]/1000), threshold[8]), (currTime, threshold[8]) ]
            dataPoints = {}
            dataPoints[ float(mapping[5]/1000) ] = DataPoint(threshold[8], curr_newt, 0.0, threshold[8], float(mapping[5]/1000)) 
            dataPoints[ currTime ] = DataPoint(threshold[8], newt, 1.0, threshold[8], currTime) 
            self.plotLines( plotPoints, dataPoints, missingPoints, cmd, table, policyName + " - max", item )

        return
            
    ###########################################################################
    # Actual call to plot the data.
    ###########################################################################
    def plotLines( self, plotPoints, dataPoints, missingPoints, cmd, table, column, item ):

        title = ""
        xaxis = ""
        yaxis = ""
        # Find an unused color index.
        colorIndex = None
        for index in range(len(self.colorIndexs)):
                if ( self.colorIndexs[index] == False ):
                        colorIndex = index
                        self.colorIndexs[index] = True
                        break

        #print(colorIndex)

        pD = PlotData()
        pD.cmd = cmd
        pD.item = item
        pD.treeItem = item
        pD.table = table
        pD.tableColumn = column
        pD.colorIndex = colorIndex
        pD.dataMarkerColour = plotColours[ colorIndex ]
        pD.dataMarkerType = plotMarkers[ colorIndex ]
        pD.dataLineColour = markerColours[ colorIndex ]
        pD.dataLegend = column
        pD.missingMarkerType = "triangle"
        pD.missingMarkerColour = "black"
        pD.missingLegend = "Missing Data"
        pD.title = title
        pD.xaxisLabel = xaxis
        pD.yaxisLabel = yaxis
        pD.dataPoints = dataPoints
        pD.plotPoints = plotPoints
        pD.missingPoints = missingPoints
        pD.key = column + ":" + table
         
        self.plots[pD.key] = pD

        self.plot.SetFontSizeLegend(10)
        self.plot.SetShowScrollbars(True)
        self.plot.Draw( self.produceGraph( pD.key ) )

        return pD

    ###########################################################################
    # Get the data points from the DB and parse for missing data. 
    ###########################################################################
    def getDataPoints( self, cmd, table, column ):

        # Collect the actual data points.
        dataPoints = self.parent.executeAll( cmd )
  
        if ( not dataPoints ):
            wx.MessageBox("No Data Points were found, maybe try a different table or time range?" )
            return ((), (), ())

        if (dataPoints[0] == 'Error'):
            return ((), (), ())

        index = 0
        plotData = []
        missingData = []
        prev = None
        newDataPoints = {}
        listDataPoints = list(dataPoints)
        if ( "order" in cmd ):
                listDataPoints.reverse()
                
        for next in listDataPoints:

            # Check if there are missing hours and days
            #if ( prev != None ):
            if ( False ):
                nextTuple = datetime.datetime.fromtimestamp(next[1]/1000).timetuple()
                nextHour = nextTuple[3]
                nextDay = nextTuple[2]
                nextMonth = nextTuple[1]
                nextMaxDayForMonth = days_in_month( nextMonth, nextTuple[0] ) 

                prevTuple = datetime.datetime.fromtimestamp(prev[1]/1000).timetuple()
                prevHour = prevTuple[3]
                prevDay = prevTuple[2]
                prevMonth = prevTuple[1]
                prevMaxDayForMonth = days_in_month( prevMonth, prevTuple[0] ) 

                diffDay = 0

                # Check to see if we are in between months, this will affect the day
                # diff.
                if ( nextMonth == prevMonth ): # Same month, process normally
                    dayDiff = nextDay - prevDay
                else: # Months are switching
                    # To find out the number of days we need, we need to find out how
                    # many days in the previous month
                    dayDiff = (nextDay - 1) + (prevMaxDayForMonth - prevDay)

                # Do the Hourly Diff based on the Day Diff
                hourDiff = (nextHour - prevHour) - 1
                if ( dayDiff > 0 ):
                    # Is the next hour less than the previous hour?
                    if ( nextHour < prevHour ):
                        hourDiff = (nextHour + (24 * dayDiff)) - prevHour
                    elif ( nextHour > prevHour ):
                        hourDiff = (nextHour - prevHour) + (24 * dayDiff) - 1


                if ( hourDiff > 1 ):
                    hourDiff = hourDiff * 4
                    timeTuple = datetime.datetime.fromtimestamp(prev[1]/1000).timetuple()
                    statsGap = 300
                    if ( "summary" in table ):
                        statsGap = 1200
                    for i in range(0, hourDiff):
                        index += 1
                        # Make a string of the date taking into account the requested timezone
                        floatDate = (time.mktime(timeTuple) + ((i+1)*statsGap))
                        missingData.append( (floatDate, 0.0) )
                        #plotData.append( (floatDate, 0.0) )
                        newt = time.ctime(floatDate + (self.timeDiff * (60 * 60)))
                        newDataPoints[floatDate] = DataPoint(0.0, newt, float(index), 0.0, date) 

            value, date = next
            # Hack to make the data for the cluster processing status chart
            #
            if ( column == "Minutes between collections" ):
                if ( prev != None ):
                    # We want the minutes between collections so we need
                    value = (date - prev[1])/1000/60
                else:
                    value = 0
            # Make the time a float and remove the milliseconds
            floatDate = float(date)/1000
            displayValue = value
            if ( value != None ):
                plotData.append( (floatDate, float(value)) )
            else :
                value = 0.0
                displayValue = -1
                plotData.append( (floatDate, 0.0) )
                missingData.append( (floatDate, 0.0) )
            index += 1

            # Make a string of the date taking into account the requested timezone
            t = datetime.datetime.fromtimestamp(date/1000)
            t = time.ctime(time.mktime(t.timetuple()) + (self.timeDiff * (60 * 60)))
            newDataPoints[floatDate] = DataPoint(value, t, float(index), displayValue, date)
            prev = next

        return ( plotData, newDataPoints, missingData )

    ###########################################################################
    # Given the dataPoints, produce a graph from them.
    ###########################################################################
    def produceGraph( self, key ):

        title = ""
        xaxis = ""
        yaxis = ""
        if ( key != "" ):
            a = self.plots[key].title.split()
            title = " ".join( a[:len(a)-2] )
            # Use the first plots x and y axis labels
            xaxis = self.plots[key].xaxisLabel
            yaxis = self.plots[key].yaxisLabel

        list = []
        missing = []
        for plot in self.plots.values():
            #t = plot.title.split()
            #title += " + " + t[len(t)-2] + " " + t[len(t)-1]
            goodMarkers = PolyMarker(plot.plotPoints, legend=plot.dataLegend, 
                                     colour=plot.dataMarkerColour, marker=plot.dataMarkerType, size=1)
            list.append( goodMarkers )
            #goodLines = PolyLine(plot.plotPoints, colour=plot.dataLineColour)
            goodLines = PolyLine(plot.plotPoints, colour=plot.dataMarkerColour)
            list.append( goodLines )
            missing += plot.missingPoints

        if ( missing ):
            missingMarkers = PolyMarker(missing, legend="Missing Data", colour="black", marker="triangle", size=1)
            list.append( missingMarkers )

        return PlotGraphics(list, title, xaxis, yaxis )

class PlotData:
    def init( self ):
        self.key = ""
        self.cmd = ""
        self.itme = None
        self.colorIndex = 0
        self.table = ""
        self.tableColumn = ""
        self.dataMarkerColour = ""
        self.dataMarkerType = ""
        self.dataLineColour = ""
        self.dataLegend = ""
        self.missingMarkerType = ""
        self.missingMarkerColour = ""
        self.missingLegend = ""
        self.title = ""
        self.xaxisLabel = ""
        self.yaxisLabel = ""
        self.dataPoints = ()
        self.plotPoints = ()
        self.missingPoints = ()
        return

    def __str__( self ):
        return str((self.table, self.tableColumn, self.title))

class DataPoint:
    def __init__( self, value, timestamp, index, displayValue, trueDate ):
        self.changed = False
        self.value = value
        self.displayValue = displayValue
        self.timestamp = timestamp
        self.trueDate = trueDate
        self.index = index
        return

    def __str__(self):
        return str((self.value, self.index, self.timestamp))
