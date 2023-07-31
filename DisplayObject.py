#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        DisplayObject
# Purpose:     This class is used to store information on objects that are 
#              displayed on the graphing tools.
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History


import wx
import string
import pydot
import sys
import time
import sparkplot
import os
from Constants import *

nameDict = { SERVER: "Server",
             APPLICATION: "Application",
             CLUSTER: "Cluster",
             SERVER_VOLUME: "Volume",
             SERVER_LUN: "Server LUN",
             SERVER_HBA: "Array LUN",
             STORAGE_ARRAY: "Array",
             STORAGE_ARRAY_DISK: "Disk",
             STORAGE_ARRAY_DISK_SSD: "Disk",
             STORAGE_ARRAY_RAIDSET: "Raid Set",
             STORAGE_ARRAY_LUN: "Array LUN",
             STORAGE_ARRAY_VOLUME: "Array Volume",
             NAMESPACE: "Namespace",
             STORAGE_ARRAY_CONT: "Array LUN",
             ASG: "Disk Group",
             DISKGROUP: "Disk Group",
             APP_INSTANCE : "Application",
             APP_INSTANCE2: "Application",
             APP_DATA: "Application Data",
             APP_DATA2 : "Application Data2",
             SHAREPOINT: "SharePoint",
             FCSWITCH: "Fibre Channel Switch",
             FCSWITCH_PORT: "Fibre Channel Port",
             SUBGROUP: "SubGroup",
             DISK_PARTITION: "Disk Partition",
             UNACCOUNTED_WORKLOAD: "Unaccounted Workload",

             DC_NETWORK: "Delay Center Network",
             NBLADE: "CPU NBlade",
             DC_QOS_LIMIT: "Delay Center QOS Limit",
             DC_CLUSTER_INTERCONNECT: "Delay Center Interconnect",
             DBLADE: "CPU DBlade",
             DBLADE_BACKGROUND: "CPU DBlade Background",
             DC_DISK_IO: "Delay Center Disk IO",
             DC_WAFL_SUSP_CP: "Delay Center WAFL SUSP CP",
             DISK_HDD: "Disk HDD",
             DISK_SDD: "Disk SSD",
             }
                    
ICONS = {} 
ICONS_LOADED = False

def loadIcons():
    global ICONS, ICONS_LOADED
    ICONS_LOADED = True
    ICONS = {
          DC_NETWORK: (wx.Image("./images/switchPort.ico", wx.BITMAP_TYPE_ICO), 
                            wx.Image("./images/switchPortSelected.ico", wx.BITMAP_TYPE_ICO)),
          NBLADE: (wx.Image("./images/cpu.ico", wx.BITMAP_TYPE_ICO), 
                            wx.Image("./images/cpuSelected.ico", wx.BITMAP_TYPE_ICO)),
          DC_QOS_LIMIT: (wx.Image("./images/internalWorkload.jpg", wx.BITMAP_TYPE_JPEG), 
                             wx.Image("./images/internalWorkloadSelected.jpg", wx.BITMAP_TYPE_JPEG)),
          DC_CLUSTER_INTERCONNECT: (wx.Image("./images/switch.ico", wx.BITMAP_TYPE_ICO), 
                          wx.Image("./images/switchSelected.ico", wx.BITMAP_TYPE_ICO)),
          DBLADE: (wx.Image("./images/cpu.ico", wx.BITMAP_TYPE_ICO), 
                            wx.Image("./images/cpuSelected.ico", wx.BITMAP_TYPE_ICO)),
          DBLADE_BACKGROUND: (wx.Image("./images/cpu.ico", wx.BITMAP_TYPE_ICO), 
                            wx.Image("./images/cpuSelected.ico", wx.BITMAP_TYPE_ICO)),
          DC_DISK_IO: (wx.Image("./images/internalWorkload.jpg", wx.BITMAP_TYPE_JPEG), 
                             wx.Image("./images/internalWorkloadSelected.jpg", wx.BITMAP_TYPE_JPEG)),
          DC_WAFL_SUSP_CP: (wx.Image("./images/internalWorkload.jpg", wx.BITMAP_TYPE_JPEG), 
                             wx.Image("./images/internalWorkloadSelected.jpg", wx.BITMAP_TYPE_JPEG)),
          DISK_HDD: (wx.Image("./images/asg.ico", wx.BITMAP_TYPE_ICO), 
                                    wx.Image("./images/asgSelected.ico", wx.BITMAP_TYPE_ICO)),
          DISK_SDD: (wx.Image("./images/asg.ico", wx.BITMAP_TYPE_ICO), 
                                    wx.Image("./images/asgSelected.ico", wx.BITMAP_TYPE_ICO)),

          CLUSTER: (wx.Image("./images/cluster.ico", wx.BITMAP_TYPE_ICO), 
                         wx.Image("./images/clusterSelected.ico", wx.BITMAP_TYPE_ICO)),
          
          APPLICATION: (wx.Image("./images/application.ico", wx.BITMAP_TYPE_ICO), 
                             wx.Image("./images/applicationSelected.ico", wx.BITMAP_TYPE_ICO)),
          SERVER: (wx.Image("./images/server.ico", wx.BITMAP_TYPE_ICO), 
                        wx.Image("./images/serverSelected.ico", wx.BITMAP_TYPE_ICO)),
          SERVER_VOLUME: (wx.Image("./images/volume.ico", wx.BITMAP_TYPE_ICO), 
                               wx.Image("./images/volumeSelected.ico", wx.BITMAP_TYPE_ICO)),
          SERVER_LUN: (wx.Image("./images/lun.ico", wx.BITMAP_TYPE_ICO), 
                            wx.Image("./images/lunSelected.ico", wx.BITMAP_TYPE_ICO)),
          SERVER_HBA: (wx.Image("./images/storageArrayLun.ico", wx.BITMAP_TYPE_ICO), 
                            wx.Image("./images/storageArrayLunSelected.ico", wx.BITMAP_TYPE_ICO)),
          STORAGE_ARRAY: (wx.Image("./images/array.ico", wx.BITMAP_TYPE_ICO), 
                               wx.Image("./images/arraySelected.ico", wx.BITMAP_TYPE_ICO)),
          STORAGE_ARRAY_DISK: (wx.Image("./images/disk.ico", wx.BITMAP_TYPE_ICO), 
                                    wx.Image("./images/diskSelected.ico", wx.BITMAP_TYPE_ICO)),
          STORAGE_ARRAY_DISK_SSD: (wx.Image("./images/diskSSD.ico", wx.BITMAP_TYPE_ICO), 
                                    wx.Image("./images/diskSSDSelected.ico", wx.BITMAP_TYPE_ICO)),
          STORAGE_ARRAY_RAIDSET: (wx.Image("./images/raid0.ico", wx.BITMAP_TYPE_ICO), 
                                       wx.Image("./images/raid0Selected.ico", wx.BITMAP_TYPE_ICO)),
          SHAREPOINT: (wx.Image("./images/sharePoint.ico", wx.BITMAP_TYPE_ICO), 
                             wx.Image("./images/sharePointSelected.ico", wx.BITMAP_TYPE_ICO)),
          FCSWITCH: (wx.Image("./images/switch.ico", wx.BITMAP_TYPE_ICO), 
                          wx.Image("./images/switchSelected.ico", wx.BITMAP_TYPE_ICO)),
          FCSWITCH_PORT: (wx.Image("./images/switchPort.ico", wx.BITMAP_TYPE_ICO), 
                               wx.Image("./images/switchPortSelected.ico", wx.BITMAP_TYPE_ICO)),
          NAMESPACE: (wx.Image("./images/namespace.ico", wx.BITMAP_TYPE_ICO), 
                                   wx.Image("./images/namespaceSelected.ico", wx.BITMAP_TYPE_ICO)),
          STORAGE_ARRAY_LUN: (wx.Image("./images/lun.ico", wx.BITMAP_TYPE_ICO), 
                                   wx.Image("./images/lunSelected.ico", wx.BITMAP_TYPE_ICO)),
          STORAGE_ARRAY_VOLUME: (wx.Image("./images/storageArrayLun.ico", wx.BITMAP_TYPE_ICO), 
                                   wx.Image("./images/storageArrayLunSelected.ico", wx.BITMAP_TYPE_ICO)),
          STORAGE_ARRAY_CONT: (wx.Image("./images/hba.ico", wx.BITMAP_TYPE_ICO), 
                                    wx.Image("./images/hbaSelected.ico", wx.BITMAP_TYPE_ICO)),
          APP_INSTANCE: (wx.Image("./images/appInstance.ico", wx.BITMAP_TYPE_ICO), 
                              wx.Image("./images/appInstanceSelected.ico", wx.BITMAP_TYPE_ICO)),
          APP_INSTANCE2: (wx.Image("./images/appInstance.ico", wx.BITMAP_TYPE_ICO), 
                               wx.Image("./images/appInstanceSelected.ico", wx.BITMAP_TYPE_ICO)),
          APP_DATA: (wx.Image("./images/appData.ico", wx.BITMAP_TYPE_ICO), 
                          wx.Image("./images/appDataSelected.ico", wx.BITMAP_TYPE_ICO)),
          APP_DATA2: (wx.Image("./images/appData.ico", wx.BITMAP_TYPE_ICO), 
                           wx.Image("./images/appDataSelected.ico", wx.BITMAP_TYPE_ICO)),
          DISK_PARTITION: (wx.Image("./images/diskPartition.ico", wx.BITMAP_TYPE_ICO), 
                           wx.Image("./images/diskPartitionSelected.ico", wx.BITMAP_TYPE_ICO)),
          UNACCOUNTED_WORKLOAD: (wx.Image("./images/internalWorkload.jpg", wx.BITMAP_TYPE_JPEG), 
                           wx.Image("./images/internalWorkloadSelected.jpg", wx.BITMAP_TYPE_JPEG)),
          ASG: (wx.Image("./images/asg.ico", wx.BITMAP_TYPE_ICO), 
                     wx.Image("./images/asgSelected.ico", wx.BITMAP_TYPE_ICO)),
          DISKGROUP: (wx.Image("./images/asg.ico", wx.BITMAP_TYPE_ICO), 
                     wx.Image("./images/asgSelected.ico", wx.BITMAP_TYPE_ICO)),
          SUBGROUP: (wx.Image("./images/subGroup.ico", wx.BITMAP_TYPE_ICO), 
                          wx.Image("./images/subGroupSelected.ico", wx.BITMAP_TYPE_ICO)),
          }

# These values designate where the display object was created from.
#
CREATED_FROM_DB = 1
CREATED_FROM_USER = 2
CREATED_FROM_DB_MODIFIED_BY_USER = 3

#
# A Display object is what is displayed on the graph
#
class displayObject(object):
  def __init__(self, icontype, text, id, data, trend):
      # Positioning 
      self.baseText = text
      self.text = text + " (" + str(id) + ")"
      self.image = None
      self.icontype = icontype
      self.imageWidth = 30 + (len(self.text) * 4)
      self.imageHeight = 30
      if (self.icontype == CLUSTER ):
          self.imageWidth = 50 + (len(self.text) * 4)
          self.imageHeight = 80

      self.bitmapWidth = self.imageWidth 
      self.bitmapHeight = self.imageHeight + 10
      self.imageX = 0
      self.imageY = 0
      self.id = id
      self.data = data
      self.attributes = []
      self.font = None
      self.fontcolor = None
      self.fontsize = 7
      self.scale = 0
      self.icon = None
      self.iconSelected = None
      self.selected = False
      self.connectDownList = []
      self.connectUpList = []
      self.lineColor = wx.BLACK
      self.lineSize = 1
      self.trend = trend
      self.currentIcon = None
      self.getIcon()
      self.hideImage = False
      self.sparkImage = None
      #self.createImage()

      self.createdFrom = CREATED_FROM_DB

      self.qosWorkloadNodeRelationshipId = None
      self.stats = None
      return

  def setQosWorkloadNodeRelationshipId( self, id ):
      self.qosWorkloadNodeRelationshipId = id
      return

  def getQosWorkloadNodeRelationshipId(self):
      return self.qosWorkloadNodeRelationshipId

  #############################################################################
  # This will set the stats
  #############################################################################
  def setStats( self, stats ):

      allZeros = True
      simplified = []
      for stat in stats:
          if ( stat[0] != None ):
              if ( stat[0] != 0.0 ): allZeros = False
              simplified.append(stat[0])
          else:
              simplified.append(0.0)

      if ( len(simplified) == 0 or allZeros == True ):
          simplified = [0.0, 0.0]
      elif ( len(simplified) == 1 ):
          simplified.append(0.0)

      self.stats = simplified
      data = ""
      for stat in simplified:
          s = "%.2f" % stat
          if ( data == "" ):
              data = s
          else:
              data = data + "," + s

      try:
          os.remove("spark"+str(self.id)+".png")
      except:
          pass
    
      sp = None
      sp = sparkplot.Sparkplot( input_data=data,
                                label_first_value=True,
                                label_last_value=True,
                                plot_max=True,
                                label_max=True,
                                output_file="spark"+str(self.id)+".png")
      sp.plot_sparkline()

      self.sparkImage = wx.Image("spark"+str(self.id)+".png", wx.BITMAP_TYPE_ANY)

      # Update the bitmap height so that we can account for the spark chart
      self.bitmapHeight = self.bitmapHeight + 50 

      os.remove("spark"+str(self.id)+".png")
      
      return

  def getCleanCopy( self, name, id ):
      copy = displayObject( self.icontype, name, id, self.data, self.trend )
      copy.createdFrom = self.createdFrom
      
      return copy

  def __str__(self):
      return self.text

  def setNewName( self, name ):
      self.baseText = name
      self.text = name + " (" + str(self.id) + ")"
      self.createImage()
      return

  def removeRelations( self, obj ):
      #print "------------------------"
      #print self.text
      #print "Down: "
      #for o in self.connectDownList:
              #print "   " + o.text
      #print "UP: " 
      #for o in self.connectUpList:
              #print "   " + o.text
      if ( obj in self.connectDownList ):
          #print "Down List Removing object = " + obj.text + " From my list = " + self.text
          self.connectDownList.remove(obj)
      if ( obj in self.connectUpList ):
          #print "Up List Removing object = " + obj.text + " From my list = " + self.text
          self.connectUpList.remove(obj)
      return

  def createImage( self ):
      if ( self.font == None ):
          #print "Font is nothing"
          #self.font = wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL, 0, "MS Shell Dlg 2")
          self.font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Courier New")

      if ( self.image == None ) :
          self.image = wx.Bitmap( self.bitmapWidth*(self.font.GetPointSize()/4)+(self.scale*2), 
                                  self.bitmapHeight+self.font.GetPointSize()+(self.scale*2) )
      else:
          return

      icon = None
      if ( self.selected ): 
          icon = self.iconSelected
                  
      # If we did not set an icon then set the default
      if ( icon == None ): icon = self.icon

      # If the current Icon is None, then we are in the original case.
      if ( self.currentIcon == None ): 
          self.currentIcon = icon
      elif ( self.currentIcon == icon ): 
          return
      else:
          self.currentIcon = icon
     
      #print self.currentIcon.GetMask(), self.currentIcon.HasAlpha()
      w = icon.GetWidth()
      h = icon.GetHeight()
      img = icon.Scale( w+self.scale, h+self.scale )
      offDC = wx.MemoryDC()
      offDC.SelectObject(self.image)
      offDC.SetBackground(wx.Brush(wx.Colour(2,2,2), wx.SOLID))
      offDC.Clear()

      # Determine the text to display then display with correct 
      # size
      text = self.text
      if ( self.icontype > UNACCOUNTED_WORKLOAD and self.icontype != STORAGE_ARRAY_DISK_SSD):
          nodeName = self.text.split(".")[1].split(":")[0]
          text = nodeName+"->"+nameDict[self.icontype]
          if ( self.icontype == DISK_HDD or self.icontype == DISK_SDD ):
              aggrName = self.text[9:-37]
              text = nodeName+"->"+aggrName+":"+nameDict[self.icontype]
          elif ( self.icontype == DC_DISK_IO ):
              if ( "OTHER" in self.text ):
                  text = nodeName+"->"+nameDict[self.icontype] + " Other"
              else:
                  text = nodeName+"->"+nameDict[self.icontype] + " Aggr"
          text = text+" (" + str(self.id) + ")"
      offDC.SetFont( self.font )
      if ( self.icontype != CLUSTER ):
          if ( self.icontype < DC_NETWORK and self.icontype != DISK_HDD and self.icontype != DISK_SDD ):
              offDC.DrawText( text, 0, 30+(self.scale*2) )
          else:
              offDC.DrawText( text, 0, 38+(self.scale*2) )
              
      else:
          offDC.DrawText( text, 0, 75+(self.scale*2) )

      offDC.DrawBitmap( wx.Bitmap(img), 0, 0, True )

      # If there is a spark line then draw that as well
      if ( self.sparkImage != None ):
          w = self.sparkImage.GetWidth()
          h = self.sparkImage.GetHeight()
          spark = self.sparkImage.Scale( w+self.scale, h+self.scale )
          offDC.DrawBitmap( wx.BitmapFromImage(spark), self.scale+40, self.scale-7, True )
      #offDC.DrawBitmap( wx.BitmapFromImage(self.icon), 0, 0)
    
      #-- release bitmap image from drawing context to process it further
      del offDC

      # If you want to see what the image boxes look like, comment this out.
      mask = wx.Mask(self.image, wx.Colour(2,2,2))
      self.image.SetMask(mask)
      return

  def getIcon( self ):
      # Load icons if not loaded
      if (not ICONS_LOADED):
          loadIcons()
      self.icon = ICONS[self.icontype][0]
      self.iconSelected = ICONS[self.icontype][1]
      return

  def hide( self ):
      self.hideImage = True
      self.image = None
      return

  def show( self ):
      self.hideImage = False
      if ( self.image == None ):
          self.createImage()
      return

  def select( self ):
      if ( self.selected == False ):
          self.selected = True
          self.image = None
          #self.createImage()
          return True
      return False

  def isSelected( self ):
      return self.selected

  def unselect( self ):
      if ( self.selected == True ):
          self.selected = False
          self.image = None
          #self.createImage()
          return True
      return False

  def mark( self ):
      self.lineColor = wx.RED
      self.lineSize = 2
      return

  def unmark( self ):
      self.lineColor = wx.BLACK
      self.lineSize = 1
      return

  def setFontAndColor( self, font, color ):
      self.font = font
      self.fontcolor = color
      self.fontsize = self.font.GetPointSize()
      return

  def updateText( self, text ):
      self.text = text
      self.image = None
      self.createImage()
      return

  def updatePos( self, x, y ):
      self.imageX = x
      self.imageY = y
      return

  def zoomIn( self ):
      import Graph
      self.scale += 5
      self.imageX += 30
      self.imageY += 100
      self.fontsize += 2
      self.font.SetPointSize( self.fontsize )
      self.select()
      self.createImage()
      self.unselect()
      self.createImage()
      return

  def zoomOut( self ):
      import Graph
      self.scale -= 5
      # Need to scale things into the center of the screen
      self.imageX -= 30
      self.imageY -= 100
      self.fontsize -= 2
      self.font.SetPointSize( self.fontsize )
      self.image = None
      self.select()
      self.createImage()
      self.unselect()
      self.createImage()
      return

