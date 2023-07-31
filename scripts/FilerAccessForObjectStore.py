
# Import the NetApp protocol classes.
#
import NaServer, NaElement
import urllib2

# A sample filer to connect to
#
filerAddress = "10.97.152.30"
filerUserName = "ladmin"
filerPassword = "netapp123"
useSSL = False
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


# Create a connection
filerConn = createConnection()
results = makeRequest("system-get-version")
print results.toEncodedString()
version = results.getChildByName('version')
print version.content

# Get the volumes
results = makeRequest("volume-get-iter")
volumes = results.getChildByName('attributes-list')
vols = []
for volume in volumes.getChildren():
    via = volume.getChildByName("volume-id-attributes")
    volName = via.getChildContent("name")
    volUuid = via.getChildContent("instance-uuid")
    vols.append((volName,volUuid))

stats = makeStatsRequest( 'volume', 'total_ops', vols[0][1] )
print "--------------------------------------------"
print stats.toEncodedString()




