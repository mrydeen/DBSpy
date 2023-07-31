#-----------------------------------------------------------------------------
# Name:        QosStatsToExcelXml.py
# Purpose:     A simple class to create an Excel based XML file that is based
#              on the CDOT Qos Workload Statistics.
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History


import datetime, os, time, wx

# Used to map the service center name to a tab name because excel
# cannot have large tab names
SS_TO_TAB_NAME = { "CPU_dblade": "CPU_Db",
                   "CPU_nblade": "CPU_Nb",
                   "DELAY_CENTER_CLUSTER_INTERCONNECT": "DC_C_X",
                   "DELAY_CENTER_DISK_IO_OTHER": "DC_Disk_IO_O",
                   "DELAY_CENTER_NETWORK": "DC_NET",
                   "DELAY_CENTER_QOS_LIMIT": "DC_QOS_Limit",
                   "DELAY_CENTER_WAFL_SUSP_CP": "DC_WAFL_Susp_CP",
                   "CPU_dblade_background": "CPU_Db_Bkg",
                   "CPU_exempt": "CPU_Ex"
                 }

###############################################################################
# A class to export qos statistics to an excel XML format.
###############################################################################
class QosStatsToExcelXml:
    def __init__( self, parent, volumeId, numOfDays, filename ):
        self.parent = parent
        self.volumeId = volumeId
        self.numberOfDays = numOfDays
        self.fileName = filename
        self.currentTime = long(time.time() * 1000)
        self.daysPast= self.currentTime - ((self.numberOfDays * 24 * 60 * 60 * 1000))
        self.fetchData()
        self.writeOutFile()
        return
    
    ############################################################################
    # Method to go and fetch all of the data that we need.  Might need to
    # revisit if we are using a lot of memory.
    ############################################################################
    def fetchData( self ):
        # First grab the volume information:
        sql="select * from netapp_model.volume where objid = " + str(self.volumeId)
        self.volume = self.parent.executeAll(sql)[0]
        #print self.volume

        # Now grab the workload information
        sql="select * from netapp_model.qos_volume_workload where volumeId = " + str(self.volumeId)
        self.workload = self.parent.executeAll(sql)[0]
        #print self.workload

        # Now grab all of the workload details
        sql="select * from netapp_model.qos_workload_detail where workloadId = " + str(self.workload[0])
        self.workloadDetails = self.parent.executeAll(sql)
        #for wd in self.workloadDetails:
        #    print "  " + wd[2]

        # Fetch the workload stats columns.
        sql="show columns from netapp_performance.sample_qos_volume_workload_" + str(self.workload[5])
        self.workloadStatsColumns = self.parent.executeAll(sql)
        #print self.workloadStatsColumns

        # Fetch the workload stats.
        sql="select * from netapp_performance.sample_qos_volume_workload_" + str(self.workload[5]) + " where objid=" + str(self.workload[0]) + " and time > " + str(self.daysPast)
        self.workloadStats = self.parent.executeAll(sql)

        # Fetch the workload detail stats columns
        sql="show columns from netapp_performance.sample_qos_workload_detail_" + str(self.workload[5])
        self.workloadDetailStatsColumns = self.parent.executeAll(sql)

        # Fetch all of the workload detail stats.
        self.workloadDetailStatsMap = {}
        for wd in self.workloadDetails:
            sql="select * from netapp_performance.sample_qos_workload_detail_" + str(self.workload[5]) + " where objid=" + str(wd[0]) + " and time > " + str(self.daysPast)
            wdStats = self.parent.executeAll(sql)
            #print wd[2] + " --> " + str(len(wdStats))
            if ( len(wdStats) > 0 ):
                self.workloadDetailStatsMap[wd[2]] = (wd[0], wdStats)

    def writeOutFile( self ):
        # Now output the data to a excel XML file.  Use the workload stats as our base.
        file = None
        try:
            file = open(self.fileName, "w")
        except IOError as inst:
            wx.MessageBox("Permission denied for file: " + self.fileName)
            return
        file.write('<?xml version="1.0"?>\n')
        file.write('<ss:Workbook xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">\n')
        file.write('  <ss:Styles>\n')
        file.write('    <ss:Style ss:ID="1">\n')
        file.write('      <ss:Font ss:Bold="1"/>\n')
        file.write('    </ss:Style>\n')
        file.write('  </ss:Styles>\n')

        # Output the workload statistics first.  Make sure to set the header
        file.write('<ss:Worksheet ss:Name="workload('+str(self.workload[0])+')">\n')
        file.write('  <ss:Table>\n')
        # Add the Workload Name
        file.write('    <ss:Row ss:StyleID="1">\n')
        file.write('      <ss:Cell>\n')
        file.write('        <ss:Data ss:Type="String">Workload Name: ' + self.workload[4] + '</ss:Data>\n')
        file.write('      </ss:Cell>\n')
        file.write('    </ss:Row>\n')
        file.write('    <ss:Row ss:StyleID="1">\n')
        for column in self.workloadStatsColumns:
            if ( column[0] == "objid" ): continue
            file.write('      <ss:Cell>\n')
            file.write('        <ss:Data ss:Type="String">' + column[0] + '</ss:Data>\n')
            file.write('      </ss:Cell>\n')
        file.write('    </ss:Row>\n')
        
        # Now do the stats
        for stat in reversed(self.workloadStats):
            file.write('    <ss:Row>\n')
            # Skip the id
            index = 0
            for s in stat[1:]:
                file.write('      <ss:Cell>\n')
                if ( index != 0 ):
                    file.write('        <ss:Data ss:Type="String">' + str(s) + '</ss:Data>\n')
                else:
                    strTime = datetime.datetime.fromtimestamp(s/1000).strftime('%m-%d-%Y %H:%M:%S')
                    file.write('        <ss:Data ss:Type="String">' + str(strTime) + '</ss:Data>\n')
                file.write('      </ss:Cell>\n')
                index = index + 1
            file.write('    </ss:Row>\n')
        
        file.write('  </ss:Table>\n')
        file.write('</ss:Worksheet>\n')
        
       # Now create a worksheet for each cluster component.
        # Output the workload statistics first.  Make sure to set the header
        for workloadDetail in self.workloadDetailStatsMap.keys():
            #print workloadDetail
            name = workloadDetail.split(".")[2]
            # Get the tab name
            tabName = ""
            if ( "aggr" not in name ):
                tabName = SS_TO_TAB_NAME[name]
            else:
                if ( "DISK_HDD" in name ):
                    tabName = "DISK_HDD"
                elif ( "DISK_SDD" in name ):
                    tabName = "DISK_SDD"
                else:
                    tabName = "DC_Disk_IO_Aggr"
        
            file.write('<ss:Worksheet ss:Name="'+ tabName + '(' + str(self.workloadDetailStatsMap[workloadDetail][0]) + ')">\n')
            file.write('  <ss:Table>\n')
            # Add the Workload Detail Name
            file.write('    <ss:Row ss:StyleID="1">\n')
            file.write('      <ss:Cell>\n')
            file.write('        <ss:Data ss:Type="String">Workload Detail Name: ' + workloadDetail[37:] + '</ss:Data>\n')
            file.write('      </ss:Cell>\n')
            file.write('    </ss:Row>\n')
        
            file.write('    <ss:Row ss:StyleID="1">\n')
            for column in self.workloadDetailStatsColumns:
                if ( column[0] == "objid" ): continue
                file.write('      <ss:Cell>\n')
                file.write('        <ss:Data ss:Type="String">' + column[0] + '</ss:Data>\n')
                file.write('      </ss:Cell>\n')
            file.write('    </ss:Row>\n')
        
            # Now do the stats
            for stat in reversed(self.workloadDetailStatsMap[workloadDetail][1]):
                file.write('    <ss:Row>\n')
                # Skip the id
                index = 0
                for s in stat[1:]:
                    file.write('      <ss:Cell>\n')
                    if ( index != 0 ):
                        file.write('        <ss:Data ss:Type="String">' + str(s) + '</ss:Data>\n')
                    else:
                        strTime = datetime.datetime.fromtimestamp(s/1000).strftime('%m-%d-%Y %H:%M:%S')
                        file.write('        <ss:Data ss:Type="String">' + str(strTime) + '</ss:Data>\n')
                    file.write('      </ss:Cell>\n')
                    index = index + 1
                file.write('    </ss:Row>\n')
        
            file.write('  </ss:Table>\n')
            file.write('</ss:Worksheet>\n')
        
        file.write('</ss:Workbook>\n')
        file.close()

        return

