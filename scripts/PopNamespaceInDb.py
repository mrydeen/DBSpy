import mysql.connector 
import uuid, random, time

#
# Server Parameters
#
SERVER = "10.231.176.196" 
USER = "mrydeen" 
PASSWORD = "" 

#
# Connect to the server
#
dbConn = mysql.connector.connect( host=SERVER,
                                  user=USER, 
                                  passwd=PASSWORD, 
                                  autocommit=True, 
                                  raw=True, 
                                  db="")
dbWorker = dbConn.cursor()

#
# We want to grab all of the qtrees and add a namespace entry.
#
dbWorker.execute("select * from netapp_model.qtree where objState='LIVE'")
qtrees = dbWorker.fetchall()
x = 1
for qtree in qtrees:
    mytime = str(int(str(time.time()).split(".")[0])*1000)
    nuuid = str(uuid.uuid4())
    vserverRk = str(qtree[3])
    qtreeId = str(qtree[0])
    clusterUuid = vserverRk.split(":")[0]
    namespaceRk = clusterUuid + ":type=namespace,uuid="+nuuid
    clusterId = str(qtree[6])
    volumeId = str(qtree[7])
    vserverId = str(qtree[8])
    # Need to get the nodeid from the volumes aggregate
    dbWorker.execute("select aggregateId from netapp_model.volume where objId="+str(volumeId))
    aggregateId = dbWorker.fetchall()[0][0]
    nodeId = "0"
    if ( aggregateId != None ):
        dbWorker.execute("select nodeId from netapp_model.aggregate where objId="+str(aggregateId))
        nodeId = str(dbWorker.fetchall()[0][0])
    else:
        continue
    randomNumber = random.randint(0,1000)
    path="/home/yaba/daba/do"+str(randomNumber)
    subsystem = "SubSystem" + str(randomNumber)
    i =  "INSERT INTO netapp_model.namespace (objid, originid, uuid, resourceKey, qtreeId, volumeId, vserverId, clusterId, path, state, subsystem, isReadOnly, restoreInaccessible, size, blockSize, sizeUsed, comment, createtime, updatetime, checksum, changeDetailChecksum) "
    v =  "VALUES ("+str(objid)+","+str(randomNumber)+",'"+nuuid+"','"+namespaceRk+"',"+qtreeId+","+volumeId+","+vserverId+","+clusterId+",'"+path+"','ONLINE','"+subsystem+"',"+"0"+","+"0"+","+"1000"+","+"1024"+","+"500"+","+"'My comment',"+mytime+","+mytime+",52,52)"
    print i
    print v
    dbWorker.execute(i+v)
    x = x + 1
