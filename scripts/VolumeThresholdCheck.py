import mysql.connector, sys, string, os, time, datetime

#
# Server Parameters
#
SERVER = "opm-int.nane.netapp.com" 
USER = "root" 
PASSWORD = "ugauga" 

# We want to grab the latest time 10 minutes back.
currentTime = time.time() * 1000
tenMinsBack = currentTime - (10 * 60 * 60 * 1000)

#
# Connect to the server
#
dbConn = mysql.connector.connect( host=SERVER,
                                  user=USER, 
                                  passwd=PASSWORD,
                                  db="")
dbWorker = dbConn.cursor()

#
# Now test out the connection
#

cmd = "select objid, name, vserverId, clusterId, aggregateId from netapp_model.volume where objState='LIVE'"
dbWorker.execute(cmd)
volumes = dbWorker.fetchall()
for volume in volumes:
    # Grab the workload for the volume to check its stats
    cmd = "select objid, name, clusterId from netapp_model.qos_volume_workload where volumeId=" + str(volume[0])
    dbWorker.execute(cmd)
    workload = dbWorker.fetchall()
    # Sometimes a volume might not have a workload
    if ( len(workload) == 0 ): continue
    
    workload = workload[0]
    # Now get the stats for this workload
    cmd = "select * from netapp_performance.sample_qos_volume_workload_" + str(workload[2]) + " where objid=" + str(workload[0]) + " and time >= " + str(tenMinsBack) + " limit 1"
    dbWorker.execute(cmd)
    wstats = dbWorker.fetchall()
    
    # Make sure there are actual stats
    if ( len(wstats) == 0 ): continue
    wstats = wstats[0]

    #print datetime.datetime.fromtimestamp(wstats[1]/1000).strftime('%Y-%m-%d %H:%M:%S')

    # Check the OPS
    if ( wstats[4] > 100 ):
        print "%s -> Latency (us): %f  OPS: %f WOPS: %f  ROPS: %f" %(volume[1], wstats[3], wstats[4], wstats[8], wstats[11])
    
    

