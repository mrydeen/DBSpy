###############################################################################
# This script will attempt to generate data for namespaces, and it 
# will fill the gaps for the opm.acquisition_info table as well.
###############################################################################
import mysql.connector 
import uuid, random, time
import numpy as np
import datetime

#
# Server Parameters
#
UMSERVER = "10.231.176.196" 
USER = "mrydeen" 
PASSWORD = "" 

# Create tables if they do not exist
SAMPLE_CREATE = "CREATE TABLE IF NOT EXISTS `sample_namespace_%s` (" +\
                    "`objid` bigint(20) NOT NULL DEFAULT '0'," +\
                    "`time` bigint(20) NOT NULL DEFAULT '0'," +\
                    "`empty` tinyint(1) DEFAULT NULL," +\
                    "`avgLatency` float DEFAULT NULL," +\
                    "`avgReadLatency` float DEFAULT NULL," +\
                    "`avgWriteLatency` float DEFAULT NULL," +\
                    "`avgOtherLatency` float DEFAULT NULL," +\
                    "`totalData` float DEFAULT NULL," +\
                    "`readData` float DEFAULT NULL," +\
                    "`writeData` float DEFAULT NULL," +\
                    "`totalOps` float DEFAULT NULL," +\
                    "`readOps` float DEFAULT NULL," +\
                    "`writeOps` float DEFAULT NULL," +\
                    "`otherOps` float DEFAULT NULL," +\
                    "PRIMARY KEY (`objid`,`time`)," +\
                    "KEY `time_index` (`time`)" +\
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8"

SUMMARY_CREATE = "CREATE TABLE IF NOT EXISTS `summary_namespace_%s` (" +\
                    "`objid` bigint(20) NOT NULL DEFAULT '0'," +\
                    "`fromtime` bigint(20) NOT NULL DEFAULT '0'," +\
                    "`avgLatency` float DEFAULT NULL," +\
                    "`avgReadLatency` float DEFAULT NULL," +\
                    "`avgWriteLatency` float DEFAULT NULL," +\
                    "`avgOtherLatency` float DEFAULT NULL," +\
                    "`totalData` float DEFAULT NULL," +\
                    "`readData` float DEFAULT NULL," +\
                    "`writeData` float DEFAULT NULL," +\
                    "`totalOps` float DEFAULT NULL," +\
                    "`readOps` float DEFAULT NULL," +\
                    "`writeOps` float DEFAULT NULL," +\
                    "`otherOps` float DEFAULT NULL," +\
                    "PRIMARY KEY (`objid`,`fromtime`)," +\
                    "KEY `fromtime_index` (`fromtime`)" +\
                  ") ENGINE=InnoDB DEFAULT CHARSET=utf8" 



###############################################################################
# Function to handle mysql commands
###############################################################################
def tryAndDump( cursor, cmd, conn ):
    try:
	if ( ";" in cmd ):
	    cursor.execute(cmd, multi=True)
	else:
	    cursor.execute(cmd)
	conn.commit()
    except Exception, err:
	if ( "Partition management" not in err.message ):
	    print Exception, err
    except mysql.connector.Error as merr:
	print merr.msg
    return

###############################################################################
# Connect to the server
###############################################################################
DBCONN = mysql.connector.connect( host=UMSERVER,
                                  user=USER, 
                                  passwd=PASSWORD, 
                                  autocommit=True, 
                                  raw=False, 
                                  db="")
DBWORKER = DBCONN.cursor()

STATSDB = "netapp_performance"
DOMAINDB = "netapp_model"
OPMDB = "opm"

###############################################################################
# We want to grab all of the namespaces and add statistics for them, 72 hours if we can.
###############################################################################
DBCONN.database = DOMAINDB
DBWORKER.execute("SELECT * FROM namespace WHERE objState='LIVE'")
NAMESPACES = DBWORKER.fetchall()

# Now only look at the clusters with namespaces
CLUSTERIDS = []
for namespace in NAMESPACES:
    CLUSTERIDS.append( namespace[7] )

###############################################################################
# Make a timestamp that is now and back 168 hours (7 days).  
###############################################################################
CURRENTTIME = int(str(time.time()).split(".")[0])
# 60 seconds in a minute, 60 minutes in an hour, 72 hours in 3 days
BACKXDAYS = CURRENTTIME - (60 * 60 * 168) # 7 days
#BACKXDAYS = CURRENTTIME - (60 * 60 * 110) # 5 days
#BACKXDAYS = CURRENTTIME - (60 * 60 * 24) # 1 day

###############################################################################
# Method to grab the acqusition times
###############################################################################
ACQTIMESBYCLUSTERID = {}
def collectClusterAcqTimes( clusterId, startTime, endTime, includeEndTime ):
    global ACQTIMESBYCLUSTERID, DBCONN, DBWORKER, OPMDB
    DBCONN.database = OPMDB
    includeStr = " >= "
    if ( not includeEndTime ):
        includeStr = " > "
    DBWORKER.execute("SELECT DISTINCT time FROM acquisition_info WHERE success = 1 AND time <= " +\
		     str(startTime) + " AND time " + includeStr + str(endTime) + " AND clusterId = "+str(clusterId))
    acquisitionTimes = DBWORKER.fetchall()
    print "Found " + str(len(acquisitionTimes)) + " collection times for cluster: " + str(clusterId) + " for times between " + str(startTime) + " and " + str(endTime)

    # Need to walk the acquisition times and fill in the gaps.  All the times 
    # should be within 5 minutes
    prevtime = -1
    newTimes = []
    for acqTime in acquisitionTimes:
        if ( prevtime != -1 ):
	    # See if the delta between the previous time and the current
	    # time is > 6 minutes
	    deltaTime = (acqTime[0] - prevtime[0])/1000
	    if ( deltaTime > 360 ):
                print "Found a %s second gap between collections" % deltaTime
		# Add in entries to the acquitision_info table to fill in 
		# the blanks
		nextTime = prevtime[0] + (300 * 1000) # 5 minutes in seconds
		x = 1
		while ( nextTime < acqTime[0] ):
		    cmd = "INSERT INTO acquisition_info " +\
                             "(time, success, clusterId, analysisDuration, collectionDuration, msgRcvTime, isHistorical) " +\
			     "VALUES ("+str(nextTime)+",1,"+str(clusterId)+",180, 200,"+str(nextTime)+",0)"
	            DBWORKER.execute(cmd)
	            newTimes.append((nextTime))
		    nextTime = nextTime + (300 * 1000) # 5 minutes in seconds
		    print str(x) +" : "+cmd
		    x = x + 1
	prevtime = acqTime
	newTimes.append(acqTime)
    ACQTIMESBYCLUSTERID[clusterId] = acquisitionTimes
    return


###############################################################################
# Flush the statistics and grab some necessary info
###############################################################################
for clusterId in CLUSTERIDS:
    collectClusterAcqTimes(clusterId, CURRENTTIME*1000, BACKXDAYS*1000, True)

    #
    # Lets make sure to flush the existing tables so that we do not have to worry 
    # about multiple entries.
    #
    print "Flushing the existing namespace statistics or adding if not exists"
    DBCONN.database = STATSDB
    tryAndDump( DBWORKER, SAMPLE_CREATE % clusterId, DBCONN)
    tryAndDump( DBWORKER, SUMMARY_CREATE % clusterId, DBCONN)
    tryAndDump( DBWORKER, "TRUNCATE TABLE sample_namespace_"+str(clusterId), DBCONN)
    tryAndDump( DBWORKER, "TRUNCATE TABLE summary_namespace_"+str(clusterId), DBCONN)

    # Remove the partitions so that we do not have to worry about 
    # creating them.
    tryAndDump( DBWORKER, "ALTER TABLE sample_namespace_"+str(clusterId)+" REMOVE PARTITIONING", DBCONN)
    tryAndDump( DBWORKER, "ALTER TABLE summary_namespace_"+str(clusterId)+" REMOVE PARTITIONING", DBCONN)

###############################################################################
# Now for each namespace, add into the sample and summary tables
###############################################################################
LASTACQTIMES = {}
print "Populating the statistics"
while (1):
    DBCONN.database = STATSDB
    numNameSpaces = len(NAMESPACES)
    i = 1
    volStats = {}
    for namespace in NAMESPACES:
        print "Working on namespace: " + namespace[9] + ":" + str(namespace[1]) + "  (" + str((i*100)/numNameSpaces) + "%)"
	# namespace[7] is the clusterId
        previousHour = -1
	volStats[namespace[5]] = [namespace[7], {}, []] # clusterId and timestamp with IOPS, Data, Latency
        for acquisitionTime in ACQTIMESBYCLUSTERID[namespace[7]]:
	    # Come up with some "valid" numbers
	    readOps = random.randint(20, 100)
	    writeOps = random.randint(0, 50)
	    otherOps = random.randint(0, 3)
	    #totalOps = readOps + writeOps + otherOps
	    totalOps = random.randint(150000, 165000)
	    readData = random.randint(60, 100) * 512 * 1024
	    writeData = 0
	    if ( writeOps != 0 ):
	        writeData = random.randint(10, 100) * 512 * 1024
	    otherData = 0
	    if ( otherOps != 0 ):
	        otherData = random.randint(1, 100) * 512
	    #totalData = readData + writeData + otherData
	    #totalData = random.randint(10000000000, 25600000000)
	    totalData = random.randint(19000*1024, 20000*1024)
	    avgReadLatency = round(random.uniform(1.0, 800.0 ),3)
	    avgWriteLatency = 0
	    if ( writeOps != 0 ):
	        avgWriteLatency = round(random.uniform(1.0, 800.0),3)
	    avgOtherLatency = 0
	    if ( otherOps != 0 ):
	        avgOtherLatency = round(random.uniform(1.0, 800.0),3)
	    #avgLatency = round(((avgReadLatency + avgWriteLatency + avgOtherLatency)/3),3)
	    avgLatency = round(random.uniform(0.120, 0.220), 3) # these are in microseconds.
    
	    cmd = "INSERT INTO sample_namespace_"+str(namespace[7]) +\
	          " (objid, time, empty, avgLatency, avgReadLatency, avgWriteLatency, avgOtherLatency, totalData, readData, writeData, totalOps, readOps, writeOps, otherOps) " +\
	          "VALUES ("+str(namespace[0])+","+str(acquisitionTime[0])+",0,"+\
	          str(avgLatency)+","+\
	          str(avgReadLatency)+","+\
	          str(avgWriteLatency)+","+\
	          str(avgOtherLatency)+","+\
	          str(totalData)+","+\
	          str(readData)+","+\
	          str(writeData)+","+\
	          str(totalOps)+","+\
	          str(readOps)+","+\
	          str(writeOps)+","+\
	          str(otherOps)+")"
	    try:
	        DBWORKER.execute(cmd)
	    except Exception, err:
                print Exception, err
	        print cmd
	        #exit()
    
	    #
	    # See if we are in a new hour.  If we are, add an entry to the summary tables as well.
	    #
	    dtime = datetime.datetime.fromtimestamp(acquisitionTime[0]/1000)
	    currentHour = dtime.hour
	    if ( previousHour == -1 or (previousHour != -1 and (previousHour != currentHour)) ):
                dtime = dtime.replace(minute=0, second=0, microsecond=0)
		millTime = int(time.mktime(dtime.timetuple()))*1000
		# Now check if there is a time entry for this time/volume yet
		vs = volStats[namespace[5]][1]
		if ( vs.has_key(millTime) ):
                    vs[millTime][0] = vs[millTime][0] + totalOps
                    vs[millTime][1] = vs[millTime][1] + totalData
                    vs[millTime][2] = round(random.uniform(0.220, 0.320), 3) 
		else:
		    vs[millTime] = [totalOps, totalData, round(random.uniform(0.220, 0.320), 3)]
		    volStats[namespace[5]][2].append(millTime)
		cmd = "INSERT INTO summary_namespace_"+str(namespace[7]) +\
	              " (objid, fromtime, avgLatency, avgReadLatency, avgWriteLatency, avgOtherLatency, totalData, readData, writeData, totalOps, readOps, writeOps, otherOps) " +\
	              "VALUES ("+str(namespace[0])+","+str(millTime)+","+\
	              str(avgLatency)+","+\
	              str(avgReadLatency)+","+\
	              str(avgWriteLatency)+","+\
	              str(avgOtherLatency)+","+\
	              str(totalData)+","+\
	              str(readData)+","+\
	              str(writeData)+","+\
	              str(totalOps)+","+\
	              str(readOps)+","+\
	              str(writeOps)+","+\
	              str(otherOps)+")"
	        previousHour = currentHour
	        try:
	            DBWORKER.execute(cmd)
	        except Exception, err:
                    pass
                    #print Exception, err
	            #print "====> "+cmd
	            #exit()
        i = i + 1

    # Now we need to populate the volume summary_qos_volume_workload table
    for volId in volStats.keys():
	volEntry = volStats[volId]
	clusterId = volEntry[0]
	statsDict = volEntry[1]
	statsOrder = volEntry[2]
	# Need to get the workloadId for the volume
        DBCONN.database = DOMAINDB
        DBWORKER.execute("SELECT objId FROM qos_workload WHERE holderId="+str(volId))
        wkId = DBWORKER.fetchall()[0][0]
	
        DBCONN.database = STATSDB
	for so in statsOrder:
            iops, data, latency = statsDict[so]
            cmd = "INSERT INTO summary_qos_volume_workload_"+str(clusterId) +\
	              " (objid, fromtime, latency, ops, totalData) " +\
	              "VALUES ("+str(wkId)+","+str(so)+","+\
	              str(latency)+","+\
	              str(iops)+","+\
	              str(data)+")" +\
		   " ON DUPLICATE KEY UPDATE " +\
		   " latency="+str(latency)+"," +\
		   " ops="+str(iops)+"," +\
		   " totalData="+str(totalData)
	    try:
	        print "====> "+cmd
	        DBWORKER.execute(cmd)
	    except Exception, err:
                print Exception, err
	        #exit()
       

    print "Finished populating: waiting 6 minutes for next acquisition"
    #time.sleep(360)
    time.sleep(10)

    # Fetch the namespaces again in case more were added.
    DBCONN.database = DOMAINDB
    DBWORKER.execute("SELECT * FROM namespace WHERE objState='LIVE'")
    NAMESPACES = DBWORKER.fetchall()
    
    # Keep the last acqusition times by cluster
    for key in ACQTIMESBYCLUSTERID.keys():
        acqList = ACQTIMESBYCLUSTERID[key]
	if (len(acqList) != 0 ):
            LASTACQTIMES[key] = acqList[-1][0]

    # We woke up, now refresh the acquisition times based on the last entry.
    currentTime = int(str(time.time()).split(".")[0])
    for clusterId in CLUSTERIDS:
	lastAcqTime = LASTACQTIMES[clusterId]
        collectClusterAcqTimes(clusterId, currentTime*1000, lastAcqTime, False)





