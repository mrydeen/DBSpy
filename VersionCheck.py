#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        VersionCheck.py
# Purpose:     Simple code to grab a version from a location and verify that
#              this is the latest one.
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History

import ftplib, wx, Constants, threading, time, string

class VersionCheck(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        return

    def run(self):
        time.sleep(3)
        # Try and grab the version information.
        ftp = ftplib.FTP(host="rydeenclubhouse.com", user="public", passwd="public")
        ftp.retrbinary('RETR OpmDbSpyNewVersion.txt', open('OpmDbSpyNewVersion.txt', 'wb').write)
        ftp.quit()

        lines = open('OpmDbSpyNewVersion.txt', 'r').readlines()
        version=0
        updates=""
        for line in lines:
            if ( "VERSION" in line ):
                version = line.split("=")[1]
            if ( "UPDATE" in line ):
                updates = line.split("=")[1]

        version = eval(version)
        if ( version > Constants.SPY_VERSION ):
            message = "There is a newer version of Opm Database Spy (" + str(version) + ") out on \\\\aurora\\share\\ipc\\OpmDbSpy \n   Updates: \n " 
            for update in updates.split(";"):
                message += "          " + update + "\n"
            wx.MessageBox(message, style=wx.OK)
    
        return

