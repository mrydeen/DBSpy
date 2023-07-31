#
# A simple example of how to issue a REST call to the UM.
#
import requests

# Global parameters
url = "https://ocum-main-int.gdl.englab.netapp.com/rest/system"
username = "admin"
password = "barharbor"
accept_header = "application/vnd.netapp.system.info.hal+json"
verify_certificates = False

# Dump out all of the methods of the requests module
print dir(requests)
headers = {'accept':accept_header}
response = requests.get(url, auth=(username, password), headers=headers, verify=verify_certificates)

# Print the headers out
print
print response.headers

# Print the content
print
print response.content


