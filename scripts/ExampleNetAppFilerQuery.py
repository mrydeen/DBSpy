
# Import the NetApp protocol classes.
#
import NaServer, NaElement, ssl

# Ignore self signed certificates
ssl._create_default_https_context = ssl._create_unverified_context

# A sample filer to connect to
#
#filerAddress = "10.231.176.53" # Mobility
filerAddress = "172.26.166.233"
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
    import NaElement
    xi = NaElement.NaElement(zapi_command)
    if ( extra != "" ) :
        params = extra.split("=")
        xi.addNewChild(params[0], params[1])
    results = NaElement.NaElement("result")
    try:
        results = filerConn.invokeElem(xi)
    except Exception as e:
        print("Error in communicating with Filer, please verify that that is the correct address")
        traceback.print_exc()
    return results


###########################################################################
# Simple method to request statistical information from the filer.
###########################################################################
def makeStatsRequest( objectType, counter, instance ):
    global filerConn
    import NaElement

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

    print(xi.toEncodedString())
    statsResults = filerConn.invokeElem(xi)

    return statsResults


# Create a connection
filerConn = createConnection()
results = makeRequest("system-get-version")
version = results.getChildByName('version')
print(version.content)



# Get the applications
results = makeRequest("perf-archive-datastore-get-iter")
attributes = results.getChildByName('attributes-list')
print("Attributes = {}".format(attributes.name))
data = []
for d in attributes.getChildren():
    info = []
    preset = d.getChildContent("datastore")
    print("Preset = {}".format(preset))
    node = d.getChildContent("node")
    print("Node = {}".format(node))
    if ( preset == None ):
        preset = "root"
        
    archives = d.getChildByName("perf-archive-datafile-infos")
    avgSize = 0
    if ( archives ):
        count = 0
        for a in archives.getChildren():
            size = int(a.getChildContent('size'))
            avgSize += size
            count += 1
    else:
        # See if there is a size
        size = int(d.getChildContent('size'))
        if ( size ):
            avgSize = size

    avgSize = avgSize/count
    info = [preset, avgSize]
    print(info)
    data.append(info)

#stats = makeStatsRequest( 'volume', 'total_ops', vols[0][1] )
#print "--------------------------------------------"
#print stats.toEncodedString()





