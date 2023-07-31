#Viewer!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        Constants.py
# Purpose:     Contains predefined and constant variables
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

# Version
SPY_VERSION = "9.8"
SOFTWARE_VERSION = "UM DataBase Spy " + SPY_VERSION

###############################################################################
# Element Types from OPM
###############################################################################
ELEMENT_AGGREGATE = 1
ELEMENT_CLUSTER = 2
ELEMENT_DISK = 3
ELEMENT_FCP_LIF = 4
ELEMENT_FCP_PORT = 5
ELEMENT_LUN = 6
ELEMENT_NETWORK_LIF = 7
ELEMENT_NETWORK_PORT = 8
ELEMENT_CLUSTER_NODE = 9
ELEMENT_PLEX = 10
ELEMENT_QTREE = 11
ELEMENT_RAID_GROUP = 12
ELEMENT_VOLUME = 13
ELEMENT_VSERVER = 14
ELEMENT_QOS_VOLUME_WORKLOAD = 23
ELEMENT_NAMESPACE = 69
ELEMENT_NVMF_FC_LIF = 70

###############################################################################
# Resource Object Types
###############################################################################
SERVER                  = 1
APPLICATION             = 2
SERVER_VOLUME           = 3
SERVER_LUN              = 4
SERVER_HBA              = 5
STORAGE_ARRAY           = 6
STORAGE_ARRAY_DISK      = 7
STORAGE_ARRAY_DISK_SSD  = 8
STORAGE_ARRAY_RAIDSET   = 9
DISKGROUP               = 10
STORAGE_ARRAY_LUN       = 11
STORAGE_ARRAY_VOLUME    = 12
STORAGE_ARRAY_CONT      = 13
STORAGE_ARRAY_FCPORT    = 14
ASG                     = 15
APP_INSTANCE            = 16
APP_INSTANCE2           = 17
APP_DATA                = 18
APP_DATA2               = 19
CLUSTER                 = 20
SHAREPOINT              = 21
FCSWITCH                = 22
FCSWITCH_PORT           = 23
SUBGROUP                = 24
DISK_PARTITION          = 25
NAMESPACE               = 26
UNACCOUNTED_WORKLOAD    = 27

DC_NETWORK =              50
NBLADE =                  51
DC_QOS_LIMIT =            52
DC_CLUSTER_INTERCONNECT = 53
DBLADE =                  54
DBLADE_BACKGROUND =       55
DC_DISK_IO =              56
DC_WAFL_SUSP_CP =         57
DISK_HDD =                58
DISK_SDD =                59

###############################################################################
# MAP of OPM Element to Db Spy Resource Objects
###############################################################################
ELEMENT_TO_RESOURCE_MAP= {
                           ELEMENT_AGGREGATE:DISKGROUP,
                           ELEMENT_CLUSTER:CLUSTER,
                           ELEMENT_DISK:STORAGE_ARRAY_DISK,
                           ELEMENT_LUN:STORAGE_ARRAY_LUN,
                           ELEMENT_CLUSTER_NODE:STORAGE_ARRAY,
                           ELEMENT_FCP_PORT:STORAGE_ARRAY_FCPORT,
                           ELEMENT_VOLUME:STORAGE_ARRAY_VOLUME
                         }



###############################################################################
# Threshold Analysis Role
###############################################################################
THRESHOLD_ANALYSIS_ROLE = { 1: "TRIGGER",
                            2: "INSIGNIFICANT TRIGGER",
                            3: "UNKNOWN"
                          }

###############################################################################
# Workload Sort Type
###############################################################################
WORKLOAD_SORT_TYPE = { 0: "PAIN_INDEX",
                       1: "ABSOLUTE_UTIL",
                       2: "ABNORMAL_UTIL",
                       3: "ABSOLUTE_PER_QUEUE_CONT",
                       4: "ABNORMAL_PER_QUEUE_CONT",
                       5: "ABSOLUTE_PER_QOS_LIMIT",
                       6: "ABNORMAL_PER_QOS_LIMIT"
                     }

###############################################################################
# Given a resource type, hand back the DB table name
###############################################################################
def getDBTableNameFromResource( resourceType ):
      # Need to map type to table
      tableName = ""
      if ( resourceType == DISKGROUP or resourceType == 1):
          tableName = "netapp_model.aggregate"
      elif ( resourceType == STORAGE_ARRAY_DISK ):
          tableName = "netapp_model.disk"
      elif ( resourceType == STORAGE_ARRAY ):
          tableName = "netapp_model.node"
      elif ( resourceType == STORAGE_ARRAY_VOLUME ):
          tableName = "netapp_model.volume"
      elif ( resourceType == STORAGE_ARRAY_LUN ):
          tableName = "netapp_model.lun"
      elif ( resourceType == SHAREPOINT ):
          tableName = "netapp_model.cifs_share"
      else:
          print("No table found for type: " + str(resourceType))

      return tableName
 

###############################################################################
# Given a map, return a string value
###############################################################################
def stringDict( map ):
    s = ""
    for key in map.keys():
        s = s + str(key) + " (" + map[key] + "), "
    return s



