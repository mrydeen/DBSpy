###############################################################################
# A simple script to issue commands on a remote server
###############################################################################

import pysftp

SERVER = "ocum-main-int.gdl.englab.netapp.com"
USER = "root"
PASSWORD = "M+D3w"


cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
conn = pysftp.Connection(host=SERVER, 
                         username=USER, 
                         password=PASSWORD,
                         cnopts=cnopts)
retVal = conn.execute('ls -al /tmp')
if ( "Access denied" in str(retVal) ):
    print "Access was denied with given username and password"
else:
    print retVal
                
conn.close()
