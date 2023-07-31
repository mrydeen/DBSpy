import sys, os

# Look for Chrome
chromePath = os.environ['ProgramFiles'] + "\\Google\\Chrome\\Application\\chrome.exe"

# Check if chrome in 32bit area, if not check 64 bit installation dir
if ( !os.path.isfile(chromePath) ):
    # Could not find chrome in 32 bit area, look in 64 bit installation
    # dir
    chromePath = os.environ['ProgramFilesW6432'] + "\\Google\\Chrome\\Application\\chrome.exe"
    if ( !os.path.isfile(chromePath) ):
        print "Chrome not found"
        # Disable button

fireFoxPath = os.environ['ProgramFiles'] + "\\Mozilla Firefox\\firefox.exe"
# Check if firefox in 32bit area, of not check 64 bit installation dir
if ( !os.path.isfile(fireFoxPath) ):
    # Could not find chrome in 32 bit area, look in 64 bit installation
    # dir
    fireFoxPath = os.environ['ProgramFilesW6432'] + "\\Mozilla Firefox\\firefox.exe"
    if ( !os.path.isfile(chromePath) ):
        print "FireFox not found"



