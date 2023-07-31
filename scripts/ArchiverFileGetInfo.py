
# Import the NetApp protocol classes.
#
import NaServer, NaElement
import urllib2

# A sample filer to connect to
#
filerAddress = "10.195.48.190"
filerUserName = "admin"
filerPassword = "netapp1!"
useSSL = True
filerConn = None

###########################################################################
# A method to create a connection based on the filer information above
# @return a filer connection object
###########################################################################
def createConnection():
    global filerAddress, filerUserName, filerPassword, useSSL
    import NaServer
    filerConn = NaServer.NaServer(filerAddress)
    filerConn.setAdminUser(filerUserName, filerPassword)
    if ( useSSL == True ):
        filerConn.setTransportType('https')
        filerConn.setPort(443)
    else: 
        filerConn.setTransportType('http')
        filerConn.setPort(80)  
    return filerConn

###########################################################################
# A method to actually make a zapi command to the filer
# @return the results of the request.
###########################################################################
def makeRequest( zapi_command, extra="" ):
    global filerConn
    import NaElement, urllib2
    xi = NaElement.NaElement(zapi_command)
    if ( extra != "" ) :
        params = extra.split("=")
        xi.addNewChild(params[0], params[1])
    results = NaElement.NaElement("result")
    try:
        results = filerConn.invokeElem(xi)
    except urllib2.URLError:
        print "Error in communicating with Filer, please verify that that is the correct address"
    return results


###########################################################################
# Simple method to request statistical information from the filer.
###########################################################################
def makeStatsRequest( objectType, counter, instance ):
    global filerConn
    import NaElement, urllib2

    print (objectType, counter, instance)
    xi = NaElement.NaElement("perf-object-get-instances")
    xi.addNewChild("objectname", objectType)
    if ( counter != None ):
        counters = NaElement.NaElement("counters")
        counters.addChildElem(NaElement.NaElement("counter", counter))
        xi.addChildElem(counters)
    if (instance != None):
        instances = NaElement.NaElement("instance-uuids")
        instances.addChildElem(NaElement.NaElement("instance-uuid", instance))
        xi.addChildElem(instances)

    print xi.toEncodedString()
    statsResults = filerConn.invokeElem(xi)

    return statsResults

#######################################################################################
# Create a connection
filerConn = createConnection()
results = makeRequest("perf-archive-datastore-get-iter")
#print results.toPrettyString()
datastoreResults = results.getChildByName('attributes-list')
datastores = []
for datastore in datastoreResults.getChildren():
    node = datastore.getChildContent("node")
    path = datastore.getChildContent("path")
    print (node, path)
    dataFileResults = datastore.getChildByName('perf-archive-datafile-infos')
    datafiles = []
    for datafile in dataFileResults.getChildren():
        duration = datafile.getChildContent("duration")
        timestamp = datafile.getChildContent("timestamp")
        fileNames = []
        print (duration, timestamp)
        fileNameResults = datafile.getChildByName('filenames')
        for fn in fileNameResults.getChildren():
            fileNames.append(fn.getContent())
	datastores.append((node, path, fileNames, timestamp, duration))

print datastores




