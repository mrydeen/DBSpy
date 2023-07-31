#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        Graph.py
# Purpose:     The main graphing component that collects the data and does
#              the layout
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History


import wx, string, pydot, sys, time, DataPlotter, Constants, ElementGraphWindow, os
from DisplayObject import *
import ViewAndEdit

#
# Mouse key values
#

mouseLeftDown    = wx.EVT_LEFT_DOWN.typeId
mouseLeftUp      = wx.EVT_LEFT_UP.typeId
mouseRightDown   = wx.EVT_RIGHT_DOWN.typeId
mouseRightUp     = wx.EVT_RIGHT_UP.typeId
mouseMove        = wx.EVT_MOTION.typeId
mouseIn          = wx.EVT_ENTER_WINDOW.typeId
mouseOut         = wx.EVT_LEAVE_WINDOW.typeId
mouseLeftDClick  = wx.EVT_LEFT_DCLICK.typeId
mouseRightDClick = wx.EVT_RIGHT_DCLICK.typeId

if ( sys.platform != "win32" ):
    mouseLeftDown    = 10097
    mouseLeftUp      = 10098
    mouseRightDown   = 10100
    mouseRightUp     = 10102
    mouseMove        = 10103
    mouseIn          = 10104
    mouseOut         = 10105
    mouseLeftDClick  = 10106
    mouseRightDClick = 10108

DOT_PROGRAM = os.getcwd() + "\\Graphviz\\bin\\dot.exe"

DCLICK_CONNECT=1
DCLICK_EDIT=2
MAX_WIDTH=5000
MAX_HEIGHT=3000

class Graph( wx.ScrolledWindow ):
  def __init__(self, parent, id = -1, size = wx.DefaultSize):
      wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size,
                                 style=wx.SUNKEN_BORDER|wx.NO_FULL_REPAINT_ON_RESIZE)
      # Sets dimensions so that image will be larger than window,
      # and scrolling can occur.
      self.maxWidth = MAX_WIDTH
      self.maxHeight = MAX_HEIGHT
      self.font = None
      self.fontcolor = None

      self.parent = parent
      self.controlDown = False
      self.displayObjects = []
      self.displayObjectsReverse = []
      self.dclickAction = DCLICK_EDIT
      self.edges = []
      self.elementAttributes = {}
      self.elementTypes = {}
      self.topType = None
      self.prevView = None
      self.prevObjId = None
      self.parentWindow = None

      self.mouseDown = False
      self.dragObject = None
      self.dragObjects = []

      self.dotGraph = None

      # Flag used when we are connecting objects
      self.selectWindowActive = False
      self.startRect = None
      self.endRect = None
      self.overSelect = None

      # Set the size of the total window, of which only a small part
      self.SetVirtualSize((self.maxWidth, self.maxHeight))

      # Set the scrolling rate; use same value in both horizontal and
      self.EnableScrolling(True,True)
      self.SetScrollRate(10, 10)

      # Bind the key events that will be used to move the small image
      # Mouse movements
      self.Bind(wx.EVT_MOUSE_EVENTS, self.mouseEvent )
      self.Bind(wx.EVT_PAINT, self.OnPaint)
      # Keyboard events
      self.Bind(wx.EVT_CHAR, self.keyboardEvent )
      self.Bind(wx.EVT_CHAR_HOOK, self.keyboardEvent )
      self.Bind(wx.EVT_KEY_DOWN, self.keyboardEvent )
      self.Bind(wx.EVT_KEY_UP, self.keyboardEvent )
      # Scroll events
      #self.Bind(wx.evt_scrollwin_thumbrelease, self.scrollevent )
      self.Bind(wx.EVT_SCROLLWIN_THUMBTRACK, self.scrollEvent )
      self.Bind(wx.EVT_RIGHT_DOWN, self.rightDownEvent )
      self.Bind(wx.EVT_MOUSEWHEEL, self.mouseWheelScrollEvent )
    
      self.tipballoon = []

      # Initialize the buffer bitmap.  No real DC is needed at this point.
      self.buffer = wx.Bitmap(self.maxWidth, self.maxHeight)
      self.refreshGraph( True )

      return

  def setWidth( self, width ):
      self.maxWidth = eval(width)
      self.SetVirtualSize((self.maxWidth, self.maxHeight))
      self.buffer = wx.Bitmap(self.maxWidth, self.maxHeight)
      self.refreshGraph( True )
      return

  def setHeight( self, height ):
      self.maxHeight = eval(height)
      self.SetVirtualSize((self.maxWidth, self.maxHeight))
      self.buffer = wx.Bitmap(self.maxWidth, self.maxHeight)
      self.refreshGraph( True )
      return

  def createTree(self, elementId, topType, tableName):
      if ( self.topType != None ):
          # Store previous object and type
          self.prevView = self.topType
          self.prevObjId = self.elementId
      self.topType = topType
      self.elementId = elementId
      # Build the tree based on the ElementId
      self.collectTree( elementId, topType, tableName )
      self.fillTree( elementId )
      return

  #############################################################################
  # Collect the workload detail visit stats
  #############################################################################
  def collectWLStats( self, workloadId, clusterId, qosNodeRelationshipID, table, column ):

      current = long(time.time() * 1000)
      daysPast = current - ((24 * 60 * 60 * 1000))/2
      cmd = "select "+column+" from netapp_performance."+table+str(clusterId)+" where objid="+str(qosNodeRelationshipID)+ " and time > "+str(daysPast)
      stats = self.parent.executeAll( cmd )
      return stats

  #############################################################################
  # Fill in the tree 
  #############################################################################
  def fillTree( self, parentId ):
      self.edges = []
      self.displayObjects = []
      self.displayObjectsReverse = []

      self.dotGraph = pydot.Dot(graph_type='digraph', fontname="Courier")

      if ( self.topType == "IO" or self.topType == "PHYSICAL_LAYOUT" ):

          # Create Each element, go in this order
          #       disks, aggregates, volumes, luns, cifs_shares, namespaces
          for obj in self.elementTree["disks"]:
              if ( obj[self.diskInterfaceTypeIndex] != 'SSD' ):
                  self.addDisplayObject( Constants.STORAGE_ARRAY_DISK, obj[self.diskNameIndex], obj[0], obj )
              else:
                  self.addDisplayObject( Constants.STORAGE_ARRAY_DISK_SSD, obj[self.diskNameIndex], obj[0], obj )
          for obj in self.elementTree["aggregates"]:
              self.addDisplayObject( Constants.DISKGROUP, obj[self.aggrNameIndex], obj[0], obj )
          for obj in self.elementTree["volumes"]:
              self.addDisplayObject( Constants.STORAGE_ARRAY_VOLUME, obj[self.volumeNameIndex], obj[0], obj )
          for obj in self.elementTree["luns"]:
              self.addDisplayObject( Constants.STORAGE_ARRAY_LUN, obj[self.lunNameIndex], obj[0], obj )
          for obj in self.elementTree["cifs_shares"]:
              self.addDisplayObject( Constants.SHAREPOINT, obj[self.cifsPathIndex], obj[0], obj )
          for obj in self.elementTree["namespaces"]:
              self.addDisplayObject( Constants.NAMESPACE, obj[self.namespaceNameIndex], obj[0], obj )

          # Now connect each element, connect the disks to aggregates
          for obj in self.elementTree["diskmappings"]:
              self.connectDisplayObjects(obj[0], obj[1])
              self.edges.append((obj[0],int(obj[1])))
          # Connect the volumes to the aggregates
          for obj in self.elementTree["volumes"]:
              self.connectDisplayObjects(obj[0], obj[self.volumeAggrIndex])
              self.edges.append((int(obj[0]), obj[self.volumeAggrIndex]))
          # Now connect each element, connect the flexgroup to constituents
          for obj in self.elementTree["volumemappings"]:
              self.connectDisplayObjects(obj[0], obj[1])
              self.edges.append((obj[0],int(obj[1])))
          # Connect the luns to the volumes
          for obj in self.elementTree["luns"]:
              self.connectDisplayObjects(obj[0], obj[self.lunVolumeIndex])
              self.edges.append((int(obj[0]), obj[self.lunVolumeIndex]))
          # Connect the shares to the volumes
          for obj in self.elementTree["cifs_shares"]:
              self.connectDisplayObjects(obj[0], obj[self.cifsVolumeIndex])
              self.edges.append((int(obj[0]), obj[self.cifsVolumeIndex]))
          # Connect the namespaces to the volumes
          for obj in self.elementTree["namespaces"]:
              self.connectDisplayObjects(obj[0], obj[self.namespaceVolumeIndex])
              self.edges.append((int(obj[0]), obj[self.namespaceVolumeIndex]))

      elif ( self.topType == "VSERVER_MAPPINGS" ):
          # Create the vservers first
          vserverNodeMap = {}
          for vserver in self.elementTree["vservers"]:
              # Create vserver object
              self.addDisplayObject( Constants.UNACCOUNTED_WORKLOAD, vserver[4], vserver[0], vserver )
              # Go through all of the volumes to find their aggregate to then find the node
              # it is on.
              for vol in self.elementTree["volumes"]:
                  if ( vol[1] == vserver[0] ):
                      # Found a volume mapped through this vserver, now find the aggregate 
                      # and then node
                      for aggr in self.elementTree["aggregates"]:
                          if ( aggr[0] == vol[2] ):
                              # Found aggr, get the node id
                              if ( vserver[0] in vserverNodeMap.keys() ):
                                  # Make sure that node is not already in here.
                                  if ( aggr[1] not in vserverNodeMap[vserver[0]] ):
                                      vserverNodeMap[vserver[0]].append(aggr[1])
                              else:
                                  vserverNodeMap[vserver[0]] = [aggr[1]]

          # Create the arrays second
          for obj in self.elementTree["nodes"]:
              # Create array object
              self.addDisplayObject( Constants.STORAGE_ARRAY, obj[4], obj[0], obj )

          # Now connect them up
          for vserverId in vserverNodeMap.keys():
              for nodeId in vserverNodeMap[vserverId]:
                  self.connectDisplayObjects(vserverId, nodeId)
                  self.edges.append((int(vserverId), nodeId))

      elif ( self.topType == "CLUSTER_NODES" ):
          for obj in self.elementTree["nodes"]:
              # Create array object
              self.addDisplayObject( Constants.STORAGE_ARRAY, obj[4], obj[0], obj )

              # Connect nodes up
              if ( obj[6] != None ):
                  self.connectDisplayObjects(obj[0], obj[6])
                  self.edges.append((int(obj[0]), obj[6]))

      elif ( self.topType == "CLUSTER" ):
          for obj in self.elementTree["clusters"]:
              self.addDisplayObject( Constants.CLUSTER, obj[5], obj[0], obj )
 
      elif ( self.topType == "VISIT" ):
          # Normal tree should be in this order:
          #
          #    CPU_nblade
          #    DELAY_CENTER_NETWORK
          #    DELAY_CENTER_QOS_LIMIT - not in use yet
          #    DELAY_CENTER_CLUSTER_INTERCONNECT
          #    CPU_dblade
          #    CPU_dblade_background
          #    DELAY_CENTER_DISK_IO
          #    DELAY_CENTER_WALF_SUSP_CP
          #    DISK_HDD_aggr
          #    DISK_SDD
          #    

          self.networkCluster = pydot.Cluster("network", label="network")
          self.dotGraph.add_subgraph(self.networkCluster)
          self.nbladeCluster = pydot.Cluster("nblade", label="nblade")
          self.dotGraph.add_subgraph(self.nbladeCluster)
          self.qosLimitCluster = pydot.Cluster("qoslimit", label="qoslimit")
          self.dotGraph.add_subgraph(self.qosLimitCluster)
          self.interconnectCluster = pydot.Cluster("interconnect", label="interconnect")
          self.dotGraph.add_subgraph(self.interconnectCluster)
          self.dbladeCluster = pydot.Cluster("dblade", label="dblade")
          self.dotGraph.add_subgraph(self.dbladeCluster)
          self.dbladeBGCluster = pydot.Cluster("dbladeBG", label="dbladeBG")
          self.dotGraph.add_subgraph(self.dbladeBGCluster)
          self.diskIOAndWaflCluster = pydot.Cluster("diskIO", label="diskIO")
          self.dotGraph.add_subgraph(self.diskIOAndWaflCluster)
          self.diskCluster = pydot.Cluster("disk", label="disk")
          self.dotGraph.add_subgraph(self.diskCluster)
          
          nblades = self.elementTree["CPU_nblade"]
          nameIndex = self.parent.findColumnIndex("name", self.serviceCenterColumns)
          clusterIdIndex = self.parent.findColumnIndex("clusterId", self.serviceCenterColumns)
          for nblade in nblades:
              print("--------------------------------------------------------")

              # Need to get the qos_workload_node_relationship objid as it is the id into
              # the nblade and dblade stats.
              qwnr = self.parent.executeAll( "select objid from netapp_model.qos_workload_node_relationship where nodeId="+str(nblade[6])+" and workloadId="+str(self.workloadId) )[0][0]
              print(qwnr)
              nodeName = nblade[2].split(".")[1].split(":")[0]
              self.nbladeCluster.add_node(pydot.Node(nblade[0], label=str(nblade[0])))
              obj = self.addDisplayObject( Constants.NBLADE, nblade[2], nblade[0], nblade )
              obj.setStats( self.collectWLStats( nblade[0], nblade[clusterIdIndex], qwnr, "sample_qos_workload_queue_nblade_", "(SUM(cpuNBladeUtilServiceTime)+SUM(cpuNBladeResidenceTime))" ) )
              obj.setQosWorkloadNodeRelationshipId(qwnr)

              # Find the delay center network
              if ( "DELAY_CENTER_NETWORK" in self.elementTree.keys() ):
                  delayCenterNetworks = self.elementTree["DELAY_CENTER_NETWORK"]
                  for dcn in delayCenterNetworks:
                      name = dcn[2]
                      self.networkCluster.add_node(pydot.Node(dcn[0], label=str(dcn[0])))
                      if ( nodeName in name ):
                          obj = self.addDisplayObject( Constants.DC_NETWORK, dcn[2], dcn[0], dcn )
                          obj.setStats( self.collectWLStats( dcn[0], dcn[clusterIdIndex], qwnr, "sample_qos_workload_queue_nblade_", "delayNetworkWaitTime" ) )
                          obj.setQosWorkloadNodeRelationshipId(qwnr)
                          self.connectDisplayObjects(nblade[0], dcn[0])
                          self.dotGraph.add_edge(pydot.Edge(dcn[0], nblade[0]))
                          self.edges.append((nblade[0], dcn[0]))

              # Now look for the QOS LIMIT, might not be there.
              qosLimitFound = None
              if ( "DELAY_CENTER_QOS_LIMIT" in self.elementTree.keys() ):
                  qosLimits = self.elementTree["DELAY_CENTER_QOS_LIMIT"]
                  for qosLimit in qosLimits:
                      name = qosLimit[2]
                      if ( nodeName in name ):
                          self.qosLimitCluster.add_node(pydot.Node(qosLimit[0], label=str(qosLimit[0])))
                          qosLimitFound = qosLimit
                          obj = self.addDisplayObject( Constants.DC_QOS_LIMIT, qosLimit[2], qosLimit[0], qosLimit )
                          obj.setStats( self.collectWLStats( qosLimit[0], qosLimit[clusterIdIndex], qwnr, "sample_qos_workload_queue_nblade_", "delayQosLimitWaitTime" ) )
                          obj.setQosWorkloadNodeRelationshipId(qwnr)
                          self.connectDisplayObjects(nblade[0], qosLimit[0])
                          self.dotGraph.add_edge(pydot.Edge(nblade[0], qosLimit[0]))
                          self.edges.append((nblade[0], qosLimit[0]))

              # Look for the interconnect
              interconnectFound = None
              if ( "DELAY_CENTER_CLUSTER_INTERCONNECT" in self.elementTree.keys() ):
                  interconnects = self.elementTree["DELAY_CENTER_CLUSTER_INTERCONNECT"]
                  for interconnect in interconnects:
                      name = interconnect[2]
                      if ( nodeName in name ):
                          self.interconnectCluster.add_node(pydot.Node(interconnect[0], label=str(interconnect[0])))
                          interconnectFound = interconnect
                          obj = self.addDisplayObject( Constants.DC_CLUSTER_INTERCONNECT, interconnect[2], interconnect[0], interconnect )
                          obj.setStats( self.collectWLStats( interconnect[0], interconnect[clusterIdIndex], qwnr, "sample_qos_workload_queue_nblade_", "delayClusterInterconnectWaitTime" ) )
                          obj.setQosWorkloadNodeRelationshipId(qwnr)
                          if ( qosLimitFound != None ):
                              self.connectDisplayObjects(qosLimitFound[0], interconnect[0])
                              self.dotGraph.add_edge(pydot.Edge(qosLimitFound[0], interconnect[0]))
                              self.edges.append((qosLimitFound[0], interconnect[0]))
                          else:
                              self.connectDisplayObjects(nblade[0], interconnect[0])
                              self.dotGraph.add_edge(pydot.Edge(nblade[0], interconnect[0]))
                              self.edges.append((nblade[0], interconnect[0]))

              # Find the dblade
              dbladeFound = None
              dblades = self.elementTree["CPU_dblade"]
              for dblade in dblades:
                  name = dblade[2]
                  if ( nodeName in name ):
                      self.dbladeCluster.add_node(pydot.Node(dblade[0], label=str(dblade[0])))
                      dbladeFound = dblade
                      obj = self.addDisplayObject( Constants.DBLADE, dblade[2], dblade[0], dblade )
                      obj.setStats( self.collectWLStats( dblade[0], dblade[clusterIdIndex], qwnr, "sample_qos_workload_queue_dblade_", "(SUM(cpuDBladeResidenceTime)+SUM(cpuDBladeUtilServiceTime))" ) )
                      obj.setQosWorkloadNodeRelationshipId(qwnr)
                      if ( interconnectFound != None ):
                          self.connectDisplayObjects(interconnectFound[0], dblade[0])
                          self.dotGraph.add_edge(pydot.Edge(interconnectFound[0], dblade[0]))
                          self.edges.append((interconnectFound[0], dblade[0]))
                      if ( qosLimitFound != None ):
                          self.connectDisplayObjects(qosLimitFound[0], dblade[0])
                          self.dotGraph.add_edge(pydot.Edge(qosLimitFound[0], dblade[0]))
                          self.edges.append((qosLimitFound[0], dblade[0]))

                      # Make sure to connect to nblade
                      if ( qosLimitFound == None ) :
                          self.connectDisplayObjects(nblade[0], dblade[0])
                          self.dotGraph.add_edge(pydot.Edge(nblade[0], dblade[0]))
                          self.edges.append((nblade[0], dblade[0]))

              # Find the dblade background
              dbladeBackgroundFound = None
              if ( "CPU_dblade_background" in self.elementTree.keys() ):
                  dbladeBackgrounds = self.elementTree["CPU_dblade_background"]
                  for dbladeBackground in dbladeBackgrounds:
                      name = dbladeBackground[2]
                      if ( nodeName in name ):
                          self.dbladeBGCluster.add_node(pydot.Node(dbladeBackground[0], label=str(dbladeBackground[0])))
                          dbladeBackgroundFound = dbladeBackground
                          obj = self.addDisplayObject( Constants.DBLADE_BACKGROUND, dbladeBackground[2], dbladeBackground[0], dbladeBackground )
                          obj.setStats( self.collectWLStats( dbladeBackground[0], dbladeBackground[clusterIdIndex], qwnr, "sample_qos_workload_queue_dblade_", "(SUM(cpuDBladeBackgroundServiceTime)+SUM(cpuDBladeBackgroundWAFLCPServiceTime)+SUM(cpuDBladeBackgroundBackgroundDeleteServiceTime)+SUM(cpuDBladeBackgroundRAStripeXServiceTime))" ) )
                          obj.setQosWorkloadNodeRelationshipId(qwnr)
                          self.connectDisplayObjects(dbladeFound[0], dbladeBackground[0])
                          self.dotGraph.add_edge(pydot.Edge(dbladeFound[0], dbladeBackground[0]))
                          self.edges.append((dbladeFound[0], dbladeBackground[0]))

              # Find the disk IOs
              diskIOsFound = []
              dbladeBackgroundFound = None
              if ( "DELAY_CENTER_DISK_IO" in self.elementTree.keys() ):
                  diskIOs = self.elementTree["DELAY_CENTER_DISK_IO"]
                  for diskIO in diskIOs:
                      name = diskIO[2]
                      if ( nodeName in name ):
                          self.diskIOAndWaflCluster.add_node(pydot.Node(diskIO[0], label=str(diskIO[0])))
                          diskIOsFound.append(diskIO)
                          obj = self.addDisplayObject( Constants.DC_DISK_IO, diskIO[2], diskIO[0], diskIO )
                          obj.setStats( self.collectWLStats( diskIO[0], diskIO[clusterIdIndex], qwnr, "sample_qos_workload_queue_dblade_", "delayDiskIOWaitTime" ) )
                          obj.setQosWorkloadNodeRelationshipId(qwnr)
                          self.connectDisplayObjects(dbladeFound[0], diskIO[0])
                          self.dotGraph.add_edge(pydot.Edge(dbladeFound[0], diskIO[0]))
                          self.edges.append((dbladeFound[0], diskIO[0]))
                          if ( dbladeBackgroundFound != None ):
                              self.connectDisplayObjects(dbladeBackgroundFound[0], diskIO[0])
                              self.dotGraph.add_edge(pydot.Edge(dbladeBackgroundFound[0], diskIO[0]))
                              self.edges.append((dbladeBackgroundFound[0], diskIO[0]))

              # Find the Wafl susp cp
              waflCPFound = None
              if ( "DELAY_CENTER_WAFL_SUSP_CP" in self.elementTree.keys() ):
                  waflCPs = self.elementTree["DELAY_CENTER_WAFL_SUSP_CP"]
                  for waflCP in waflCPs:
                      name = waflCP[2]
                      if ( nodeName in name ):
                          self.diskIOAndWaflCluster.add_node(pydot.Node(waflCP[0], label=str(waflCP[0])))
                          waflCPFound = waflCP
                          obj = self.addDisplayObject( Constants.DC_WAFL_SUSP_CP, waflCP[2], waflCP[0], waflCP )
                          obj.setStats( self.collectWLStats( waflCP[0], waflCP[clusterIdIndex], qwnr, "sample_qos_workload_queue_dblade_", "delayWAFLSuspCPWaitTime" ) )
                          obj.setQosWorkloadNodeRelationshipId(qwnr)
                          self.connectDisplayObjects(waflCP[0], dbladeFound[0])
                          self.dotGraph.add_edge(pydot.Edge(waflCP[0], dbladeFound[0]))
                          self.edges.append((waflCP[0], dbladeFound[0]))
                          if ( dbladeBackgroundFound != None ):
                              self.connectDisplayObjects(dbladeBackgroundFound[0], waflCP[0])
                              self.dotGraph.add_edge(pydot.Edge(dbladeBackgroundFound[0], waflCP[0]))
                              self.edges.append((dbladeBackgroundFound[0], waflCP[0]))

              aggrs = self.elementTree["aggregates"]
              for aggr in aggrs:
                  #print(aggr)
                  diskDDs = self.elementTree[aggr]
                  for diskDD in diskDDs:
                      if ( nodeName in diskDD[2] ):
                          obj = None
                          self.diskCluster.add_node(pydot.Node(diskDD[0], label=str(diskDD[0])))
                          if ( "HDD" in diskDD[2] ):
                              obj = self.addDisplayObject( Constants.DISK_HDD, diskDD[2], diskDD[0], diskDD )
                              obj.setStats( self.collectWLStats( diskDD[0], diskDD[clusterIdIndex], qwnr, "sample_qos_workload_queue_dblade_", "(SUM(diskHDDBackgroundServiceTime)+SUM(diskHDDBackgroundWAFLCPServiceTime)+SUM(diskHDDBackgroundBackgroundDeleteServiceTime)+SUM(diskHDDBackgroundRAStripeXServiceTime))" ) )
                              obj.setQosWorkloadNodeRelationshipId(qwnr)
                          else:
                              obj = self.addDisplayObject( Constants.DISK_SDD, diskDD[2], diskDD[0], diskDD )
                              obj.setStats( self.collectWLStats( diskDD[0], diskDD[clusterIdIndex], qwnr, "sample_qos_workload_queue_dblade_", "(SUM(diskSSDBackgroundServiceTime)+SUM(diskSSDBackgroundWAFLCPServiceTime)+SUM(diskSSDBackgroundBackgroundDeleteServiceTime)+SUM(diskSSDBackgroundRAStripeXServiceTime))" ) )
                              obj.setQosWorkloadNodeRelationshipId(qwnr)

                          if ( len(diskIOsFound) != 0 ):
                              for dio in diskIOsFound:
                                  self.connectDisplayObjects(dio[0], diskDD[0])
                                  self.dotGraph.add_edge(pydot.Edge(dio[0], diskDD[0]))
                                  self.edges.append((dio[0], diskDD[0]))
                          if ( waflCPFound != None ):
                              self.connectDisplayObjects(waflCPFound[0], diskDD[0])
                              self.dotGraph.add_edge(pydot.Edge(waflCPFound[0], diskDD[0]))
                              self.edges.append((waflCPFound[0], diskDD[0]))
                          if ( len(diskIOsFound) == 0 and waflCPFound == None ):
                              self.connectDisplayObjects(dbladeFound[0], diskDD[0])
                              self.dotGraph.add_edge(pydot.Edge(dbladeFound[0], diskDD[0]))
                              self.edges.append((dbladeFound[0], diskDD[0]))

      if ( "DELAY_CENTER_CLUSTER_INTERCONNECT" in self.elementTree.keys() ):
          interconnects = self.elementTree["DELAY_CENTER_CLUSTER_INTERCONNECT"]
          dblades = self.elementTree["CPU_dblade"]
          for interconnect in interconnects:
              nodeName = interconnect[2].split(".")[1].split(":")[0]
              for dblade in dblades:
                  if ( nodeName in dblade[2] ): continue
                  self.connectDisplayObjects(interconnect[0], dblade[0])
                  self.dotGraph.add_edge(pydot.Edge(interconnect[0], dblade[0]))
                  self.edges.append((interconnect[0], dblade[0]))

      # Now attempt to plot the data
      self.autoPlace()

      self.refreshGraph(True)

      return

  #############################################################################
  # Main entrance to collect the specified tree type.
  #############################################################################
  def collectTree( self, elementId, topType, tableName ):
      self.elementTree = {}

      if ( topType == "IO" ):
          self.collectIOTree( elementId, tableName )
      elif ( topType == "VISIT" ):
          self.collectVisitTree( elementId, tableName )
      elif ( topType == "CLUSTER" ):
          self.collectClusterTree()
      elif ( topType == "CLUSTER_NODES" ):
          self.collectClusterNodesTree( elementId )
      elif ( topType == "VSERVER_MAPPINGS" ):
          self.collectVserverMappings( elementId )
      elif ( topType == "PHYSICAL_LAYOUT" ):
          self.collectPhysicalLayout( elementId )
      else:
          print("Invalid Topology Type:" + topType)
      return

  #############################################################################
  # Collect Physical Layout of an array.  This would be luns, volumes, 
  # aggregates, disks
  #############################################################################
  def collectPhysicalLayout( self, nodeId ):
      aggregates = []
      disks = []
      diskmappings = []
      volumes = []
      volume_consts = []
      volumemappings = []
      luns = []
      cifs_shares = []
      namespaces = []


      diskColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.disk"))
      self.diskNameIndex = self.parent.findColumnIndex("name", diskColumns)
      self.diskInterfaceTypeIndex = self.parent.findColumnIndex("interfaceType", diskColumns)
      diskAggrRelationshipColumns = ()
      diskAggrRelationshipColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.disk_aggregate_relationship"))

      self.aggrColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.aggregate"))
      self.aggrNameIndex = self.parent.findColumnIndex("name", self.aggrColumns)

      self.volumeColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.volume"))
      self.volumeNameIndex = self.parent.findColumnIndex("name", self.volumeColumns)
      self.volumeAggrIndex = self.parent.findColumnIndex("aggregateId", self.volumeColumns)
      self.volumeStyleExtendedIndex = self.parent.findColumnIndex("styleExtended", self.volumeColumns)

      self.lunColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.lun"))
      self.lunNameIndex = self.parent.findColumnIndex("path", self.lunColumns)
      self.lunVolumeIndex = self.parent.findColumnIndex("volumeId", self.lunColumns)

      if ( self.parent.version >= 7.4 ):
          self.namespaceColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.namespace"))
          self.namespaceNameIndex = self.parent.findColumnIndex("path", self.namespaceColumns)
          self.namespaceVolumeIndex = self.parent.findColumnIndex("volumeId", self.namespaceColumns)

      self.cifsColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.cifs_share"))
      self.cifsPathIndex = self.parent.findColumnIndex("path", self.cifsColumns)
      self.cifsVolumeIndex = self.parent.findColumnIndex("volumeId", self.cifsColumns)

      self.aggregates = list(self.parent.executeAll( "select * from netapp_model.aggregate where nodeId="+str(nodeId)  + " and objState='LIVE'"))
      disks = list(self.parent.executeAll( "select * from netapp_model.disk where homeNodeId="+str(nodeId) + " and containerType != 'SPARE' and objState='LIVE'"))
      diskmappings = list(self.parent.executeAll( "select aggregateId, diskId from netapp_model.disk_aggregate_relationship where diskId in (select objid from netapp_model.disk where homeNodeId="+str(nodeId)+")" ))
      for aggr in self.aggregates:
          if ( self.volumeStyleExtendedIndex != -1 ):
              volumes = volumes + list(self.parent.executeAll( "select * from netapp_model.volume where aggregateId="+str(aggr[0])  + " and objState='LIVE' and styleExtended='FLEXVOL'"))
              volume_consts = volume_consts + list(self.parent.executeAll( "select * from netapp_model.volume where aggregateId="+str(aggr[0])  + " and objState='LIVE' and styleExtended='FLEXGROUP_CONSTITUENT'"))
          else:
              volumes = volumes + list(self.parent.executeAll( "select * from netapp_model.volume where aggregateId="+str(aggr[0])  + " and objState='LIVE'"))

      # Check if any constituents
      if ( len(volume_consts) != 0 ):
          vcs = []
          for v in volume_consts:
              vcs.append( v[0] )
          tupleString = str(tuple(vcs))
          if ( len(vcs) == 1 ):
              tupleString = tupleString.replace(',','')
          flexGroups = list(self.parent.executeAll( "select * from netapp_model.volume where objId in (select flexgroupId from netapp_model.volume_flexgroup_constituent_relationship where objid in "+tupleString+")"))
          volumes += flexGroups
          volumes += volume_consts
          volumemappings = list(self.parent.executeAll( "select flexgroupId, objid from netapp_model.volume_flexgroup_constituent_relationship where objid in "+tupleString))

      for volume in volumes:
          lunList = self.parent.executeAll( "select * from netapp_model.lun where volumeId="+str(volume[0]) + " and objState='LIVE'" )
          if ( len(lunList) != 0 ):
              luns = luns + list(lunList)
          cifsList = self.parent.executeAll( "select * from netapp_model.cifs_share where volumeId="+str(volume[0]) + " and objState='LIVE'")
          if ( len(cifsList) != 0 ):
              cifs_shares = cifs_shares + list(cifsList)

          if ( self.parent.version >= 7.4 ):
              namespaceList = self.parent.executeAll( "select * from netapp_model.namespace where volumeId="+str(volume[0]) + " and objState='LIVE'" )
              if ( len(namespaceList) != 0 ):
                  namespaces = namespaces + list(namespaceList)


      self.elementTree = { "aggregates": self.aggregates,
                           "disks": disks,
                           "diskmappings": diskmappings,
                           "volumes": volumes,
                           "volumemappings": volumemappings,
                           "luns": luns,
                           "cifs_shares": cifs_shares,
                           "namespaces": namespaces}

      return

  #############################################################################
  # Collect all data needed for Vserver mappings
  #############################################################################
  def collectVserverMappings( self, clusterId ):
      # Get all of the vservers for this cluster
      cmd = "select * from netapp_model.vserver where clusterId = " + str(clusterId) + " and typeRaw != 'system' and typeRaw != 'admin' and objState='LIVE'"
      vservers = self.parent.executeAll( cmd )
      self.elementTree["vservers"] = vservers
      # Get all of the nodes for this cluster
      cmd = "select * from netapp_model.node where clusterId = " + str(clusterId)
      nodes = self.parent.executeAll( cmd )
      self.elementTree["nodes"] = nodes

      # Need the aggregates for their node information
      cmd = "select objid, nodeId from netapp_model.aggregate where clusterId = " + str(clusterId) + " and objState='LIVE'"
      aggregates = self.parent.executeAll( cmd )
      self.elementTree["aggregates"] = aggregates
      
      # Need the volumes for their aggregate information
      cmd = "select objid, vserverId, aggregateId from netapp_model.volume where clusterId = " + str(clusterId) + " and objState='LIVE'"
      volumes = self.parent.executeAll( cmd )
      self.elementTree["volumes"] = volumes

      return

  #############################################################################
  # Collect the node information for the cluster
  #############################################################################
  def collectClusterNodesTree( self, clusterId ):
      # Get all of the nodes for this cluster
      cmd = "select * from netapp_model.node where clusterId = " + str(clusterId)
      nodes = self.parent.executeAll( cmd )
      self.elementTree["nodes"] = nodes
      return

  #############################################################################
  # Collect the cluster information
  #############################################################################
  def collectClusterTree( self ):
      # Get all of the clusters
      cmd = "select * from netapp_model.cluster"
      clusters = self.parent.executeAll( cmd )
      self.elementTree["clusters"] = clusters

      return

  #############################################################################
  # Collect the VISIT Tree for a volume.
  #############################################################################
  def collectVisitTree( self, elementId, tableName ):
      # This elementId should be a volume, so we need to get the workload id
      self.workloadId = 0
      if ( self.parent.version < 7.3 ):
          cmd = "select objid from netapp_model.qos_volume_workload where volumeId="+str(elementId) + " and objState=\"LIVE\""
      else:
          cmd = "select objid from netapp_model.qos_workload where holderId="+str(elementId) + " and objState=\"LIVE\""
      self.workloadId = self.parent.executeAll( cmd )[0][0]


      # Get the column
      cmd = "show columns from netapp_model.qos_service_center"
      columns = self.parent.executeAll(cmd)

      # We need to get the service centers.  Todo this, we need to look up in the 
      # qos_workload_node_relationship table and get the node ids.  And once we have that,
      # we can look at the service centers.
      cmd = "SELECT nodeId from netapp_model.qos_workload_node_relationship where workloadId="+str(self.workloadId)+" and objState='LIVE'"
      self.nodeIds = self.parent.executeAll(cmd)
      nodeIdList = []
      for node in self.nodeIds:
          nodeIdList.append(node[0]) 
            
      cmd = "SELECT * FROM netapp_model.qos_service_center where nodeId in "+str(tuple(nodeIdList))+" and objState='LIVE'"
      self.serviceCenters = self.parent.executeAll(cmd)

      # The list contains all the aggregates across this cluster so we only want to filter down to the
      # aggregate that we are attached to.
      volumeValues = self.parent.executeAll("select * from netapp_model.volume where objid="+str(elementId))[0]
      volumeColumns = self.parent.executeAll("show columns from netapp_model.volume")
      aggregateIdIndex = self.parent.findColumnIndex("aggregateId", self.parent.reformatColumns(volumeColumns))
      aggregateId = volumeValues[aggregateIdIndex]
      # If this is a valid value, then we are good to go, otherwise this might be a flexgroup so have to grab the list of 
      # aggregates.
      aggregateNames = []
      if ( aggregateId != None ):
        aggregate = self.parent.executeAll("select * from netapp_model.aggregate where objId="+str(aggregateId))[0]
        aggregateNames.append(aggregate[4])
      else:
        # Need to find all of the constituents
        constituents = self.parent.executeAll("select objid from netapp_model.volume_flexgroup_constituent_relationship where flexgroupId="+str(volumeId))
        for c in constituents:
            volumeValues = self.parent.executeAll("select * from netapp_model.volume where objId="+str(c))[0]
            aggregateId = volumeValues[aggregateIdIndex]
            aggregate = self.parent.executeAll("select * from netapp_model.aggregate where objId="+str(aggregateId))[0]
            aggregateNames.append(aggregate[4])

      # Walk each workload detail and sort by its service center name.
      aggrs = []
      self.serviceCenterColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.qos_service_center"))
      nameIndex = self.parent.findColumnIndex("name", self.serviceCenterColumns)
      for sc in self.serviceCenters:
          name = sc[nameIndex]
          if ( "HDD" in name or "SDD" in name):
              found = False
              for a in aggregateNames:
                  scAggrName = name
                  if ( a == scAggrName ): 
                      found = True
                      break
              if ( found == False ): continue      

              if ( name not in aggrs ):
                  aggrs.append( name )
          elif ( "DELAY_CENTER_DISK_IO" in name ):
              name = "DELAY_CENTER_DISK_IO"

          if ( not name in self.elementTree.keys() ):
              self.elementTree[ name ] = [ sc ]
          else:
              self.elementTree[ name ].append(sc)

      self.elementTree["aggregates"] = aggrs
      return

  #############################################################################
  # Collect the IO tree for a particular element
  #############################################################################
  def collectIOTree( self, elementId, tableName ):
      aggregates = []
      disks = []
      volumes = []
      diskmappings = []
      volume_consts = []
      volumemappings = []
      luns = []
      cifs_shares = []
      namespaces = []

      diskColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.disk"))
      self.diskNameIndex = self.parent.findColumnIndex("name", diskColumns)
      self.diskInterfaceTypeIndex = self.parent.findColumnIndex("interfaceType", diskColumns)
      diskAggrRelationshipColumns = ()
      diskAggrRelationshipColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.disk_aggregate_relationship"))

      self.aggrColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.aggregate"))
      self.aggrNameIndex = self.parent.findColumnIndex("name", self.aggrColumns)

 
      self.aggrColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.aggregate"))
      self.aggrNameIndex = self.parent.findColumnIndex("name", self.aggrColumns)

      self.volumeColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.volume"))
      self.volumeNameIndex = self.parent.findColumnIndex("name", self.volumeColumns)
      self.volumeAggrIndex = self.parent.findColumnIndex("aggregateId", self.volumeColumns)
      self.volumeStyleExtendedIndex = self.parent.findColumnIndex("styleExtended", self.volumeColumns)

      self.lunColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.lun"))
      self.lunNameIndex = self.parent.findColumnIndex("path", self.lunColumns)
      self.lunVolumeIndex = self.parent.findColumnIndex("volumeId", self.lunColumns)

      if ( self.parent.version >= 7.4 ):
          self.namespaceColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.namespace"))
          self.namespaceNameIndex = self.parent.findColumnIndex("path", self.namespaceColumns)
          self.namespaceVolumeIndex = self.parent.findColumnIndex("volumeId", self.namespaceColumns)

      self.cifsColumns = self.parent.reformatColumns(self.parent.executeAll("show columns from netapp_model.cifs_share"))
      self.cifsPathIndex = self.parent.findColumnIndex("path", self.cifsColumns)
      self.cifsVolumeIndex = self.parent.findColumnIndex("volumeId", self.cifsColumns)

      if ( tableName == "netapp_model.aggregate" ):
          self.aggregates = list(self.parent.executeAll( "select * from netapp_model.aggregate where objid="+str(elementId) ))
          disks = list(self.parent.executeAll( "select * from netapp_model.disk where netapp_model.disk.objid in (select diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId="+str(elementId)+")" ))
          diskmappings = list(self.parent.executeAll( "select aggregateId, diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId="+str(elementId) ))
          if ( self.volumeStyleExtendedIndex != -1 ):
              volumes = list(self.parent.executeAll( "select * from netapp_model.volume where aggregateId="+str(elementId)  + " and objState='LIVE' and styleExtended='FLEXVOL'"))
              volume_consts = volume_consts + list(self.parent.executeAll( "select * from netapp_model.volume where aggregateId="+str(elementId)  + " and objState='LIVE' and styleExtended='FLEXGROUP_CONSTITUENT'"))
          else:
              volumes = list(self.parent.executeAll( "select * from netapp_model.volume where aggregateId="+str(elementId)  + " and objState='LIVE'"))
          # Check if any constituents
          if ( len(volume_consts) != 0 ):
              vcs = []
              for v in volume_consts:
                  vcs.append( v[0] )
              tupleString = str(tuple(vcs))
              if ( len(vcs) == 1 ):
                  tupleString = tupleString.replace(',','')
              flexGroups = list(self.parent.executeAll( "select * from netapp_model.volume where objId in (select flexgroupId from netapp_model.volume_flexgroup_constituent_relationship where objid in "+tupleString+")"))
              volumes += flexGroups
              volumes += volume_consts
              volumemappings = list(self.parent.executeAll( "select flexgroupId, objid from netapp_model.volume_flexgroup_constituent_relationship where objid in "+tupleString))

          for volume in volumes:
              val = self.parent.executeAll( "select * from netapp_model.lun where volumeId="+str(volume[0]))
              if ( len(val) != 0 ):
                  for lun in val:
                      luns.append(lun)
              val = self.parent.executeAll( "select * from netapp_model.cifs_share where volumeId="+str(volume[0]))
              if ( len(val) != 0 ):
                  for share in val:
                      cifs_shares.append( share )
              if ( self.parent.version >= 7.4 ):
                  val = self.parent.executeAll( "select * from netapp_model.namespace where volumeId="+str(volume[0]))
                  if ( len(val) != 0 ):
                      for namespace in val:
                          namespaces.append( namespace )
      elif ( tableName == "netapp_model.disk" ):
          disks = list(self.parent.executeAll( "select * from netapp_model.disk where objid="+str(elementId) ))
          # should be only one disk
          disk = disks[0]
          self.aggregates = ()
          self.aggregates = list(self.parent.executeAll( "select * from netapp_model.aggregate where objid in (select aggregateId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.diskId = "+str(elementId)+")" ))
          diskmappings = [[self.aggregates[0][0], elementId]]
          if ( self.volumeStyleExtendedIndex != -1 ):
              volumes = list(self.parent.executeAll( "select * from netapp_model.volume where aggregateId="+str(self.aggregates[0][0])  + " and objState='LIVE' and styleExtended='FLEXVOL'"))
          else:
              volumes = list(self.parent.executeAll( "select * from netapp_model.volume where aggregateId="+str(self.aggregates[0][0])  + " and objState='LIVE'"))
          volume_consts = volume_consts + list(self.parent.executeAll( "select * from netapp_model.volume where aggregateId="+str(self.aggregates[0][0])  + " and objState='LIVE' and styleExtended='FLEXGROUP_CONSTITUENT'"))
          # Check if any constituents
          if ( len(volume_consts) != 0 ):
              vcs = []
              for v in volume_consts:
                  vcs.append( v[0] )
              tupleString = tuple(vcs).toString()
              if ( len(vcs) == 1 ):
                  tupleString = tupleString.replace(',','')
              flexGroups = list(self.parent.executeAll( "select * from netapp_model.volume where objId in (select flexgroupId from netapp_model.volume_flexgroup_constituent_relationship where objid in "+tupleString+")"))
              volumes += flexGroups
              volumes += volume_consts
              volumemappings = list(self.parent.executeAll( "select flexgroupId, objid from netapp_model.volume_flexgroup_constituent_relationship where objid in "+tupleString))
          for volume in volumes:
              val = self.parent.executeAll( "select * from netapp_model.lun where volumeId="+str(volume[0]))
              if ( len(val) != 0 ):
                  for lun in val:
                      luns.append(lun)
              val = self.parent.executeAll( "select * from netapp_model.cifs_share where volumeId="+str(volume[0]))
              if ( len(val) != 0 ):
                  for share in val:
                      cifs_shares.append( share )
              if ( self.parent.version >= 7.4 ):
                  val = self.parent.executeAll( "select * from netapp_model.namespace where volumeId="+str(volume[0]))
                  if ( len(val) != 0 ):
                      for namespace in val:
                          namespaces.append( namespace )
      elif ( tableName == "netapp_model.volume" ):
          volumes = list(self.parent.executeAll( "select * from netapp_model.volume where objid="+str(elementId) ))
          volume = volumes[0]
          if ( self.volumeStyleExtendedIndex == -1 or
               volume[self.volumeStyleExtendedIndex] == "FLEXVOL" or
               volume[self.volumeStyleExtendedIndex] == "FLEXGROUP_CONSTITUENT" ):
              # This is a FLEXVOL or FLEXGROUP_CONSTITUENT
              self.aggregates = list(self.parent.executeAll( "select * from netapp_model.aggregate where objid="+str(volume[self.volumeAggrIndex]) ))
              disks = list(self.parent.executeAll( "select * from netapp_model.disk where netapp_model.disk.objid in (select diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId="+str(self.aggregates[0][0])+")" ))
              diskmappings = list(self.parent.executeAll( "select aggregateId, diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId="+str(self.aggregates[0][0]) ))
              if ( self.volumeStyleExtendedIndex != -1 and 
                   volume[self.volumeStyleExtendedIndex] != "FLEXGROUP_CONSTITUENT" ):
                  val = self.parent.executeAll( "select * from netapp_model.lun where volumeId="+str(volume[0]))
                  if ( len(val) != 0 ):
                      for lun in val:
                          luns.append(lun)
                  val = self.parent.executeAll( "select * from netapp_model.cifs_share where volumeId="+str(volume[0]))
                  if ( len(val) != 0 ):
                      for share in val:
                          cifs_shares.append( share )
                  if ( self.parent.version >= 7.4 ):
                      val = self.parent.executeAll( "select * from netapp_model.namespace where volumeId="+str(volume[0]))
                      if ( len(val) != 0 ):
                          for namespace in val:
                              namespaces.append( namespace )
              else:
                  if ( self.volumeStyleExtendedIndex != -1 ):
                      # Need to collect the flex group of this constituent
                      flexGroup = list(self.parent.executeAll( "select * from netapp_model.volume where objId in (select flexgroupId from netapp_model.volume_flexgroup_constituent_relationship where objid="+str(volume[0])+")"))
                      volumes += flexGroup
                      volumemappings = [[flexGroup[0][0], volume[0]]]
          else:
              # This is a FLEXGROUP
              # Collect the volume constituents first.  This is in the "volume_flexgroup_constituent_relationship" table
              # This will return a list of integers.  Need to make into a touple and collect
              volumemappings = self.parent.executeAll( "select flexgroupId, objid from netapp_model.volume_flexgroup_constituent_relationship where flexgroupId="+str(elementId))
              print(volumemappings)
              consts = self.parent.executeAll( "select objid from netapp_model.volume_flexgroup_constituent_relationship where flexgroupId="+str(elementId))
              clist = []
              for c in consts:
                  clist.append(c[0])
              conts = tuple(clist)
              volumeConsts = list(self.parent.executeAll( "select * from netapp_model.volume where objid in " + str(conts)))
              volumes += volumeConsts
              # Now need to collect all the aggregates for each of the volumes
              aggrlist = []
              for c in volumeConsts:
                  if ( c[self.volumeAggrIndex] not in aggrlist ):
                      aggrlist.append( c[self.volumeAggrIndex] )
              aggrTup = str(tuple( aggrlist ))
              if ( len(aggrlist) == 1 ):
                  aggrTup = aggrTup.replace(",","")
              self.aggregates = list(self.parent.executeAll( "select * from netapp_model.aggregate where objid in "+aggrTup))
              # Now get all of the disks
              disks = list(self.parent.executeAll( "select * from netapp_model.disk where netapp_model.disk.objid in (select diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId in "+aggrTup+")" ))
              diskmappings = list(self.parent.executeAll( "select aggregateId, diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId in "+aggrTup ))
              val = self.parent.executeAll( "select * from netapp_model.lun where volumeId="+str(volume[0]) )
              if ( len(val) != 0 ):
                  for lun in val:
                      luns.append(lun)
              val = self.parent.executeAll( "select * from netapp_model.cifs_share where volumeId="+str(volume[0]))
              if ( len(val) != 0 ):
                  for share in val:
                      cifs_shares.append( share )
              if ( self.parent.version >= 7.4 ):
                  val = self.parent.executeAll( "select * from netapp_model.namespace where volumeId="+str(volume[0]))
                  if ( len(val) != 0 ):
                      for namespace in val:
                          namespaces.append( namespace )

      elif ( tableName == "netapp_model.namespace" ):
          namespaces = list(self.parent.executeAll( "select * from netapp_model.namespace where objid="+str(elementId)))
          namespace = namespaces[0]
          volumes = list(self.parent.executeAll( "select * from netapp_model.volume where objid="+str(namespace[self.namespaceVolumeIndex]) ))
          volume = volumes[0]
          if ( volume[self.volumeStyleExtendedIndex] != "FLEXGROUP" ):
              self.aggregates = list(self.parent.executeAll( "select * from netapp_model.aggregate where objid="+str(volume[self.volumeAggrIndex]) ))
              disks = list(self.parent.executeAll( "select * from netapp_model.disk where netapp_model.disk.objid in (select diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId="+str(self.aggregates[0][0])+")" ))
              diskmappings = list(self.parent.executeAll( "select aggregateId, diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId="+str(self.aggregates[0][0]) ))
          else:
              # Collect the volume constituents first.  This is in the "volume_flexgroup_constituent_relationship" table
              # This will return a list of integers.  Need to make into a touple and collect
              volumemappings = self.parent.executeAll( "select flexgroupId, objid from netapp_model.volume_flexgroup_constituent_relationship where flexgroupId="+str(elementId))
              consts = self.parent.executeAll( "select objid from netapp_model.volume_flexgroup_constituent_relationship where flexgroupId="+str(elementId))
              clist = []
              for c in consts:
                  clist.append(c[0])
              conts = tuple(clist)
              self.volumeConst = list(self.parent.executeAll( "select * from netapp_model.volume where objid in " + str(conts)))
              # Now need to collect all the aggregates for each of the volumes
              aggrlist = []
              for c in self.volumeConst:
                  if ( c[self.volumeAggrIndex] not in aggrlist ):
                      aggrlist.append( c[self.volumeAggrIndex] )

              aggrTup = str(tuple( aggrlist ))
              if ( len(aggrlist) == 1 ):
                  aggrTup = aggrTup.replace(",","")
              self.aggregates = list(self.parent.executeAll( "select * from netapp_model.aggregate where objid in "+aggrTup))
              # Now get all of the disks
              disks = list(self.parent.executeAll( "select * from netapp_model.disk where netapp_model.disk.objid in (select diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId in "+aggrTup+")" ))
              diskmappings = list(self.parent.executeAll( "select aggregateId, diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId in "+aggrTup+")" ))

      elif ( tableName == "netapp_model.lun" ):
          luns = list(self.parent.executeAll( "select * from netapp_model.lun where objid="+str(elementId)))
          lun = luns[0]
          volumes = list(self.parent.executeAll( "select * from netapp_model.volume where objid="+str(lun[self.lunVolumeIndex]) ))
          volume = volumes[0]
          if ( volume[self.volumeStyleExtendedIndex] != "FLEXGROUP" ):
              self.aggregates = list(self.parent.executeAll( "select * from netapp_model.aggregate where objid="+str(volume[self.volumeAggrIndex]) ))
              disks = list(self.parent.executeAll( "select * from netapp_model.disk where netapp_model.disk.objid in (select diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId="+str(self.aggregates[0][0])+")" ))
              diskmappings = list(self.parent.executeAll( "select aggregateId, diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId="+str(self.aggregates[0][0]) ))
          else:
              # Collect the volume constituents first.  This is in the "volume_flexgroup_constituent_relationship" table
              # This will return a list of integers.  Need to make into a touple and collect
              volumemappings = self.parent.executeAll( "select flexgroupId, objid from netapp_model.volume_flexgroup_constituent_relationship where flexgroupId="+str(elementId))
              consts = self.parent.executeAll( "select objid from netapp_model.volume_flexgroup_constituent_relationship where flexgroupId="+str(elementId))
              clist = []
              for c in consts:
                  clist.append(c[0])
              conts = tuple(clist)
              self.volumeConst = list(self.parent.executeAll( "select * from netapp_model.volume where objid in " + str(conts)))
              # Now need to collect all the aggregates for each of the volumes
              aggrlist = []
              for c in self.volumeConst:
                  if ( c[self.volumeAggrIndex] not in aggrlist ):
                      aggrlist.append( c[self.volumeAggrIndex] )

              aggrTup = str(tuple( aggrlist ))
              if ( len(aggrlist) == 1 ):
                  aggrTup = aggrTup.replace(",","")
              self.aggregates = list(self.parent.executeAll( "select * from netapp_model.aggregate where objid in "+aggrTup))
              # Now get all of the disks
              disks = list(self.parent.executeAll( "select * from netapp_model.disk where netapp_model.disk.objid in (select diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId in "+aggrTup+")" ))
              diskmappings = list(self.parent.executeAll( "select aggregateId, diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId in "+aggrTup+")" ))
      elif ( tableName == "netapp_model.cifs_share" ):
          share = self.parent.executeAll( "select * from netapp_model.cifs_share where objid="+str(elementId))[0]
          cifs_shares.append( share )
          volumes = list(self.parent.executeAll( "select * from netapp_model.volume where objid="+str(share[self.cifsVolumeIndex]) ))
          volume = volumes[0]
          if ( volume[self.volumeStyleExtendedIndex] != "FLEXGROUP" ):
              self.aggregates = list(self.parent.executeAll( "select * from netapp_model.aggregate where objid="+str(volume[self.volumeAggrIndex]) ))
              disks = list(self.parent.executeAll( "select * from netapp_model.disk where netapp_model.disk.objid in (select diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId="+str(self.aggregates[0][0])+")" ))
              diskmappings = list(self.parent.executeAll( "select aggregateId, diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId="+str(self.aggregates[0][0]) ))
              val = self.parent.executeAll( "select * from netapp_model.cifs_share where volumeId="+str(volume[0]))
              if ( len(val) != 0 ):
                  for share in val:
                      cifs_shares.append( share )
          else:
              # Collect the volume constituents first.  This is in the "volume_flexgroup_constituent_relationship" table
              # This will return a list of integers.  Need to make into a touple and collect
              volumemappings = self.parent.executeAll( "select flexgroupId, objid from netapp_model.volume_flexgroup_constituent_relationship where flexgroupId="+str(elementId))
              consts = self.parent.executeAll( "select objid from netapp_model.volume_flexgroup_constituent_relationship where flexgroupId="+str(elementId))
              clist = []
              for c in consts:
                  clist.append(c[0])
              conts = tuple(clist)
              self.volumeConst = list(self.parent.executeAll( "select * from netapp_model.volume where objid in " + str(conts)))
              # Now need to collect all the aggregates for each of the volumes
              aggrlist = []
              for c in self.volumeConst:
                  if ( c[self.volumeAggrIndex] not in aggrlist ):
                      aggrlist.append( c[self.volumeAggrIndex] )

              aggrTup = str(tuple( aggrlist ))
              if ( len(aggrlist) == 1 ):
                  aggrTup = aggrTup.replace(",","")
              self.aggregates = list(self.parent.executeAll( "select * from netapp_model.aggregate where objid in "+aggrTup))
              # Now get all of the disks
              disks = list(self.parent.executeAll( "select * from netapp_model.disk where netapp_model.disk.objid in (select diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId in "+aggrTup+")" ))
              diskmappings = list(self.parent.executeAll( "select aggregateId, diskId from netapp_model.disk_aggregate_relationship where netapp_model.disk_aggregate_relationship.aggregateId in "+aggrTup+")" ))

      self.elementTree = { "aggregates": self.aggregates,
                           "disks": disks,
                           "diskmappings": diskmappings,
                           "volumes": volumes,
                           "volumemappings": volumemappings,
                           "luns": luns,
                           "cifs_shares": cifs_shares,
                           "namespaces": namespaces}
      return
    
  def saveImage( self, filename ):
      if ( self.buffer != None ):
          if ( "bmp" not in filename ):
              filename = filename + ".bmp"
          self.buffer.SaveFile( filename, wx.BITMAP_TYPE_BMP )
      return

  def saveSmallImage( self, filename ):
      myimage = self.buffer.ConvertToImage()
      smallimage = myimage.Rescale( 500, 300 )
      smallimage.SaveFile( filename, wx.BITMAP_TYPE_BMP )
      return

  def scrollWindow( self, position ):
      x = position[0]
      if ( x != 0 ):
          x += 10
      y = position[1]
      if ( y != 0 ):
          y += 10
      self.Scroll( x, y )
      self.refreshGraph( True )
      return

  def rightDownEvent( self, event ):
      objectSelected = None
      selectedCount = 0
      for object in self.displayObjects:
          if ( object.selected == True and objectSelected == None):
              objectSelected = object
              selectedCount += 1 

      if ( objectSelected == None ): return

      self.menu = wx.Menu()

      if ( self.controlDown == False ):
          id = wx.Window.NewControlId() 
          item = self.menu.Append( id, "Hide" )
          self.Bind(wx.EVT_MENU, self.hideEventCb, item )

          id = wx.Window.NewControlId() 
          item = self.menu.Append( id, "View Statistics" )
          self.Bind(wx.EVT_MENU, self.viewStatisticsCb, item)
          id = wx.Window.NewControlId() 
          item = self.menu.Append( id, "View Attributes" )
          self.Bind(wx.EVT_MENU, self.viewAttributesCb, item )

          if ( objectSelected.icontype != Constants.CLUSTER and
               objectSelected.icontype != Constants.STORAGE_ARRAY and
               objectSelected.icontype != Constants.UNACCOUNTED_WORKLOAD ):
              id = wx.Window.NewControlId() 
              item = self.menu.Append( id, "Graph From Here" )
              self.Bind(wx.EVT_MENU, self.graphHereCb, item )
          elif ( objectSelected.icontype == Constants.CLUSTER ):
              id = wx.Window.NewControlId() 
              item = self.menu.Append( id, "View Nodes" )
              self.Bind(wx.EVT_MENU, self.graphClusterNodesCb, item )
              
              id = wx.Window.NewControlId() 
              item = self.menu.Append( id, "View Vserver Mappings" )
              self.Bind(wx.EVT_MENU, self.graphVserverMappingsCb, item)
          elif ( objectSelected.icontype == Constants.STORAGE_ARRAY ):
              id = wx.Window.NewControlId() 
              item = self.menu.Append( id, "View Physical Layout" )
              self.Bind(wx.EVT_MENU, self.graphNodesPhysicalLayoutCb, item)

      pos = event.GetPosition()
      self.PopupMenu( self.menu, pos )
      return

  ###########################################################################
  # Given a list of lists, return a map.
  ###########################################################################
  def buildMap( self, attrs ):
      map = {}
      for attr in attrs:
          map[attr[0]] = attr[1]
      return map

  # Return a list of items to display
  #
  def getDisplayList( self, object ):
      displayList = []

      # For an object that was created by the user or modified by the user all the current settings
      # should be in the attributes section.  But only the ones with values were saved so need to
      # also get all the potential attributes.
      # This device is from the DB but has not been edited yet, so need to collect all the attributes.
      displayList.append(("Name", object.data[1]))
      displayList.append(("ContainerId", object.data[2]))
      displayList.append(("Key", object.data[5]))
      displayList.append(("KeyType", object.data[6]))
      displayList.append(("KeyTwo", object.data[7]))
      displayList.append(("KeyTwoType", object.data[8]))
      displayList.append(("ElementAccessHandleId", object.data[12]))
      displayList.append(("RelationshipKey", object.data[11]))
      displayList.append(("OperationalStatus", object.data[4]) )

      displayList.append(("------------------------------------------------", "------------------------------------------"))
      # Now get all the attributes possible for this object type
      allAttrsMap = {}
      attrs = self.parent.executeAll("select * from ElementAttribute where isAttribute = 1 and elementTypeId = " + str(object.icontype))
      for attr in attrs:
          allAttrsMap[attr[1]] = attr[2]
          
      # Now get all attributes currently set for this object.
          attributes = self.parent.executeAll("select * from ElementAttributeValue where elementId = " + str(object.data[0]))
      for attribute in attributes:
          attrName = allAttrsMap.pop( attribute[2] )
          displayList.append( (attrName, str(attribute[5])) )

          # Now add all the other non valued attributes
      for key in allAttrsMap.keys():
          displayList.append( (allAttrsMap[key], "" ) )

      return displayList

  def getAttribute( self, attrs, attr ):
      for a in attrs:
          if ( attr in a[0] ):
              return a[1]
      return ""

  #############################################################################
  # Draw the physical layout of a node
  #############################################################################
  def graphNodesPhysicalLayoutCb( self, event ):
      objectSelected = None
      for object in self.displayObjects:
          if ( object.selected == True ):
              objectSelected = object
              break
      if ( objectSelected == None ): return

      self.reset()
      self.createTree(objectSelected.data[0], "PHYSICAL_LAYOUT", "netapp_model.node")
      return

  #############################################################################
  # Draw the nodes and their relationships for a cluster.
  #############################################################################
  def graphClusterNodesCb(self, event):
      objectSelected = None
      for object in self.displayObjects:
          if ( object.selected == True ):
              objectSelected = object
              break
      if ( objectSelected == None ): return

      self.reset()
      self.createTree(objectSelected.data[0], "CLUSTER_NODES", "netapp_model.node")

      return

  #############################################################################
  # Draw the Vserver and Node relationships
  #############################################################################
  def graphVserverMappingsCb(self, event):
      objectSelected = None
      for object in self.displayObjects:
          if ( object.selected == True ):
              objectSelected = object
              break
      if ( objectSelected == None ): return

      self.reset()
      self.createTree(objectSelected.data[0], "VSERVER_MAPPINGS", "netapp_model.vserver")

      return

  #############################################################################
  # Graph from the perspective of another object.
  #############################################################################
  def graphHereCb(self, event):
      objectSelected = None
      for object in self.displayObjects:
          if ( object.selected == True ):
              objectSelected = object

      if ( objectSelected == None ): return

      # Need to map type to table
      print(objectSelected.icontype )
      tableName = Constants.getDBTableNameFromResource( objectSelected.icontype )

      tv = ElementGraphWindow.ElementGraphWindow(None)
      tv.setParent(self.parent)
      
      tv.setTitle( "Topology Graph - " + objectSelected.baseText )
      tv.createTree( objectSelected.id, "IO", tableName )
      tv.Show()
      return

  def hideEventCb( self, event ):
      self.hideSelected()
      return

  # Callback from the popup to explore an element.
  def exploreElementCb( self, event ):
      for object in self.displayObjects:
          if ( object.selected == True ):
              self.editObject(object)
      return

  # Callback from the popup to view the statistics of an element.
  def viewStatisticsCb( self, event ):
      for object in self.displayObjects:
          if ( object.selected == True ):
              plot = DataPlotter.DataPlotter( None, -1, "Plot Data")
              plot.setParent( self.parent )
              columns = None
              table = None
              if ( object.icontype < Constants.DC_NETWORK ):
                  columns = self.parent.executeAll( "show columns from netapp_model.volume" ) 
                  table = "netapp_model.volume"
                  if ( object.icontype == Constants.STORAGE_ARRAY_LUN ):
                      columns = self.parent.executeAll( "show columns from netapp_model.lun" ) 
                      table = "netapp_model.lun"
                  if ( object.icontype == Constants.NAMESPACE ):
                      columns = self.parent.executeAll( "show columns from netapp_model.namespace" ) 
                      table = "netapp_model.namespace"
                  elif ( object.icontype == Constants.DISKGROUP ):
                      columns = self.parent.executeAll( "show columns from netapp_model.aggregate" ) 
                      table = "netapp_model.aggregate"
                  elif ( object.icontype == Constants.STORAGE_ARRAY_DISK or object.icontype == Constants.STORAGE_ARRAY_DISK_SSD):
                      columns = self.parent.executeAll( "show columns from netapp_model.disk" ) 
                      table = "netapp_model.disk"
                  elif ( object.icontype == Constants.CLUSTER ):
                      columns = self.parent.executeAll( "show columns from netapp_model.cluster" ) 
                      table = "netapp_model.cluster"
                  elif ( object.icontype == Constants.STORAGE_ARRAY ):
                      columns = self.parent.executeAll( "show columns from netapp_model.node" ) 
                      table = "netapp_model.node"
                  elif ( object.icontype == Constants.UNACCOUNTED_WORKLOAD ):
                      columns = self.parent.executeAll( "show columns from netapp_model.vserver" ) 
                      table = "netapp_model.vserver"
                  plot.setObject( table, object.data, self.parent.reformatColumns(columns))
              else:
                  columns = self.parent.executeAll( "show columns from netapp_model.volume" ) 
                  volumeData = self.parent.executeAll( "select * from netapp_model.volume where objid="+str(self.elementId) ) 
                  table = "netapp_model.volume"
                  plot.setObject( table, volumeData[0], self.parent.reformatColumns(columns))
              plot.Show()
              continue
      return

  # Callback from the popup to view the attributes of an element.
  def viewAttributesCb( self, event ):
      for object in self.displayObjects:
          if ( object.selected == True ):
              ve = ViewAndEdit.ViewAndEditFrame(self, -1, "")
              ve.setParent(self.parent)
              columns = None
              table = None
              if ( object.icontype < Constants.DC_NETWORK ):
                  columns = self.parent.executeAll( "show columns from netapp_model.volume" ) 
                  table = "netapp_model.volume"
                  if ( object.icontype == Constants.STORAGE_ARRAY_LUN ):
                      columns = self.parent.executeAll( "show columns from netapp_model.lun" ) 
                      table = "netapp_model.lun"
                  if ( object.icontype == Constants.NAMESPACE ):
                      columns = self.parent.executeAll( "show columns from netapp_model.namespace" ) 
                      table = "netapp_model.namespace"
                  elif ( object.icontype == Constants.DISKGROUP ):
                      columns = self.parent.executeAll( "show columns from netapp_model.aggregate" ) 
                      table = "netapp_model.aggregate"
                  elif ( object.icontype == Constants.STORAGE_ARRAY_DISK or object.icontype == Constants.STORAGE_ARRAY_DISK_SSD):
                      columns = self.parent.executeAll( "show columns from netapp_model.disk" ) 
                      table = "netapp_model.disk"
                  elif ( object.icontype == Constants.CLUSTER ):
                      columns = self.parent.executeAll( "show columns from netapp_model.cluster" ) 
                      table = "netapp_model.cluster"
                  elif ( object.icontype == Constants.STORAGE_ARRAY ):
                      columns = self.parent.executeAll( "show columns from netapp_model.node" ) 
                      table = "netapp_model.node"
                  elif ( object.icontype == Constants.UNACCOUNTED_WORKLOAD ):
                      columns = self.parent.executeAll( "show columns from netapp_model.vserver" ) 
                      table = "netapp_model.vserver"
                  columns = self.parent.reformatColumns( columns ) 
                  ve.setValues(table, columns, object.data, 0, True)
              else:
                  columns = self.parent.executeAll( "show columns from netapp_model.volume" ) 
                  volumeData = self.parent.executeAll( "select * from netapp_model.volume where objid="+str(self.elementId) ) 
                  table = "netapp_model.volume"
                  columns = self.parent.reformatColumns( columns ) 
                  ve.setValues(table, columns, object.data, 0, True)
              ve.Show()
              continue
      return

  def rightUpEvent( self, event ):
      print("right up command event")
      return

  def setParentWindow( self, parentW ):
      self.parentWindow = parentW
      print("Setting Parent Window")
      return

  def setParent( self, parent ):
      self.parent = parent
      return

  #############################################################################
  # This is called to flush all of the data and start fresh.
  #############################################################################
  def reset( self ):
      self.controlDown = False
      self.displayObjects = []
      self.displayObjectsReverse = []
      self.dclickAction = DCLICK_EDIT
      self.edges = []
      self.elementAttributes = {}
      self.elementTypes = {}
      self.parentWindow = None

      self.mouseDown = False
      self.dragObject = None
      self.dragObjects = []

      self.dotGraph = None

      self.refreshGraph( True )
      return
  #
  # This function will attempt to auto place the display objects within
  # a Grid style
  #
  def autoPlace( self ):

      if ( len(self.displayObjects) == 0 ):
          return

      maxY = 0
      # Use Pydot to get the positioning information.
      if ( self.topType == "IO" or 
           self.topType == "CLUSTER" or 
           self.topType == "CLUSTER_NODES" or
           self.topType == "PHYSICAL_LAYOUT" or
           self.topType == "VSERVER_MAPPINGS" ):
          self.dotGraph = pydot.graph_from_edges(edge_list=self.edges, directed=True)
      # Set some graph attributes
      #attributes = { 'size': "19,25",
      #               'mincross': '1.0',
      #               'rankdir' : "LR" 
      #             }
      #dot.set_attributes( attributes )
      self.dotGraph.set_size("40")
      #dot.set_ratio( "auto" )
      #dot.set_ratio( "expand" )
      self.dotGraph.set_nodesep( "2.0" )
      self.dotGraph.set_sep( "2.0" )
      #dot.set_ranksep( "1.0" )
      self.dotGraph.set_remincross( "2.0" )
      self.dotGraph.set_rankdir( "LR" )
      #self.dotGraph.directed(True)
      #print(plotdata)
      #else:
      #    plotdata = dot.create(prog='fdp', format='xdot')

      if ( self.topType == "IO" or 
           self.topType == "CLUSTER_NODES" or
           self.topType == "PHYSICAL_LAYOUT" or
           self.topType == "VSERVER_MAPPINGS" ):
          #self.dotGraph.set_ranksep( "equally" )
          self.dotGraph.set_nodesep( "0.2" )
          self.dotGraph.set_sep( "0.5" )
          self.dotGraph.set_remincross( "1.0" )
          if ( self.topType == "VSERVER_MAPPINGS" or self.topType == "PHYSICAL_LAYOUT" ):
              self.dotGraph.set_nodesep( "1.0" )
              self.dotGraph.set_sep( "0.5" )
              self.dotGraph.set_remincross( "1.0" )

          # Plot it.
          plotdata = self.dotGraph.create(prog=DOT_PROGRAM, format='xdot')
          plotdata = plotdata.decode('ASCII')

          # Now parse the information.
          for data in plotdata.split(";")[3:]:
              if ( "--" not in data and "->" not in data ):
                  if ( "}" in data ): continue;
                  tokens = data.split()
                  elementId = eval(tokens[0])
                  dobject = self.findDisplayObject(elementId)
                  if ( dobject != None ):
                      pos = eval("(" + tokens[1][6:-2]+ ")")
                      #print(pos)
                      if ( pos[1] > maxY ):
                          maxY = pos[1]
                      dobject.updatePos(pos[0], pos[1])
          print(maxY)
      elif ( self.topType == "CLUSTER" ):
          # Since cluster are not connected, just need to place them.
          x = 450/len(self.displayObjects)
          y = 100
          for object in self.displayObjects:
              object.updatePos(x, y)
              x += 160
      else :
          plotdata = self.dotGraph.create(prog='dot', format='xdot')
          split =  plotdata.split(';')
          for s in split:
              if ( "_ldraw_" in s and "subgraph" not in s):
                  array = s.split()
                  #print(array)
                  elementId = long(array[0])
                  pos = (array[2].split("=")[1][:-1]).replace("\"", "")
                  posx = eval(pos.split(",")[0])
                  posy = eval(pos.split(",")[1])
                  dobject = self.findDisplayObject(elementId)
                  if ( dobject.icontype == Constants.DC_NETWORK ):
                      posx = posx - 100
                  elif ( dobject.icontype == Constants.NBLADE ):
                      posx = posx + 5
                  elif ( dobject.icontype == Constants.DC_QOS_LIMIT ):
                      posx = posx + 100
                  elif ( dobject.icontype == Constants.DC_CLUSTER_INTERCONNECT ):
                      posx = posx + 180
                  elif ( dobject.icontype == Constants.DBLADE or dobject.icontype == Constants.DBLADE_BACKGROUND ):
                      posx = posx + 220
                  elif ( dobject.icontype == Constants.DC_DISK_IO or dobject.icontype == Constants.DC_WAFL_SUSP_CP):
                      posx = posx + 300
                  elif ( dobject.icontype == Constants.DISK_HDD or dobject.icontype == Constants.DISK_SDD):
                      posx = posx + 400

                  dobject.updatePos(posx+100, posy)

      if ( maxY != 0 and maxY > 3000 ):
          self.setHeight( str(maxY+100) )
      return

  def findObjects( self ):
      dlg = wx.TextEntryDialog( self, 
                                "Please enter full or partial object name",
                                style=wx.OK|wx.CANCEL )
      retval = dlg.ShowModal()
      if ( retval == 5100 ):
        msg = dlg.GetValue()
        if ( msg != "" ):
            for object in self.displayObjects:
                if ( msg in object.text ):
                    object.select()
      self.refreshGraph( True )
      return

  def hideSelected( self ):
      for object in self.displayObjects:
          if ( object.selected == True ):
              object.hide()
      self.refreshGraph( True )
      return

  def hideLostElements( self ):
      for object in self.displayObjects:
          if ( object.data[4] != 0 ):
              object.hide()
      self.refreshGraph( True )
      return

  def hideTreeSelected( self ):
      for object in self.displayObjects:
          if ( object.selected == True ):
              self.hideObject( object.data[1][0] )
      self.refreshGraph( True )
      return

  def showAll( self ):
      for object in self.displayObjects:
          object.show()
      self.refreshGraph( True )
      self.Refresh(True)
      return

  def showDiskPartitions( self ):
      return

  def showUnaccountedWorkloads( self ):
      return

  def zoomIn( self ):
      for object in self.displayObjects:
          if (object.hideImage == True): continue
          object.zoomIn()
      self.refreshGraph( True )
      self.Refresh(True)
      return

  def zoomOut( self ):
      for object in self.displayObjects:
          if (object.hideImage == True): continue
          object.zoomOut()
      self.refreshGraph( True )
      self.Refresh(True)
      return

  def setFontAndColor( self, font, color ):
      self.font = font
      self.fontcolor = color
      # Now need to walk through all of the display object and change the Text
      # font and font color
      for object in self.displayObjects:
          object.setFontAndColor( font, color )
          object.updateText( object.text )
      self.refreshGraph( True )
      return

  def clearAll( self ):
      self.displayObjects = []
      self.displayObjectsReverse = []
      self.refreshGraph( True )
      return

  def refreshGraph( self, draw ):
      if ( draw == True ):
          self.drawImage()
      self.Refresh(False)
      return

  def findDisplayObject( self, objectId ):
      for object in self.displayObjects:
          if ( object.id == objectId ):
              return object
      return None

  def setDisplayObjects( self, displayObjects ):

      self.displayObjects = displayObjects[:]
      self.displayObjectsReverse = self.displayObjects[:]
      self.displayObjectsReverse.reverse()
      # Now attempt to plot the data
      self.autoPlace()

      self.buildElementAttributes()

      self.refreshGraph(True)
      return

  def addDisplayObject( self, icontype, text, id, data ):
      object = displayObject( icontype, text, id, data, None )
      self.displayObjects.append( object )
      self.displayObjectsReverse = self.displayObjects[:]
      self.displayObjectsReverse.reverse()
      #print("Adding Object = " + object.text, icontype)
      return object

  def OnPaint(self, event):
      dc = wx.BufferedPaintDC(self, self.buffer)
      return
  #
  # Function to redraw the images onto the screen
  #
  def drawImage(self):
      dc = wx.BufferedDC(None, self.buffer)
      dc.Clear()
      #dc.BeginDrawing()

      #
      # Draw all the objects onto the canvas
      #
      for object in self.displayObjects:
          if (object.hideImage == True): continue
          object.createImage()
          newx, newy = self.CalcScrolledPosition( object.imageX, object.imageY )
          if ( object.image == None ):
              print("object is none")
          dc.DrawBitmap(object.image, newx, newy, True)
          newx, newy = self.CalcScrolledPosition( self.displayObjects[0].imageX,
                                                  self.displayObjects[0].imageY )
      #
      # Now draw all the connecting lines between the objects.
      # 
      for object in self.displayObjects:
          if (object.hideImage == True): continue
          for conn in object.connectDownList:
              if (conn.hideImage == True): continue
              self.connectObjects( dc, object, conn )

      #
      # Is the user using a select window?
      #
      if ( (self.selectWindowActive == True) and 
           (self.startRect != None) and 
           (self.endRect != None) ):
          dc.SetPen( wx.Pen(wx.BLUE,2) )
          brush = dc.GetBrush()
          dc.SetBrush(wx.TRANSPARENT_BRUSH)
          w = self.endRect[0] - self.startRect[0]
          h = self.endRect[1] - self.startRect[1]
          dc.DrawRectangle( self.startRect[0], 
                            self.startRect[1],
                            w, h )
          dc.SetPen( wx.Pen(wx.BLACK,1) )
          dc.SetBrush(brush)

      # Draw the tool tip of attributes
      if ( len(self.tipballoon) > 0 ): 
          pos = self.tipballoon[0]
          title = self.tipballoon[1]
          messages = self.tipballoon[2]
          maxlen = self.tipballoon[3]

          dc.SetPen( wx.Pen(wx.BLUE,2) )
          brush = dc.GetBrush()
          dc.SetBrush(wx.LIGHT_GREY_BRUSH)
          # x, y, width, height
          height = len(messages) + 2
          dc.DrawRectangle( pos[0] + 5,
                pos[1] + 5,
                9 * maxlen,
                19 * height)
          dc.SetPen( wx.Pen(wx.BLACK,1) )
          dc.SetBrush(brush)

          x = pos[0] + 10
          y = pos[1] + 10
          # Now draw the text
          dc.DrawText( title, x, y )
          y = y + 16
          dc.DrawText( "-".center(len(title)+20, "-"), x, y )
          y = y + 25
          dc.SetPen( wx.Pen(wx.BLUE,2) )
          for message in messages:
              dc.DrawText( message, x, y )
              y = y + 16 

          dc.SetPen( wx.Pen(wx.BLACK,1) )

      #dc.EndDrawing()
      del dc      
      return
  #
  # Used to see when a user moves an object
  #
  def overObject( self, pos ):
      x, y = self.CalcUnscrolledPosition( pos[0], pos[1] )
      for object in self.displayObjectsReverse:
          l = object.imageX 
          t = object.imageY
          r = object.imageX+object.imageWidth
          b = object.imageY+object.imageHeight
          if ( object.icontype == Constants.CLUSTER ):
              r = object.imageX+object.imageWidth - 20
          if ( (x >= l) and 
               (x <= r) and 
               (y >= t) and 
               (y <= b) ):
              return object
      return None

  ############################################################################# 
  # If user is using a select window, need to select all of the objects
  # within the window
  ############################################################################# 
  def selectObjsInWindow( self ):
      if ( (self.startRect == None) or (self.endRect == None) ): return
      l, t = self.CalcUnscrolledPosition( self.startRect[0], self.startRect[1] )
      #l = self.startRect[0]
      #t = self.startRect[1]
      r, b = self.CalcUnscrolledPosition( self.endRect[0], self.endRect[1] )
      #r = self.endRect[0]
      #b = self.endRect[1]
      for object in self.displayObjectsReverse:
          if ( (object.imageX >= l) and 
               (object.imageX <= r) and 
               (object.imageY+30 >= t) and 
               (object.imageY+30 <= b) ):
              if ( object.select() ):
                  self.dragObjects.append( object )
          else:
              if ( object.unselect() ):
                  try:
                      self.dragObjects.remove( object )
                  except:
                      pass
      return

  ############################################################################# 
  # Function to unselect objects
  ############################################################################# 
  def deselectDragObjects( self ):
      if ( not self.dragObjects ): return False
      for object in self.dragObjects:
          object.unselect()
      self.dragObjects = []
      return True

  ############################################################################# 
  # This function takes an object id, finds the object and will walk all 
  # connected objects and display them.
  ############################################################################# 
  def hideObject( self, objectId ):
      object = self.findDisplayObject( objectId )
      if ( object == None ): return
      self.hideDownPath( object )
      self.hideUpPath( object )
      return

  def hideDownPath( self, object ):
      object.hide()
      #print("DW -> " + object.text + str(object.connectDownList) + str(object.image))
      for item in object.connectDownList:
          self.hideDownPath( item )
      return
      
  def hideUpPath( self, object ):
      object.hide()
      #print("UP -> " + object.text + str(object.connectUpList) + str(object.image))
      for item in object.connectUpList:
          self.hideUpPath( item )
      return

  ############################################################################# 
  # This function takes an object id, finds the object and will walk all 
  # connected objects and display them.
  ############################################################################# 
  def exposeObject( self, objectId ):
      object = self.findDisplayObject( objectId )
      if ( object == None ): return
      self.exposeDownPath( object )
      self.exposeUpPath( object )
      return

  def exposeDownPath( self, object ):
      object.show()
      #print("DW -> " + object.text + str(object.connectDownList) + str(object.image))
      for item in object.connectDownList:
          self.exposeDownPath( item )
      return
      
  def exposeUpPath( self, object ):
      object.show()
      #print("UP -> " + object.text + str(object.connectUpList) + str(object.image))
      for item in object.connectUpList:
          self.exposeUpPath( item )
      return

  ############################################################################# 
  # This function will walk the object within the connected path and make
  # the connecting lines red to show the relationships better
  ############################################################################# 
  def markPaths( self, object ):
      self.markDownPath( object )
      #self.markUpPath( object )
      return

  def markDownPath( self, object ):
      object.mark()
      #print(object.text)
      # Do the down list
      for item in object.connectDownList:
          self.markDownPath( item )
      return
      
  def markUpPath( self, object ):
      object.mark()
      #print(object.text)
      # Do the down list
      for item in object.connectUpList:
          self.markUpPath( item )
      return

  def unmarkPaths( self ):
      for object in self.displayObjects:
          object.unmark()
      return

  #
  # Scrolling Event
  #
  def scrollEvent( self, event ):
      if ( event.GetEventType() == wx.wxEVT_SCROLLWIN_THUMBRELEASE ):
          return
      start = self.GetViewStart()
      if ( event.GetOrientation() == 8 ):
          self.Scroll(start[0], event.GetPosition())
      else:
          self.Scroll(event.GetPosition(), start[1])
      self.refreshGraph( True )
      return

  #
  # Mouse Wheel Scrolling Event
  #
  def mouseWheelScrollEvent( self, event ):
      
      return

      #start = self.GetViewStart()
      print(event.GetPosition())
      if ( event.GetWheelRotation() > 0  ):
          # Scrolling up
          print("UP")
          self.zoomIn()
          #self.Scroll(start[0], (self.GetScrollPos(8)) - 120 )
      else:
          print("DOWN")
          self.zoomOut()
          # Scrolling down
          #self.Scroll(start[0], self.GetScrollPos( 8 ) + 120 )
     
      self.refreshGraph( True )
      return

  #
  # Keyboard Events
  #
  def keyboardEvent( self, event ):

      #print(event.ControlDown())
      if ( event.ControlDown() ):
         self.controlDown = True
         #print("Control is down")
      else:
         self.controlDown = False
         self.deselectDragObjects()
         self.dragObjects = []
         self.refreshGraph( True )
         #print("Control is up")
      return
      
  def getMax( self, a , b ):
      if ( a > b ): return a
      return b

  def popMapValue( self, map, key ):
      try:
          return map.pop(key)
      except:
          return None


  def setupBalloonTip( self, event, object ):

      # Get the position
      self.tipballoon.append(event.GetPosition())

      message = []
      maxlen = 0

      title = nameDict[object.icontype] + " : " + str(object.data[1])
      maxlen = self.getMax( maxlen, len(title) ) 
      self.tipballoon.append(title)

      m = "ID = " + str(object.data[0])
      maxlen = self.getMax( maxlen, len(m) ) 
      message.append(m)

      opState = object.data[4]
      m = "Op State = " + str(Constants.opStatus[opState])
      maxlen = self.getMax( maxlen, len(m) ) 
      message.append(m)

      m = "Container Id = " + str(object.data[2])
      maxlen = self.getMax( maxlen, len(m) ) 
      message.append(m)

      m = "Key = " + str(object.data[5])
      maxlen = self.getMax( maxlen, len(m) ) 
      message.append(m)

      m = "Key Type = " + Constants.resourceKeyTypes[object.data[6]]
      maxlen = self.getMax( maxlen, len(m) ) 
      message.append(m)

      m = "Secondary Key = " + str(object.data[7])
      maxlen = self.getMax( maxlen, len(m) ) 
      message.append(m)

      m = "Secondary Key Type = " + Constants.resourceKeyTypes[object.data[8]]
      maxlen = self.getMax( maxlen, len(m) ) 
      message.append(m)

      m = "Relationship Key = " + str(object.data[11])
      maxlen = self.getMax( maxlen, len(m) ) 
      message.append(m)

      m = "Access Handle Id = " + str(object.data[12])
      maxlen = self.getMax( maxlen, len(m) ) 
      message.append(m)

      m = "----------------- Attributes ------------------"
      maxlen = self.getMax( maxlen, len(m) ) 
      message.append(m)

      # Lets build up the attributes for this object.
      attributes = self.parent.executeAll("select * from ElementAttributeValue where elementId = " + str(object.data[0]))
      for attribute in attributes:
          if ( self.elementAttributes[attribute[2]] == "RAID Type" or self.elementAttributes[attribute[2]] == "Deprecated Raid Type" ):
              m = self.elementAttributes[attribute[2]] + " = " + Constants.raidTypes[eval(attribute[5])]
          elif ( self.elementAttributes[attribute[2]] == "subType" ):
              m = self.elementAttributes[attribute[2]] + " = " + Constants.arrayLunSubTypes[eval(attribute[5])]
          elif ( self.elementAttributes[attribute[2]] == "Application Type" ):
              m = self.elementAttributes[attribute[2]] + " = " + Constants.appTypes[eval(attribute[5])]
          elif ( self.elementAttributes[attribute[2]] == "Data Transfer Type" ):
              m = self.elementAttributes[attribute[2]] + " = " + Constants.dataTransferTypes[eval(attribute[5])]
          else:
              m = self.elementAttributes[attribute[2]] + " = " + str(attribute[5])
          maxlen = self.getMax( maxlen, len(m) ) 
          message.append(m)
#          else:
#          map = self.buildMap( object.attributes )
#          item = self.popMapValue( map, "Name" )
#              title = nameDict[object.icontype] + " : " + item
#          maxlen = self.getMax( maxlen, len(title) ) 
#              self.tipballoon.append(title)
#
#              m = "ID = " + str(object.id)
#          maxlen = self.getMax( maxlen, len(m) ) 
#              message.append(m)
#
#              #print(self.topType)
#          #print(object.data)
#          item = self.popMapValue( map, "OperationalStatus" )
#          if ( item != None and item != "" ):
#                  m = "Op State = " + str(Constants.opStatus[eval(item)])
#              maxlen = self.getMax( maxlen, len(m) ) 
#                  message.append(m)
#
#          item = self.popMapValue( map, "ContainerId" )
#          if ( item != None ):
#                  m = "Container Id = " + item
#              maxlen = self.getMax( maxlen, len(m) ) 
#                  message.append(m)
#
#          item = self.popMapValue( map, "Key" )
#          if ( item != None ):
#                  m = "Key = " + item
#              maxlen = self.getMax( maxlen, len(m) ) 
#                  message.append(m)
#
#          item = self.popMapValue( map, "KeyType" )
#          if ( item != None and item != "" ):
#                  m = "Key Type = " + Constants.resourceKeyTypes[eval(item)]
#              maxlen = self.getMax( maxlen, len(m) ) 
#                  message.append(m)
#
#          item = self.popMapValue( map, "KeyTwo" )
#          if ( item != None ):
#                  m = "Secondary Key = " + item
#              maxlen = self.getMax( maxlen, len(m) ) 
#                  message.append(m)
#
#          item = self.popMapValue( map, "KeyTwoType" )
#          if ( item != None and item != "" ):
#                  m = "Secondary Key Type = " + Constants.resourceKeyTypes[eval(item)]
#              maxlen = self.getMax( maxlen, len(m) ) 
#                  message.append(m)
#
#          item = self.popMapValue( map, "RelationshipKey" )
#          if ( item != None ):
#                  m = "Relationship Key = " + item
#              maxlen = self.getMax( maxlen, len(m) ) 
#                  message.append(m)
#
#          item = self.popMapValue( map, "ElementAccessHandleId" )
#          if ( item != None ):
#                  m = "Access Handle Id = " + item
#              maxlen = self.getMax( maxlen, len(m) ) 
#                  message.append(m)
#
#              m = "----------------- Attributes ------------------"
#          maxlen = self.getMax( maxlen, len(m) ) 
#              message.append(m)
#
          # Lets build up the attributes for this object.
#          for key in map.keys():
#          if ( key == "RAID Type" or key == "Deprecated Raid Type" ):
#                      m = key + " = " + Constants.raidTypes[eval(map[key])]
#              elif ( key == "subType" ):
#                      m = key + " = " + Constants.arrayLunSubTypes[eval(map[key])]
#              elif ( key == "Application Type" ):
#                      m = key + " = " + Constants.appTypes[eval(map[key])]
#              elif ( key == "Data Transfer Type" ):
#                      m = key + " = " + Constants.dataTransferTypes[eval(map[key])]
#                  else:
#                      m = key + " = " + str(map[key])
#              maxlen = self.getMax( maxlen, len(m) ) 
#                  message.append(m)
#
      self.tipballoon.append(message)
      self.tipballoon.append(maxlen)

      return

  def stopBalloonTip( self, event ):
      if ( self.tipballoon != None ) :
          self.tipballoon = []
      return

  #
  # Mouse Events
  #
  def mouseEvent( self, event ):
      # Check to see what type of event this is
      eventType = event.GetEventType()
      #print(eventType)
      if ( eventType == mouseMove ):
          change = False
          if ( self.selectWindowActive == True ):
              self.endRect = event.GetPosition()
              self.selectObjsInWindow()
              change = True
          elif (self.dragObject != None):
              self.stopBalloonTip( event )
              self.moveObject( event )
              change = True
          else:
              # User is just moving the mouse with out any buttons
              # pressed so just see if the mouse is over any objects
              # to change their icons as well as create tool tip.
              #
              # If the control is down, do some other stuff.
              #
              obj = self.overObject( event.GetPosition() )
              if ( self.controlDown == False ): 
                  if ( obj == None ):
                      self.stopBalloonTip( event )
                      if ( self.overSelect != None ):
                          self.overSelect.unselect()
                      else:
                          return
                  elif ( (obj != None) and (obj.selected == False) ): 
                      obj.select()
                      # Create Tool Tip.
                      #self.setupBalloonTip( event, obj )
                      if ( (self.overSelect != None) and (self.overSelect != obj) ):
                          self.overSelect.unselect()
                  else:
                      self.stopBalloonTip( event )
                      return
                  self.overSelect = obj
                  change = True
          if ( change == True ):
              self.refreshGraph( True )
      elif ( eventType == mouseLeftDown ):
          # If we are connecting, then ignore single clicks
          self.stopBalloonTip( event )
          # Need to find object mouse is on
          self.dragObject = self.overObject( event.GetPosition() )
          if ( self.controlDown == False ):
              if ( (self.dragObject != None) and (self.dragObject not in self.dragObjects) ):
                  self.dragObject.select()
                  self.markPaths( self.dragObject )
                  self.mouseDown = True
                  self.deselectDragObjects()
                  self.refreshGraph( True )
              elif ( self.dragObject in self.dragObjects ):
                  self.mouseDown = True
              else:
                  self.deselectDragObjects()
                  if ( self.selectWindowActive == False ):
                      self.selectWindowActive = True
                      self.startRect = event.GetPosition()
                      self.endRect = None
          else:
              # Control is currently down
              if ( (self.dragObject != None) ):
                  # If the object is currently selected, then unselect it
                  #print(len(self.dragObjects))
                  if ( len(self.dragObjects) < 2 ):
                      if ( not self.dragObject.isSelected() ) :
                          self.dragObject.select()
                          self.dragObjects.append( self.dragObject )
                      else:
                          self.dragObject.unselect()
                          if ( self.dragObject in self.dragObjects ):
                              self.dragObjects.remove( self.dragObject )
                  elif ( self.dragObject.isSelected() ):
                      self.dragObject.unselect()
                      if ( self.dragObject in self.dragObjects ):
                          self.dragObjects.remove( self.dragObject )

          self.refreshGraph( True )
      elif ( (eventType == mouseLeftUp) or (eventType == mouseOut) ):
          # If we are connecting, then ignore single clicks
          if ( self.selectWindowActive == True ):
              self.selectWindowActive = False
              self.startRect = None
              self.endRect = None
              self.refreshGraph( True )

          self.mouseDown = False
          if ( self.dragObject != None ):
              if ( self.dragObject not in self.dragObjects ):
                  self.dragObject.unselect()
              self.unmarkPaths()
              self.dragObject = None
              self.refreshGraph( True )
      elif ( eventType == mouseLeftDClick ):
          self.stopBalloonTip( event )
          # User wants to connect 2 display Objects
          if ( self.dclickAction == DCLICK_EDIT ):
              object = self.overObject( event.GetPosition() )
              if ( object == None ): return
              self.editObject( object )
          else:
              # Need to see if the user has double clicked on an object
              self.dragObject = self.overObject( event.GetPosition() )
              if ( self.dragObject == None ): return
              #newpos = (self.dragObject.imageX, self.dragObject.imageY)
              newpos = self.CalcScrolledPosition(self.dragObject.imageX, self.dragObject.imageY)
      return

  def editObject( self, displayObject ):
      # Get the columns
      columns = self.parent.executeAll( "show columns from Element" ) 
      temp = []
      for column in columns:
          temp.append(column[0])
      columns = temp
      element = self.parent.executeAll( "select * from Element where elementId = " + str(displayObject.id) )[0] 

      ##ev = elementView.ElementViewer(self, -1, "")
      ##ev.setParent(self.parent)
      ##ev.setSelection( columns, element )
      ##ev.Show()

      return

  def moveObject( self, event ):
      if ( self.mouseDown != True ): return
      pos =  event.GetPosition()
      unscrolledpos = self.CalcUnscrolledPosition( pos[0], pos[1] )
      if ( not self.dragObjects ):
          self.dragObject.updatePos( unscrolledpos[0], unscrolledpos[1] )
      else:
          diffx = unscrolledpos[0] - self.dragObject.imageX
          diffy = unscrolledpos[1] - self.dragObject.imageY
          for object in self.dragObjects: 
              object.updatePos( object.imageX + diffx, object.imageY + diffy )
      return

  def connectObjects( self, buffer, o1, o2 ):
      x1, y1 = self.CalcScrolledPosition( o1.imageX, o1.imageY )
      x2, y2 = self.CalcScrolledPosition( o2.imageX, o2.imageY )
      buffer.SetPen( wx.Pen(o2.lineColor,o2.lineSize) )
      buffer.DrawLine( x1, y1, x2, y2 )
      return

  def connectDisplayObjects( self, objectId1, objectId2):
      # Need to find the objects first
      object1 = self.findDisplayObject( objectId1 )
      if ( object1 == None ):
          print("Failed to find first object ", (objectId1))
          return False
      object2 = self.findDisplayObject( objectId2 )
      if ( object2 == None ):
          print("Failed to find second object ", (objectId2))
          return False
      # Now connect them
      #print("----------------------------------------------------------------")
      #print("Connecting object1 = " + object1.text + " <-> object2 = " + object2.text)
      #print("before object1 Up = " + self.strList(object1.connectUpList))
      #print("before object1 Down = " + self.strList(object1.connectDownList))
      #print("before object2 Up = " + self.strList(object2.connectUpList))
      #print("before object2 Down = " + self.strList(object2.connectDownList))
      if ( object1 not in object2.connectDownList ):
          object2.connectDownList.append( object1 )
      if ( object2 not in object1.connectUpList ):
          object1.connectUpList.append( object2 )
      #print("after object1 Up = " + self.strList(object1.connectUpList))
      #print("after object1 Down = " + self.strList(object1.connectDownList))
      #print("after object2 Up = " + self.strList(object2.connectUpList))
      #print("after object2 Down = " + self.strList(object2.connectDownList))
      return True

  def strList( self, list ):
      ret = "[ "
      for i in list:
          ret += str(i) + ", "
      ret += " ]"
      return ret
    
  def isConnected( self, objectId1, objectId2):
      # Need to find the objects first
      object1 = self.findDisplayObject( objectId1 )
      if ( object1 == None ):
          print("Failed to find first object ", (objectId1))
          return False
      object2 = self.findDisplayObject( objectId2 )
      if ( object2 == None ):
          print("Failed to find second object ", (objectId2))
          return False
      # Now see if they are connected
      if ( object1 in object2.connectDownList ): return True
      return False



class GraphWithTools(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Panel.__init__(self, *args, **kwds)
        self.mainPanel = wx.Panel(self, wx.ID_ANY)
        self.toolPanel = wx.Panel(self.mainPanel, wx.ID_ANY)
        self.backButton = wx.BitmapButton(self.toolPanel, wx.ID_ANY, wx.Bitmap(".\\images\\backButton.jpg", wx.BITMAP_TYPE_ANY))
        self.refreshButton = wx.BitmapButton(self.toolPanel, wx.ID_ANY, wx.Bitmap(".\\images\\refreshButton.jpg", wx.BITMAP_TYPE_ANY))
        self.static_line_1 = wx.StaticLine(self.mainPanel, wx.ID_ANY, style=wx.LI_VERTICAL)
        self.graph = Graph(self.mainPanel, wx.ID_ANY)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.backButtonHandler, self.backButton)
        self.Bind(wx.EVT_BUTTON, self.refreshButtonHandler, self.refreshButton)
        # end wxGlade

    def __set_properties(self):
        self.backButton.SetToolTip("Go back one level")
        self.backButton.SetSize(self.backButton.GetBestSize())
        self.refreshButton.SetToolTip("Reset the graph back to original position")
        self.refreshButton.SetSize(self.refreshButton.GetBestSize())
        return

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        toolSizer = wx.BoxSizer(wx.HORIZONTAL)
        toolSizer.Add(self.backButton, 0, wx.LEFT, 2)
        toolSizer.Add(self.refreshButton, 0, wx.LEFT | wx.RIGHT, 2)
        toolSizer.Add((20, 20), 0, 0, 0)
        self.toolPanel.SetSizer(toolSizer)
        sizer_2.Add(self.toolPanel, 0, wx.EXPAND, 0)
        sizer_2.Add(self.static_line_1, 0, wx.EXPAND, 0)
        sizer_2.Add(self.graph, 1, wx.EXPAND|wx.BOTTOM, 6)
        self.mainPanel.SetSizer(sizer_2)
        sizer_1.Add(self.mainPanel, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def backButtonHandler(self, event):  # wxGlade: MyFrame.<event_handler>
        # If we are already at the cluster view, nothing to go to.
        if ( self.graph.topType == "CLUSTER" ): return

        if ( self.graph.topType == "CLUSTER_NODES" or self.graph.topType == "VSERVER_MAPPINGS" ):
            self.reset()
            self.createTree( 0, "CLUSTER", "netapp_model.cluster")
        elif ( self.graph.topType == "PHYSICAL_LAYOUT" ):
            self.reset()
            print(self.graph.prevObjId)
            print(self.graph.prevView)
            self.createTree( self.graph.prevObjId, self.graph.prevView, "netapp_model.cluster")
        return 

    def refreshButtonHandler(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'refreshButtonHandler' not implemented!")
        event.Skip()

    def reset(self):
        self.graph.reset()
        return

    def setParent(self, parent):
        self.graph.setParent(parent)
        return

    def createTree( self, id, topType, tableName ):
        self.graph.createTree( id, topType, tableName )
        return

#class MainWindow(wx.Frame):
#    def __init__(self, parent, title):
#        wx.Frame.__init__(self, parent)

        #add position panel
#        posPnl = wx.Panel(self)
#        graph = GraphWithTools(posPnl)

#        posPnlSzr = wx.BoxSizer(wx.HORIZONTAL)
#        posPnlSzr.Add(graph, 1, wx.GROW)

#    app.MainLoop()

