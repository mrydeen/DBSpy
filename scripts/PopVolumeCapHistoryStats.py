###############################################################################
# This script will attempt to generate capacity history data for volumes
###############################################################################
import mysql.connector 
from mysql.connector.constants import ClientFlag
import sys
import datetime

#
# Server Parameters
# EDIT THESE PARAMETERS
#
UMSERVER = "10.234.168.169" 
USER = "umdev" 
PASSWORD = "ugauga" 
VOLUME_ID = "38763"
#VOLUME_ID = "3587"
DAYS_TO_FILL = 30


VOLUME_CAP_TABLES = ["volumehistorymonth", "volumehistoryweek", "volumehistoryyear"]
STATSDB = "netapp_performance"
DOMAINDB = "netapp_model"
OPMDB = "opm"
OCUMDB = "ocum"

###############################################################################
# Printing in python 3 and python 2 are different.  Need to catch to make
# sure this runs on both
###############################################################################
def log( message ):
    print(str(message))

###############################################################################
# Simple method to find the index of a particular column
###############################################################################
def findIndex(name, columns):
    index = 0
    for c in columns:
        if (name == c[0]):
            print(name + " : " + str(index))
            return index 
        index += 1
    return None 

###############################################################################
# Connect to the server
###############################################################################
DBCONN = mysql.connector.connect( host=UMSERVER,
                                  user=USER, 
                                  passwd=PASSWORD, 
                                  autocommit=True, 
                                  auth_plugin='mysql_native_password',
                                  raw=False, 
                                  db="",
                                  connection_timeout=86400,
                                  client_flags=[ClientFlag.MULTI_STATEMENTS])
DBWORKER = DBCONN.cursor()

###############################################################################
# See if there is any data currently for the volume
###############################################################################
DBCONN.database = DOMAINDB
DBWORKER.execute("SHOW COLUMNS FROM volume")
COLUMNS = DBWORKER.fetchall()
DBWORKER.execute("SELECT * FROM volume WHERE objId=" + VOLUME_ID)
VOLUME = DBWORKER.fetchall()
if (len(VOLUME) == 0):
    log("No volume found with id = " + VOLUME_ID)
    sys.exit()
VOLUME = VOLUME[0]
log(VOLUME)


###############################################################################
# Fetch the last stats for this volume
###############################################################################
DBCONN.database = OCUMDB
cmd = "SELECT * from volumehistorymonth where volumeId = " + VOLUME_ID + " order by periodEndTime asc limit 1"
DBWORKER.execute(cmd)
# If there is no entry yet, build it out of the volume itself.
HISTORY = DBWORKER.fetchall()
sizeTotalIndex = findIndex("sizeTotal", COLUMNS) 
sizeUsedIndex = findIndex("sizeUsed", COLUMNS) 
sizeAvailIndex = findIndex("sizeAvail", COLUMNS) 
dedupIndex = findIndex("deduplicationSpaceSaved", COLUMNS)
compressionIndex = findIndex("compressionSpaceSaved", COLUMNS)
logicalIndex = findIndex("logicalSpaceUsed", COLUMNS)
cloudIndex = findIndex("cloudTierFootprintBytes", COLUMNS)
perfIndex = findIndex("performanceTierFootprintBytes", COLUMNS)
snapshotUsedIndex = findIndex("sizeUsedBySnapshots", COLUMNS)
snapshotTotalIndex = findIndex("sizeAvailableForSnapshot", COLUMNS)
# Need to find all the index
if (len(HISTORY) == 0):
    entry = [ VOLUME[0],                                               # volumeId
              datetime.datetime.now().replace(hour=20, minute=0, second=0),     # periodEndtime
              1,                                                       # sampleCount
              0,                                                       # overwriteReserveSpaceAvailSum
              VOLUME[sizeUsedIndex]/1024,                              # dfKBytesUsedSum
              VOLUME[sizeTotalIndex]/1024,                             # dfKBytesTotal
              VOLUME[snapshotUsedIndex]/1024,                          # dfSnapshotKBytesUsedSum
              VOLUME[snapshotTotalIndex]/1024,                         # dfSnapshotKBytesTotal
              VOLUME[dedupIndex]/1024,                                 # dfKBytesDedupeSpaceSavingSum
              VOLUME[compressionIndex]/1024,                           # dfKBytesComressionSpaceSavingSum
              0,                                                       # dfKBytesCloneSpaceSavingSum
              VOLUME[logicalIndex]/1024,                               # dfKBytesLogicalSpaceUsedSum
              VOLUME[sizeAvailIndex]/1024,                             # dfKBytesAvailableSum
              VOLUME[perfIndex]/1024,                                  # dfKBytesPerformanceTierFootprintSum
              VOLUME[cloudIndex]/1024                                  # dfKBytesCloudTierFootprintSum
            ]
    HISTORY = [entry]

log(HISTORY)
entry = HISTORY[0]
entryDate = entry[1]
previousDay = entryDate - datetime.timedelta(1)
toggle = True
for i in range(0, DAYS_TO_FILL):
    insertValues = list(entry)
    insertValues[1] = str(previousDay)
    cmd = "insert into volumehistorymonth (volumeId, periodEndTime, sampleCount, overwriteReserveSpaceAvailSum, dfKBytesUsedSum, dfKBytesTotal, dfSnapshotKBytesUsedSum, dfSnapshotKBytesTotal, dfKBytesDedupeSpaceSavingsSum, dfKBytesCompressionSpaceSavingsSum, dfKBytesCloneSpaceSavingsSum, dfKBytesLogicalSpaceusedSum, dfKBytesAvailableSum, dfKBytesPerformanceTierFootprintSum, dfKBytesCloudTierFootprintSum) values " + str(tuple(insertValues))
    if (toggle):
        insertValues[13] = insertValues[13] - 1000
        insertValues[14] = insertValues[14] + 1000
        toggle = False
    else:
        insertValues[13] = insertValues[13] + 1000
        insertValues[14] = insertValues[14] - 1000
        toggle = True
    log(cmd)
    DBWORKER.execute(cmd)
    previousDay = previousDay - datetime.timedelta(1)
    











