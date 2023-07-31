#Viewer!/usr/bin/env python
#-----------------------------------------------------------------------------
# Name:        UmDbSpy
# Purpose:     Main file for the Um Db Spy
#
# Author:      Michael Rydeen
#
# Created:     2010/11/03
# Copyright:   (c) 2010
# Licence:     Use as you wish.
#----------------------------------------------------------------------------
# History
#

import wx, wx.grid, wx.html, wx._xml, wx.lib.mixins.listctrl, VersionCheck, subprocess, shutil
import os, string, sys, time, traceback, datetime, re, sqlite3, errno, logging
import threading, operator, QosView, Graph, ElementGraphWindow
import DataPlotter, ViewAndEdit, TreeViewer, pysftp, LogViewer, VolumeViewer
import QosStatsToExcelXml, PythonRunner, EventOccurrenceView, ProgressBar
import wx.lib.agw.balloontip as BT
import SoftwareLicenseAgreement, TextBox, SQLCommands
from NaServer import *
from NaElement import *
import wx.lib.agw.advancedsplash as AS
from Constants import *
from io import StringIO
import mysql.connector
from mysql.connector.constants import ClientFlag
import mysql.connector.locales.eng.client_error
import shutil
import TableExporter
import QosPolicyMapping
import TableSnapShot
import requests
import traceback

# These are the numerical values for the tabs.
SUMMARY_TAB = 0
VIEWER_TAB  = 1
SCRIPTS_TAB = 2

DATABASES = []
FILTER_DBS = [ "information_schema",
               "host_data",
               "management",
               "mysql",
               "netapp_model_view",
               "performance",
               "performance_schema",
               "sanscreen",
               "serviceassurance",
               "scrub",
               "workbench",
               "BACKUP",
               "jail",
               "logfolder",
               "ocum_view",
               "ocum_data_collector",
               "#mysql50"
              ]
MUST_FILTER_DBS = True
SHOW_LICENSE = True

SQL_FILE_NAME="SQL_FULL.sql"
BUNDLE_SENTINAL="ODS.dbspy"

BASE_DIR = os.getcwd()

###############################################################################
# Open the SQL Log file
###############################################################################
SQL_FILE = "UmSqlLog.log"
SQL_LOG = open(SQL_FILE, "a", encoding='utf8')

SERVER_IP_HISTORY_FILE = os.environ["APPDATA"] + "\\UMIpHistory.txt"

###############################################################################
# Function: decodeColumnValue
#
# This method helps to decode the columns values to make reading
# enumerations better.  This is used by multiple files thus it is outside
# of the class.
###############################################################################
def decodeColumnValue( parent, setitem, ltable, lcolumn ):
    # If nothing to convert then return
    if ( setitem == None ): return setitem

    # See if we need to convert a time element
    if ( "time" in lcolumn and 
         "servicetime" not in lcolumn and
         "Elapsed" not in lcolumn and 
         "numberof" not in lcolumn and 
         lcolumn != "waittime" ):
        try:
            setitem = str(setitem) + " (" + datetime.datetime.fromtimestamp(setitem/1000).strftime('%m-%d-%Y %H:%M:%S') + ")"
        except:
            setitem = str(setitem)
    elif ( ltable == "opm.change_event" ):
        if ( lcolumn == "objecttypeid" ):
            try:
                setitem = str(setitem) + " (" + parent.ELEMENT_TYPE_DEF[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "changetypeid" ):
            try:
                setitem = str(setitem) + " (" + parent.CHANGE_TYPE_DEF[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
    elif ( ltable == "opm.continuous_event_occurrence" or ltable == "event_occurrence") :
        if ( lcolumn == "targettype" ):
            try:
                setitem = str(setitem) + " (" + parent.TARGET_TYPE_DEF[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "notificationlevel" ):
            try:
                setitem = str(setitem) + " (" + parent.NOTIFICATION_LEVEL[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "type" ):
            try:
                setitem = str(setitem) + " (" + parent.EVENT_TYPE_DEF[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "thresholdpolicyid" ):
            try:
                setitem = str(setitem) + " (" + parent.thresholdPolicies[setitem] + ")"
            except:
                setitem = str(setitem) + " (Policy Not Found)"

        elif ( lcolumn == "sorttypes" ):
            s = " ("
            for key in WORKLOAD_SORT_TYPE.keys():
                if ( ((2**key) & setitem) != 0 ):
                    s = s + WORKLOAD_SORT_TYPE[key] + ", "
            s = s[:-2] + ")"
            setitem = str(setitem) + s
    elif ( ltable == "opm.threshold" or 
           ltable == "opm.threshold_policy" or 
           ltable == "opm.threshold_notification" or 
           ltable == "opm.threshold_policy_mapping" ):
        if ( lcolumn == "elementtype" ):
            try:
                setitem = str(setitem) + " (" + parent.ELEMENT_TYPE_DEF[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "stattype" ):
            try:
                setitem = str(setitem) + " (" + parent.STAT_TYPE_DEF[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "level" ):
            try:
                setitem = str(setitem) + " (" + parent.NOTIFICATION_LEVEL[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "type" and ltable == "opm.threshold"):
            try:
                setitem = str(setitem) + " (" + parent.THRESHOLD_TYPE_DEF[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "type" and ltable == "opm.threshold_notification"):
            try:
                setitem = str(setitem) + " (" + parent.NOTIFICATION_TYPE[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "event" and ltable == "opm.threshold_notification"):
            try:
                setitem = str(setitem) + " (" + parent.NOTIFICATION_UM_EVENT[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "operation" ):
            try:
                setitem = str(setitem) + " (" + parent.OPERATIONS_DEF[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "scope" ):
            try:
                setitem = str(setitem) + " (" + parent.NOTIFICATION_SCOPE[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "dynamicthresholdeventoption" ):
            try:
                setitem = str(setitem) + " (" + parent.NOTIFICATION_DYNAMIC_EVENT_OPTION[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
    elif ( ltable == "opm.continuous_event_participant" or ltable == "opm.event_participant" ):
        if ( lcolumn == "contentionanalysisrole" ):
            try:
                setitem = str(setitem) + " (" + parent.CONTENTION_ANAL_ROLE_DEF[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "thresholdanalysisrole" ):
            try:
                setitem = str(setitem) + " (" + THRESHOLD_ANALYSIS_ROLE[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
        elif ( lcolumn == "participanttype" ):
            try:
                setitem = str(setitem) + " (" + parent.ELEMENT_TYPE_DEF[setitem] + ")"
            except:
                setitem = str(setitem) + " (New Key Found)"
    return setitem

################################################################################
# Simple helper function to turn the string to lower.
################################################################################
def lower( str ):
    return str.lower()

################################################################################
# A simple class to extract a support bundle and show the output.
################################################################################
class ExtractSupportBundle(threading.Thread):
    def __init__(self, xDir, zFileName, textBox, parent, callback):
        self.xDir = xDir
        self.zFileName = zFileName
        self.textBox = textBox
        self.parent = parent
        self.callback = callback
        self.finished = False
        threading.Thread.__init__(self)
        return

    def run( self ):
        
        # For now, only grab the db files and the log files.  The format has changed between the 7.1 
        # the 7.2.  In 7.1, it is a flat file.  In 7.2, they have broken out the files into 
        # directories.
        
        print(BASE_DIR + "\\7z.exe\" x " + self.zFileName + " -aoa")

        self.textBox.setText("\nExtracting required files...\n")

        sbVersion = self.getReleaseVersionOfZip()
        if ( sbVersion == 7.2 ):
            sbFiles = ["mysql/database-dump.sql.7z","jboss/server.log","acquisition/au.log","jboss/server_mega.log","server/ocumserver.log","server/ocum-error.log"]
            success = self.extractFiles( self.zFileName, sbFiles )
            if ( not success ):
                self.textBox.setText("\n Failed to extract files - see console for error\n")
                self.textBox.enableOkButton()
                return

            self.textBox.setText("-----------------------------------------------------------------\n")
            shutil.move(self.xDir+"\\mysql\\database-dump.sql.7z", "database-dump.sql.7z")
            self.textBox.setText("Extracting database-dump.sql.7z\n")
            success = self.extractFile( "database-dump.sql.7z" )
            if ( not success ):
                self.textBox.setText("\n Failed to extract files - see console for error\n")
                self.textBox.enableOkButton()
            self.textBox.setText("-----------------------------------------------------------------\n")
            shutil.move(self.xDir+"\\jboss\\server.log", "jboss-logs-server.log")
            shutil.move(self.xDir+"\\acquisition\\au.log", "jboss-logs-au.log")
            shutil.move(self.xDir+"\\jboss\\server_mega.log", "oncommand-logs-server_mega.log")
            shutil.move(self.xDir+"\\server\\ocumserver.log", "oncommand-logs-ocumserver.log")
            shutil.move(self.xDir+"\\server\\ocum-error.log", "oncommand-logs-ocum-error.log")
            os.rmdir("mysql")
            os.rmdir("server")
            os.rmdir("jboss")
            os.rmdir("acquisition")
        elif ( sbVersion == 7.3 or sbVersion == 7.4 or sbVersion >= 9.4 ):
            sbFiles = ["mysql/database-dump.sql.7z","jboss/server.log","acquisition/au.log","jboss/server_mega.log","server/ocumserver.log.gz","server/ocum-error.log"]
            success = self.extractFiles( self.zFileName, sbFiles )
            if ( not success ):
                self.textBox.setText("\n Failed to extract files - see console for error\n")
                self.textBox.enableOkButton()
                return
            self.textBox.setText("-----------------------------------------------------------------\n")
            shutil.move(self.xDir+"\\mysql\\database-dump.sql.7z", "database-dump.sql.7z")
            success = self.extractFile( "database-dump.sql.7z" )
            if ( not success ):
                self.textBox.setText("\n Failed to extract files - see console for error\n")
                self.textBox.enableOkButton()
                return
            try:
                shutil.move(self.xDir+"\\jboss\\server.log", "jboss-logs-server.log")
            except Exception as inst:
                pass
            try:
                shutil.move(self.xDir+"\\acquisition\\au.log", "jboss-logs-au.log")
            except Exception as inst:
                pass
            try:
                shutil.move(self.xDir+"\\jboss\\server_mega.log", "oncommand-logs-server_mega.log")
            except Exception as inst:
                pass
            try:
                shutil.move(self.xDir+"\\server\\ocumserver.log.gz", "oncommand-logs-ocumserver.log.gz")
            except Exception as inst:
                pass
            sucess = self.extractFile( "oncommand-logs-ocumserver.log.gz" )
            if ( not success ):
                self.textBox.setText("\n Failed to extract files - see console for error\n")
                self.textBox.enableOkButton()
                return
            try:
                shutil.move(self.xDir+"\\server\\ocum-error.log", "oncommand-logs-ocum-error.log")
            except Exception as inst:
                pass
            try:
                shutil.rmtree("mysql")
                shutil.rmtree("server")
                shutil.rmtree("jboss")
                shutil.rmtree("acquisition")
            except Exception as inst:
                pass
        else:
            wx.MessageBox("Unknown product version in support bundle: " + str(sbVersion))

        self.textBox.setText("-----------------------------------------------------------------\n")
        self.textBox.setText("Collapsing SQL file:")

        # The directory should now contain a bunch of *.sql files.  We need to copy them
        # into one large file for the sql lite 
        filenames = self.getSqlFileNames()
        with open(SQL_FILE_NAME, 'w', encoding='utf8') as outfile:
            for fname in filenames:
                if ( fname == SQL_FILE_NAME ): continue
                self.textBox.setText("\n    collapsing: " + fname)
                with open(fname, encoding='utf8') as infile:
                    for line in infile:
                        outfile.write(line)

        self.textBox.setText("\n\nCompleted!")
        time.sleep(5)
        self.textBox.Hide()

        os.chdir(BASE_DIR)
        self.finished = True
        self.callback( self.parent )
        return

    def getReleaseVersionOfZip( self ):
        # Need to get the release version from the x-headers.data.txt file, this could take a
        # while since 7z will actually go through the whole archive and just ignore everything
        print(os.getcwd())
        self.extractFile( self.zFileName, "x-headers-data.txt" )
        headers = open("x-headers-data.txt", "r", encoding='utf8')
        line = headers.readline()
        version = None
        while line:
            if ( "product-version" in line ):
                # Format is like:
                #       7.2P1
                #       7.4.N171109.1600
                pversion= line.split(": ")[1];
                version = eval(pversion[:3])
                self.textBox.setText("\n-----------------------------------------------------------------\n")
                self.textBox.setText("==> Detected Product Version: " + str(version) + "\n");
                self.textBox.setText("-----------------------------------------------------------------\n\n")
                break
            line = headers.readline()

        return version

    def getSqlFileNames( self ):
        dirFiles = os.listdir(os.getcwd())
        sqlFiles = []
        for f in dirFiles:
            if ("7z" not in f and "sql" in f):
                sqlFiles.append(f)
        return sqlFiles

    def extractFiles( self, zFileName, fileNames ):
        for fileName in fileNames:
            success = self.extractFile(zFileName, fileName)
            if ( not success ):
                return success
            self.textBox.setText("-----------------------------------------------------------------\n")
        return True

    def extractFile( self, zFileName, fileName=None ):
        proc = None
        if ( fileName != None ):
            self.textBox.setText(" Working on extracting: " + fileName + "\n")
            print(os.getcwd())
            print(BASE_DIR + "\\7z.exe"+" x"+" "+zFileName+" -aoa "+fileName)
            proc = subprocess.Popen([BASE_DIR + "\\7z.exe", "x", zFileName, "-aoa", fileName], stderr=subprocess.STDOUT, stdout=subprocess.PIPE )

        else:
            print(BASE_DIR + "\\7z.exe"+" x"+" "+zFileName+" -aoa")
            proc = subprocess.Popen([BASE_DIR + "\\7z.exe", "x", zFileName, "-aoa"], stderr=subprocess.STDOUT, stdout=subprocess.PIPE )

        stdout, stderr = proc.communicate()
        sys.stdout.flush()
        output = ""
        outputDecoded = stdout.decode('utf-8')
        for line in outputDecoded.split("\n"):
            output = output + line
            if ( line != '' ):
                if ( "Skip" not in line and "7-Zip" not in line ):
                    self.textBox.setText(line)
            else:
                break
        

        if (proc.returncode != 0):
            print("Failed to extract data: " + proc.returncode) 
            return False


        # See if there was an error extracting.  the line should contain something like:
        #    "No files to process"
        if ( "No files to process" in output ):
            return True

        # Due to file system cache, do not want to return until the file exists.
        if (fileName != None):
            while (not os.path.exists(fileName)):
                print("File does not exist yet, sleeping")
                time.sleep(1)

        return True



################################################################################
# Table Load class that populates the information for the tables in the background
# this way we do not block the main item.
################################################################################
class ViewerTableLoader(threading.Thread):
    def __init__(self, parent, table ):
        self.parent = parent
        self.selected = table
        threading.Thread.__init__(self)
        return

    def parseFilter( self, filter ):
        # Make sure there are no invalued SQL commands
        if ( "||" in filter or "&&" in filter ):
            wx.MessageBox("Filter contains invalid SQL statements")
            return ("", False)
        # Now build the eval string
        array = [" WHERE"]
        skip = 0
        index = 0
        processTime = False
        # Walk the string and make it into a sql string
        pattern = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
        filterArray = pattern.split(filter)[1::2]
        conditions = ['=', '>', '<', '<=', '>=', '!=' ]
        for s in filterArray:
            if ( skip == 2 ):
                skip = 0
                continue
            # Skip after an expression
            if ( skip == 1 ):
                array.append(s)
                skip = 0
                index += 1
                continue
            # Need to convert the python syntax to mysql
            if ( (s == "=") ): 
                # Make sure that the column exists
                found = 0
                for i in range(len(self.parent.dbViewerColumns)):
                    if (self.parent.dbViewerColumns[i].lower() == array[index].lower()):
                        found = 1
                        break
                if ( found == 1 ):
                    array.append("=")
                    skip = 1
                else:
                    array.pop()
                    index -= 1
                    skip = 2
                    # Check to see if there was an and/or added that we need to
                    # remove
                    if ( array[index] == "and" or array[index] == "or" ):
                        array.pop()
                    continue
            elif ( (s == "and") or (s == "or") ):
                # If we have not added anything to the list, then ignore this
                if ( index == 0 ):
                    continue
                array.append(s) 
            elif ( "time" in s or "Time" in s):
                # If we are dealing with a time filter, and they entered in a string value
                # like 02-05-15 00:00:00 then we need to convert to a long value.
                #print(s)
                array.append(s) 
                processTime = True
            elif ( processTime == True and s not in conditions ):
                #print(s)
                # Presumably if we got here, we are processing a time request.  So we want to 
                # convert it.  The expression will be handled above.
                if ( "-" not in s ):
                    wx.MessageBox("Invalid Date Format: 'MM-DD-YYYY' or 'MM-DD-YYYY HH:MM:SS' (02-03-2015 00:00:00)")
                    return ("", False)
                dateVal = None 
                if ( ":" in s ):
                    dateVal = datetime.datetime.strptime( s.strip('"'), "%m-%d-%Y %H:%M:%S" )
                else:
                    dateVal = datetime.datetime.strptime( s, "%m-%d-%Y" )
                #print(time.mktime(dateVal.timetuple()) * 1000)
                array.append(str(time.mktime(dateVal.timetuple()) * 1000))
                processTime = False
            else:
                array.append(s) 
            index += 1

        if ( len(array) == 1 ):
            where = ""
        else:
            where = " ".join(array)
        return (where, True)

    def run(self):
        self.parent.dbTableTree.Enable(False)
        self.parent.dbViewerTableTimerStopped = 0
        # Get the number of rows in this table
        self.parent.setGauge( 0 )
        self.parent.currentItemsLabel.SetLabel( "0" )
        self.parent.totalItemsLabel.SetLabel( "0" )

        # If there is a preFilter checked, make sure that we look at the filter
        # text to see if there is one
        where = ""
        if ( (self.parent.isDbViewerPreFilterChecked == True) and (self.parent.filterText.GetValue() != "") ):
            where, status = self.parseFilter( self.parent.filterText.GetValue())
            if ( status == False ):
                # Parse Filter failed
                self.parent.stopDbViewerTableTimer = 0
                self.parent.dbViewerTableTimerStopped = 1
                self.parent.dbViewerQueryInProgress = 0
                self.parent.dbTableTree.Enable(True)
                return

        table = self.parent.dbViewerTableSelected
        ltable = lower(table)

        cmd = ""
        cmd = "SELECT COUNT(*) FROM " + table + where 
                
        rows = self.parent.executeAll( cmd )
        if ( rows[0][0] == 'Error' or rows[0] == 'Error'):
            # Request was empty
            self.parent.stopDbViewerTableTimer = 0
            self.parent.dbViewerTableTimerStopped = 1
            self.parent.dbViewerQueryInProgress = 0
            self.parent.dbTableTree.Enable(True)
            return
        count = int(rows[0][0])
        self.parent.totalItemsLabel.SetLabel( str(count) )
        
        if ( count > 0 and count < 1000 ):
            cmd = "SELECT * FROM " + table + where 
            conn = self.parent.executeForFetching( cmd )
            if ( conn == None ):
                self.parent.stopDbViewerTableTimer = 0
                self.parent.dbViewerTableTimerStopped = 1
                self.parent.dbViewerQueryInProgress = 0
                self.parent.dbTableTree.Enable(True)
                return
            index = 0
            for i in range(0, count):
                if ( self.parent.stopDbViewerTableTimer == 1 ):
                    break
                value = self.parent.fetchOne(conn)
                if ( len(value) == 0 ):
                    continue
                #print(value)
                col = 1
                lcolumn = lower(str(self.parent.dbViewerColumns[0]))
                setitem = decodeColumnValue( self.parent, value[0], ltable, lcolumn )
                self.parent.dbValueList.InsertItem( index, str(setitem) )
                self.parent.dbViewerRows.append( value )
                for item in value[1:]:
                    setitem = item
                    lcolumn = lower(str(self.parent.dbViewerColumns[col]))
                    if ( self.parent.stopDbViewerTableTimer == 1 ):
                        break

                    setitem = decodeColumnValue( self.parent, setitem, ltable, lcolumn )

                    try:
                        self.parent.dbValueList.SetItem( index, col, str(setitem) )
                    except Exception as inst:
                        pass
                        #print("Failed on " + str((index, col)) + " " + str(setitem))
                        #print(inst)
                    col = col + 1
                index = index + 1
                pos = (((i+1) * 100)/count)
                self.parent.setGauge( pos )
                self.parent.currentItemsLabel.SetLabel( str(i+1) )
            # Need to release the connection when done.
            conn.unlock()
        elif ( count > 1000 ) :
            start = 0
            end = 1000
            index = 0
            while ( 1 ):
                cmd = "SELECT * FROM " + self.parent.dbViewerTableSelected + " " + where + " LIMIT " + str(start) + ", " + str(end)
                conn = self.parent.executeForFetching( cmd )
                if ( conn == None ):
                    self.parent.stopDbViewerTableTimer = 0
                    self.parent.dbViewerTableTimerStopped = 1
                    self.parent.dbViewerQueryInProgress = 0
                    self.parent.dbTableTree.Enable(True)
                    return
                if ( self.parent.stopDbViewerTableTimer == 1 ):
                    break
                for i in range(0, (end-start+1) ):
                    if ( self.parent.stopDbViewerTableTimer == 1 ):
                        break
                    value = self.parent.fetchOne(conn)
                    if ( len(value) == 0 ):
                        continue
                    col = 1

                    lcolumn = lower(str(self.parent.dbViewerColumns[0]))
                    setitem = decodeColumnValue( self.parent, value[0], ltable, lcolumn )
                    self.parent.dbValueList.InsertItem( index, str(setitem) )
                    self.parent.dbViewerRows.append( value )
                    for item in value[1:]:
                        setitem = item
                        try:
                            lcolumn = lower(str(self.parent.dbViewerColumns[col]))
                        except Exception as inst:
                            print(self.parent.dbViewerColumns)
                            continue
                        if ( self.parent.stopDbViewerTableTimer == 1 ):
                            break

                        setitem = decodeColumnValue( self.parent, setitem, ltable, lcolumn )

                        try:
                            self.parent.dbValueList.SetItem( index, col, str(setitem) )
                        except Exception as inst:
                            pass
                            #print("failed on " + str(setitem))
                            #print(inst)

                        col = col + 1
                    index = index + 1
                    pos = (((index+1) * 100)/count)
                    self.parent.setGauge( pos )
                    self.parent.currentItemsLabel.SetLabel( str(index+1) )
                start = end + 1
                if ( end == (count - 1) ):
                    break
                elif ( (end + 1000) < count ):
                    end += 1000
                else:
                    end = count - 1
                # Need to release the connection when done.
                conn.unlock()
        else :
            # Nothing was found, but only show something if user had a filter.
            if ( where != "" ):
                wx.MessageBox( "Nothing returned" )
    
        self.parent.stopDbViewerTableTimer = 0
        self.parent.dbViewerTableTimerStopped = 1
        self.parent.dbViewerQueryInProgress = 0
        self.parent.dbTableTree.Enable(True)
        return

################################################################################
# Table Load class that populates the information for the tables in the background
# this way we do not block the main item.
################################################################################
class DbScriptsTableLoad(threading.Thread):
    def __init__(self, parent, selected ):
        self.parent = parent
        self.selected = selected
        threading.Thread.__init__(self)
        return

    def buildCountCmd(self, script):
        items = script.split()
        fromIndex = 0
        cmd = ""
        skip = False
        for item in items:
            if ( lower(item) == "select" ):
                cmd += item + " count(*) "
                skip = True
                continue
            elif ( lower(item) == "from" ):
                cmd += item + " "
                skip = False 
                continue
            if ( skip == True ): continue
            cmd += item + " "

        return cmd

    def run(self):
        self.parent.dbScriptsTableList.Enable(False)
        self.parent.dbScriptsTableTimerStopped = 0
        # Get the number of rows in this table
        self.parent.setGaugeScripts( 0 )
        self.parent.currentScriptsItemsLabel.SetLabel( "0" )
        self.parent.totalScriptsItemsLabel.SetLabel( "0" )

        keys = list(self.parent.scripts.keys())
        keys.sort()

        script = self.parent.scripts[keys[self.selected]]
        table = self.parent.getTable(script)
        ltable = table.lower()

        # Need to get the count for the script.  Normally the script should be of
        # the form:
        #   select * from Table where bla, bla
        #            or
        #   select a, b, c from Table where bla, bla
        #
        # so from the script, need to insert a count to get the count.
        cmd = self.buildCountCmd(script)
        rows = self.parent.executeAll( cmd )
        count = rows[0][0]
        self.parent.totalScriptsItemsLabel.SetLabel( str(count) )
        
        if ( count > 0 and count < 1000 ):
            conn = self.parent.executeForFetching( script )
            if ( conn == None ):
                self.parent.stopDbViewerTableTimer = 0
                self.parent.dbViewerTableTimerStopped = 1
                self.parent.dbViewerQueryInProgress = 0
                self.parent.dbTableTree.Enable(True)
                return
            index = 0
            for i in range(0, count):
                if ( self.parent.stopDbScriptsTableTimer == 1 ):
                    break
                value = self.parent.fetchOne(conn)
                if ( len(value) == 0 ):
                    continue
                #print(value)
                col = 1
                self.parent.dbScriptsValueList.InsertItem( index, str(value[0]) )
                self.parent.dbScriptsRows.append( value )
                for item in value[1:]:
                    setitem = item
                    lcolumn = lower(str(self.parent.dbScriptsColumns[col]))
                    if ( self.parent.stopDbScriptsTableTimer == 1 ):
                        break

                    setitem = decodeColumnValue( self.parent, setitem, ltable, lcolumn )

                    try:
                        self.parent.dbScriptsValueList.SetItem( index, col, str(setitem) )
                    except Exception as inst:
                        pass
                        #print("Failed on " + str((index, col)) + " " + str(setitem))
                        #print(inst)
                    col = col + 1
                index = index + 1
                pos = (((i+1) * 100)/count)
                self.parent.setGaugeScripts( pos )
                self.parent.currentScriptsItemsLabel.SetLabel( str(i+1) )
            # Need to release the connection when done.
            conn.unlock()
        elif ( count > 1000 ) :
            start = 0
            end = 1000
            index = 0
            while ( 1 ):
                cmd = script + " LIMIT " + str(start) + ", " + str(end)
                conn = self.parent.executeForFetching( cmd )
                if ( conn == None ):
                    self.parent.stopDbViewerTableTimer = 0
                    self.parent.dbViewerTableTimerStopped = 1
                    self.parent.dbViewerQueryInProgress = 0
                    self.parent.dbTableTree.Enable(True)
                    return
                if ( self.parent.stopDbScriptsTableTimer == 1 ):
                    break
                for i in range(0, (end-start+1) ):
                    if ( self.parent.stopDbScriptsTableTimer == 1 ):
                        break
                    value = self.parent.fetchOne(conn)
                    if ( len(value) == 0 ):
                        continue
                    col = 1
                    self.parent.dbScriptsValueList.InsertItem( index, str(value[0]) )
                    self.parent.dbScriptsRows.append( value )
                    for item in value[1:]:
                        setitem = item
                        lcolumn = lower(str(self.parent.dbScriptsColumns[col]))
                        if ( self.parent.stopDbScriptsTableTimer == 1 ):
                            break

                        setitem = decodeColumnValue( self.parent, setitem, ltable, lcolumn )

                        try:
                            self.parent.dbScriptsValueList.SetItem( index, col, str(setitem) )
                        except Exception as inst:
                            pass
                            #print("failed on " + str(setitem))
                            #print(inst)

                        col = col + 1
                    index = index + 1
                    pos = (((index+1) * 100)/count)
                    self.parent.setGauge( pos )
                    self.parent.currentScriptsItemsLabel.SetLabel( str(index+1) )
                start = end + 1
                if ( end == (count - 1) ):
                    break
                elif ( (end + 1000) < count ):
                    end += 1000
                else:
                    end = count - 1
                # Need to release the connection when done.
                conn.unlock()
        else :
            wx.MessageBox( "Nothing returned" )
    
        self.parent.stopDbScriptsTableTimer = 0
        self.parent.dbScriptsTableTimerStopped = 1
        self.parent.dbScriptsQueryInProgress = 0
        self.parent.dbScriptsTableList.Enable(True)
        return

################################################################################
# Table Load class that populates the information for the tables in the background
# this way we do not block the main item.
################################################################################
class BuildSummaryTable(threading.Thread):
    def __init__(self, parent):
        self.parent = parent
        threading.Thread.__init__(self)

        self.i = 0
        return

    def SetItem( self, item, value, bgcolor="white", fgcolor="black" ):
        self.parent.summaryList.InsertItem( self.i, item )
        self.parent.summaryList.SetItem( self.i, 1, str(value) )
        self.parent.summaryList.SetItemBackgroundColour( self.i, bgcolor)
        self.parent.summaryList.SetItemTextColour( self.i, fgcolor)
        self.i=self.i+1

        return

    def run( self ):
        version = "Not Available"
        if ( self.parent.opm_version != "" ):
            version = eval( self.parent.opm_version.split(".")[0] )

        # Keeps track of the total number of objects being monitored by this OPM or UM
        # Current list for OPM:
        #    https://wikid.netapp.com/w/User:Cgrindst/OPM_ObjectCount#OPM_Config_Object_Counts
        totalObjectCount = 0

        #
        # Setup the summary table.
        #
        self.parent.summaryList.ClearAll()
        self.parent.summaryList.InsertColumn( 0, "Item of Interest", wx.LIST_FORMAT_LEFT, 600 )
        self.parent.summaryList.InsertColumn( 1, "Value", wx.LIST_FORMAT_CENTER, 200 )

        # Current DB time
        time = self.parent.executeAll( "select now()" )[0]
        self.SetItem( "Current DB Time", str(time[0]), "#C0C0C0" )

        # Blank
        self.SetItem( "", "" )

        self.SetItem( "Database Versions", "", "#C0C0C0" )
        self.SetItem( "    netapp_model", self.parent.versionString )
        if ( self.parent.opm_version != "" ):
            self.SetItem( "    UM Performance", self.parent.opm_version )
        scaleMonitorVersion = self.parent.executeAll( "select * from scalemonitor.version where id=1" )[0]
        self.SetItem( "    Scale Monitor", str(scaleMonitorVersion[1]) + "." + str(scaleMonitorVersion[2]) + "." + str(scaleMonitorVersion[3]) + "." + str(scaleMonitorVersion[4]))
        if ("vmware_model" in DATABASES):
            vmwareVersion = self.parent.executeAll( "select * from vmware_model.version" )[0]
            self.SetItem( "    VmWare", str(vmwareVersion[1]) + "." + str(vmwareVersion[2]) + "." + str(vmwareVersion[3]) + "." + str(vmwareVersion[4]))

        #Blank
        self.SetItem( "", "" )

        self.SetItem( "Database Breakdown:", "", "#C0C0C0" )
        # Number of clusters
        count = self.parent.executeAll( "select count(*) from netapp_model.cluster" )[0]
        self.SetItem( "    Clusters", count[0] )
        names = self.parent.executeAll( "select name from netapp_model.cluster" )
        #print(names)
        for name in names:
            self.SetItem( "                "+name[0], "", fgcolor="blue" )
        count = self.parent.executeAll( "select count(*) from netapp_model.node where objState != 'DEAD'" )[0]
        self.SetItem( "    Nodes", count[0] )
        nAndVs = self.parent.executeAll( "select name, version from netapp_model.node where objState != 'DEAD'" )
        for item in nAndVs:
            self.SetItem( "                "+item[0] + "  -  (" + item[1] + ")", "", fgcolor="blue" )
        count = self.parent.executeAll( "select count(*) from netapp_model.node where objState = 'DEAD'" )[0]
        self.SetItem( "    Deleted Nodes", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.vserver where objState != 'DEAD'" )[0]
        totalObjectCount += int(count[0]);
        self.SetItem( "    VServers", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.vserver where objState = 'DEAD'" )[0]
        self.SetItem( "    Deleted VServers", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.network_port" )[0]
        totalObjectCount += int(count[0]);
        self.SetItem( "    Network Ports", count[0] )

        count = self.parent.executeAll( "select count(*) from netapp_model.lif" )[0]
        totalObjectCount += int(count[0]);
        self.SetItem( "    LIFs", count[0] )

        count = self.parent.executeAll( "select count(*) from netapp_model.network_lif" )[0]
        self.SetItem( "    Network LIFs", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.fcp_port" )[0]
        totalObjectCount += int(count[0]);
        self.SetItem( "    FCP Ports", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.fcp_lif" )[0]
        self.SetItem( "    FCP LIFs", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.aggregate where objState != 'DEAD'" )[0]
        totalObjectCount += int(count[0]);
        self.SetItem( "    Aggregates", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.aggregate where objState = 'DEAD'" )[0]
        self.SetItem( "    Deleted Aggregates", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.plex" )[0]
        self.SetItem( "    Plexes", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.disk where objState != 'DEAD'" )[0]
        totalObjectCount += int(count[0]);
        self.SetItem( "    Disks", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.disk where objState = 'DEAD'" )[0]
        self.SetItem( "    Deleted Disks", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.volume where objState != 'DEAD'" )[0]
        totalObjectCount += int(count[0]);
        self.SetItem( "    Volumes", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.volume where objState='DEAD'" )[0]
        self.SetItem( "    Deleted Volumes", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.volume where isJunctionActive=1" )[0]
        self.SetItem( "    Exported NFS Volumes", count[0] )

        count = self.parent.executeAll( "select count(*) from netapp_model.lun where objState != 'DEAD'" )[0]
        totalObjectCount += int(count[0]);
        self.SetItem( "    LUNs", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.lun where objState='DEAD'" )[0]
        self.SetItem( "    Deleted LUNs", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.lun_map where objState != 'DEAD'" )[0]
        totalObjectCount += int(count[0]);
        self.SetItem( "    LUN Maps", count[0] )

        if ( self.parent.version >= 7.4 ):
            count = self.parent.executeAll( "select count(*) from netapp_model.namespace where objState != 'DEAD'" )[0]
            totalObjectCount += int(count[0]);
            self.SetItem( "    Namespaces", count[0] )
            count = self.parent.executeAll( "select count(*) from netapp_model.namespace where objState='DEAD'" )[0]
            self.SetItem( "    Deleted Namespaces", count[0] )

        count = self.parent.executeAll( "select count(*) from netapp_model.cifs_share where objState != 'DEAD'" )[0]
        self.SetItem( "    CIFS Shares", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.cifs_share where objState = 'DEAD'" )[0]
        self.SetItem( "    Deleted CIFS Shares", count[0] )

        self.SetItem( "", "" )
        self.SetItem( "    Total DB Objects that affect scale", str(totalObjectCount) )

        self.SetItem( "", "" )

        self.SetItem( "QOS Breakdown:", "", "#C0C0C0" )
        if ( self.parent.version < 7.3 ):
            count = self.parent.executeAll( "select count(*) from netapp_model.qos_volume_workload" )[0]
            self.SetItem( "    QoS Volume Workloads", count[0] )
        else:
            count = self.parent.executeAll( "select count(*) from netapp_model.qos_workload" )[0]
            self.SetItem( "    QoS Workloads", count[0] )
        count = self.parent.executeAll( "select count(*) from netapp_model.qos_workload_detail" )[0]
        self.SetItem( "    QOS Workload Details", count[0] )

        self.SetItem( "", "" )

        if ( self.parent.opm_version != "" ):
            self.SetItem( "Performance Breakdown:", "", "#C0C0C0" )
            try:
                count = self.parent.executeAll( "select count(*) from opm.change_event" )[0]
                self.SetItem( "    Change Events", count[0] )
                count = [0]
                if ( self.parent.version <= 7.3 ):
                    count = self.parent.executeAll( "select count(*) from opm.continuous_event_occurrence" )[0]
                    self.SetItem( "    Incidents", count[0] )
                if ( self.parent.version >= 7.2 ):
                    count = self.parent.executeAll( "select count(*) from opm.continuous_event_participant" )[0]
                else:
                    count = self.parent.executeAll( "select count(*) from opm.event_participant" )[0]
                self.SetItem( "    Event Participants", count[0] )
                count = self.parent.executeAll( "select count(*) from opm.forecast" )[0]
                self.SetItem( "    Forecasts", count[0] )
    
                if ( version >= 2 ):
                    count = self.parent.executeAll( "select count(*) from opm.threshold" )[0]
                    self.SetItem( "    Thresholds", count[0] )
                    count = self.parent.executeAll( "select count(*) from opm.threshold_policy" )[0]
                    self.SetItem( "    Policies", count[0] )

            except:
                self.SetItem( "    Change Events", "0" )
                self.SetItem( "    Incidents", "0" )
                self.SetItem( "    Event Participants", "0" )
                self.SetItem( "    Event Relationships", "0" )
                self.SetItem( "    Forecasts", "0" )
                self.SetItem( "    Thresholds", "0" )
                self.SetItem( "    Policies", "0" )

        self.SetItem( "", "" )
        return

################################################################################
# This will convert a mysql file and create the sqlite dbs
################################################################################
class ConvertMySqlToSqLite(threading.Thread):
    def __init__(self, parent, bundleDir, fileName, doneFunction ):
        self.bundleDir = bundleDir
        self.parent = parent
        self.fileName = fileName
        self.doneFunction = doneFunction
        threading.Thread.__init__(self)

        self.stop = False
        return

    def cancel(self):
        self.stop = True
        print("Stopping Convert")
        self.parent.progressBar.Destroy()
        return

    def run( self ):
        print("Starting")
        self.parent.progressBar.setProgressText("Discoverying File")
        self.parent.progressBar.Refresh()
        numberOfLines = self.parent.numberOfLinesInFile( self.fileName )
        self.parent.progressBar.setProgressText("Reading in MySQL file")
        # Now start the conversion
        inFile = open(self.fileName, "r", encoding='utf8')
        outFile = None
        self.sqlFiles = []
        nopeList = [ 'BEGIN TRANSACTION',
                     'COMMIT',
                     'LOCK TABLES',
                     'commit;',
                     'autocommit',
                     'CREATE UNIQUE INDEX', 
                     '--', 
                     'USE '
                   ]
        supportedDbs = [ 'acquisition',
                         'netapp_model',
                         'netapp_performance',
                         'opm',
                         'ocum',
                         'vmware_model',
                         'vmware_performance',
                         'scalemonitor'
                       ]
        supportedDbs = [ 'netapp_model'
                       ]
        createTable = []
        cacheCreateTable = False
        skipDatabase = False
        multiLineComment = False

        CLEAN_HTTP_TAGS = re.compile('<.*?>')

        # Create a temp directory for the dbs
        os.chdir(self.bundleDir)
        try:
            shutil.rmtree("sqLiteDbs")
        except OSError as exc:
            #print(" Failure: " + str(exc))
            if ( exc.errno == errno.EEXIST ): pass

        try:
            os.mkdir("sqLiteDbs")
        except OSError as exc:
            #print(" Failure: " + str(exc))
            if ( exc.errno == errno.EEXIST ): pass

        lineCount = 0;
        for line in inFile:
            lineCount = lineCount + 1
            #print(str(lineCount) + " - " + line)
            if ( self.stop == True ): return;
            self.parent.progressBar.setProgressGauge((lineCount*100)/numberOfLines)
            # Check if create database is in line, if so, we need to start a 
            # new file.
            if ( "CREATE DATABASE" in line or "USE `" in line or "Database: " in line and "Current " not in line):
                # CREATE DATABASE /*!32312 IF NOT EXISTS*/ `host_data` /*!40100 DEFAULT CHARACTER SET utf8 */;
                dtaBaseName = None
                if ( "CREATE" in line ):
                    if ( "utf8" in line ):
                        dataBaseName = line.split()[6][1:-1]
                    else:
                        dataBaseName = line.split()[5][:-1]
                elif ( "Database: " in line ):
                    # In this case, this is a support file that has been concated.
                    dataBaseName = line.split(":")[2].lstrip().rstrip()
                else:
                    dataBaseName = line.split()[1][1:-2]
                #print("Database name: " + dataBaseName)
                if ( dataBaseName in supportedDbs ):
                    dataBaseFileName = "sqLiteDbs/" + dataBaseName + ".db"
                    #print("New DBfile = " + dataBaseFileName)
                    if ( outFile != None ):
                        outFile.close()
                    self.parent.progressBar.setProgressText("Reading in MySQL file (" + dataBaseName + ")")
                    if ( os.path.isfile(dataBaseFileName) ):
                        outFile = open(dataBaseFileName, "a", encoding='utf8')
                    else:
                        outFile = open(dataBaseFileName, "w", encoding='utf8')
                    if ( dataBaseFileName not in self.sqlFiles ):
                        outFile.write("PRAGMA synchronous=OFF;\n")
                        outFile.write("PRAGMA count_changes=OFF;\n")
                        outFile.write("PRAGMA journal_mode=MEMORY;\n")
                        outFile.write("PRAGMA temp_store=MEMORY;\n")
                        #print("OUTFILE: " + outFile.name)
                        self.sqlFiles.append( dataBaseFileName )
                    skipDatabase = False
                    continue
                else:
                    skipDatabase = True
                    continue

            if ( skipDatabase == True ): continue

            # See if we should skip this line based on the nope list
            skip = True
            for nope in nopeList:
                if (nope in line): 
                    skip = True
                    break
                else:
                    skip = False

            if (skip == True): continue


            # Look to see if we have reached the end of the create table. Have seen where
            # MEGA uses ';' in a comment.
            if ( cacheCreateTable == True and ";" in line and "COMMENT" not in line):
                createTable.append( line )
                # Need to post process and remove any partition information.
                if ( "*/" in line and multiLineComment == True ):
                    multiLineComment = False
                newCreateTable = []
                for s in createTable:
                    #print("CreateTable: " + s)
                    if ( "PARTITION" in s ): continue
                    if ( "ENGINE" in s ): continue
                    if ( "UNIQUE" in s ): continue
                    # If there is a comment, lets remove for now.
                    if ( "COMMENT" in s ): 
                        if ( ',' in s ):
                            s = s.split("COMMENT")[0] + ",\n"
                        else:
                            s = s.split("COMMENT")[0] + "\n"
                    if ( "CHARACTER SET" in s ):
                        s = s.replace("CHARACTER SET utf8", "")
                    if ( "enum" in s and "(" in s ):
                        s = s[0:s.index("enum")] + "TEXT" + s[s.index(")")+1:]
                    newCreateTable.append(s)
                newCreateTable.append(");\n")
                # Look to see if the second to last line has an invalid ,
                #if ( ("PRIMARY" in newCreateTable[-2] or "UNIQUE" in newCreateTable[-2]) and newCreateTable[-2][-2] == ',' ):
                if ( newCreateTable[-2][-2] == ',' ):
                    newCreateTable[-2] = newCreateTable[-2][:-2] + "\n"
                for s in newCreateTable:
                    outFile.write(s)
                createTable = []
                cacheCreateTable = False
                continue

            # Need to cache the create table statements so we can post process.
            if ( "CREATE TABLE" in line ):
                #print("***** CREATE TABLE IN LINE")
                cacheCreateTable = True
 
            # If the line contains a /* and */ then ignore
            if ( "/*!" in line and "*/" in line ):
                #print(line)
                #print("dropping 0")
                continue

            # If this is a multi-line comment then we need to track until it is done
            if ( "/*!" in line and 
                 "INSERT" not in line):
                multiLineComment = True
                #print(line)
                #print("dropping 1")
                #time.sleep(5)
                continue
            # If this is a multi-line comment then we need to track until it is done
            if ( "*/" in line and 
                 multiLineComment == True and
                 "INSERT" not in line ):
                multiLineComment = False
                #print(line)
                #print("dropping 2")
                continue
            if ( multiLineComment == True ):
                #print(line)
                #print("dropping 3")
                #time.sleep(5)
                continue

            # Make sure to ignore any "SET" commands
            if ( line[:3] == "SET" ):
                continue

            # Need to ignore the KEY table constraint
            if ( "KEY" in line and ("PRIMARY" not in line and "UNIQUE" not in line and "COMMENT" not in line) ):
                continue
            if ( "UNIQUE KEY" in line ):
                line = "  " + line.split()[0] + " " + line.split()[3] + "\n"
            # If the line contains the " ON " command, need to remove
            if ( " ON " in line ):
                line = line.split(" ON ")[0] + ",\n"

            # If this is an "INSERT INTO" then we need to make sure it is not too long
            # because SqLite can not handle it.
            size = len(line)
            if ( "INSERT INTO" in line and size > 1000 and "ds_type_attrs" not in line ):
                if ( 'application_record' in line or 'forecast' in line ): continue
                line = re.sub(CLEAN_HTTP_TAGS, '', line)
                #line = line.replace('\'', '\"')
                # There is a problem where the aggregate data contains bad characters
                if ( 'aggregate' in line ):
                    line = line.replace("\'d!", "")
                #print(len(line))
                # Get the first part:
                strSplit = line.split("VALUES")
                insertStr = (strSplit[0] + " VALUES ").replace('`', '')
                count = 0
                outStr = insertStr
                #print("num of inserts = " + str(len(strSplit[1].split("),("))))
                INSERT_COUNT = 50
                if ( 'forecast' in insertStr ):
                    INSERT_COUNT = 1
                outFile.write("BEGIN TRANSACTION;\n")
                for v in strSplit[1].split("),("):
                    if ( count == INSERT_COUNT ):
                        #outStr = outStr.replace('`', '')
                        if ( 'forecast' not in insertStr ):
                            outFile.write(outStr[:-2] + ";\n")
                        else:
                            outFile.write(outStr + ");\n")
                        outFile.write("COMMIT TRANSACTION;\n")
                        outFile.write("BEGIN TRANSACTION;\n")
                        count = 0
                        outStr = insertStr + " ("
                    if ( 'forecast' not in insertStr ):
                        # See if there is a semi-colon at the end of the string.
                        if ( ";" not in v[-5:] ):
                            outStr = outStr + v + "),("
                        else:
                            outStr = outStr + v
                    else:
                        outStr = outStr + v
                    count = count + 1
                
                # Now if the count != 20 and not 0 then we need to flush the last
                # section
                if ( count != 0 and count != INSERT_COUNT ):
                    #print(outStr)
                    outStr = outStr.replace('`', '')
                    # See if there is a semi-colon at the end of the string.
                    if ( ";" not in outStr[-5:] ):
                        outFile.write(outStr + ";\n")
                    else:
                        outFile.write(outStr + "\n")
                outFile.write("COMMIT TRANSACTION;\n")
                continue
            elif ("INSERT INTO" in line ) :
                if ( 'application_record' in line ): continue
                outFile.write("BEGIN TRANSACTION;\n")
                line = line.replace('0x01', '1')
                line = line.replace('0x00', '0')
                line = re.sub(CLEAN_HTTP_TAGS, '', line)
                #line = line.replace('\'', '\"')
                outFile.write(line)
                outFile.write("COMMIT TRANSACTION;\n")
                continue
            

            line = re.sub(r"([^'])'t'(.)", "\1THIS_IS_TRUE\2", line)
            line = line.replace('THIS_IS_TRUE', '1')
            line = re.sub(r"([^'])'f'(.)", "\1THIS_IS_FALSE\2", line)
            line = line.replace('THIS_IS_FALSE', '0')
            # Need to convert the data types
            # http://stackoverflow.com/questions/1942586/comparison-of-database-column-types-in-mysql-postgresql-and-sqlite-cross-map
            if ( 'varchar' in line ):
                line = re.sub(r"varchar\(\d+\)", "TEXT", line)
            line = line.replace('float', 'REAL')
            line = re.sub(r"bigint\(\d+\)", "INTEGER", line)
            line = re.sub(r"smallint\(\d+\)", "INTEGER", line)
            line = re.sub(r"tinyint\(\d+\)", "INTEGER", line)
            line = re.sub(r"bit\(\d+\)", "INTEGER", line)
            line = re.sub(r"int\(\d+\)", "INTEGER", line)
            line = re.sub(CLEAN_HTTP_TAGS, '', line)
            line = line.replace("b\'1\'", "\'1\'")
            line = line.replace("b\'0\'", "\'0\'")
            line = line.replace('0x01', '1')
            line = line.replace('0x00', '0')
            line = line.replace('mediumtext', 'TEXT')
            line = line.replace('unsigned', '')
            line = line.replace('AUTO_INCREMENT', '')
            line = line.replace(' timestamp', ' TEXT')
            line = line.replace('COLLATE', '')
            line = line.replace('utf8_bin', '')
            line = line.replace('`', '')
            #line = line.replace('\'', '\"')
            line = line.replace('blob', 'BLOB')
            line = line.replace('-', '_')
            if ( outFile != None ):
                if (cacheCreateTable == False ):
                    outFile.write(line)
                else:
                    #print("Adding to createTable....")
                    createTable.append(line)

        if ( outFile != None ):
            outFile.close()
        time.sleep(1)
        # Now that we have all of the files broken out, we need to now take
        # the sql files and create sqlite DB's out of them.  We do this by 
        # starting sqlite with a name "opm.sqlite" and then read in the file.
        # Need to do this for all the files in the self.sqlFiles
        self.convertToSqliteDbs()

        if ( self.doneFunction != None and self.stop != True ):
            self.doneFunction()
        self.parent.progressBar.Destroy()

        # Successfully converted, now create a file that signifys that this is 
        # a valid bundle directory
        os.chdir(self.bundleDir)
        file = open(BUNDLE_SENTINAL,"w", encoding='utf8')
        file.write("SUCCESS")
        file.close()

        os.chdir(BASE_DIR)
        return

    def convertToSqliteDbs(self):
        self.parent.progressBar.setProgressText("Convert SQL files to Sqlite Databases")
        self.parent.progressBar.setProgressGauge(0)
        self.dbFiles = []
        dbCount = 0
        os.chdir("sqLiteDbs")
        for db in self.sqlFiles:
            self.parent.progressBar.setProgressText("Convert SQL file to Sqlite Databases (" + (db.split("/")[1]).split(".")[0] + ")")
            if ( self.stop == True ): return
            dbCount = dbCount + 1
            self.parent.progressBar.setProgressGauge((100*dbCount)/len(self.sqlFiles))
            # Create a sqlite db filename
            sqliteDb = db.split(".")[0] + ".sqlite"
            self.parent.sqLiteDbFiles.append(sqliteDb.split("/")[1])
            print(BASE_DIR + "\\sqlite3.exe " + sqliteDb.split("/")[1] + ' \".read ' + db.split("/")[1] + '\"')
            os.system(BASE_DIR + "\\sqlite3.exe " + sqliteDb.split("/")[1] + ' \".read ' + db.split("/")[1] + '\"')
            #wx.MessageBox("AFTER")
            print("After")
        return

###############################################################################
###############################################################################
# Thread used to keep track of DB timeout (10 Minutes)
###############################################################################
###############################################################################
class MonitorDBTimeout(threading.Thread):
    def __init__(self, parent):
        self.parent = parent
        self.running = True
        threading.Thread.__init__(self)
        return
    
    def stop(self):
        self.running = False
        return

    def run(self):
        while (self.running):
            if ( self.parent.connected and not self.parent.sqLiteSelected ):
                self.parent.dbTimeoutCounter = self.parent.dbTimeoutCounter + 5
                if ( self.parent.dbTimeoutCounter >= 900 ):
                    # Make sure we do not time out, make a simple call to the db
                    try:
                        rows = self.parent.executeAll( "SELECT now()" )
                    except:
                        wx.MessageBox( "Your connection to the DB has timed out, please connect again (use the connect button)" )
                        self.dbTimeoutCounter = 0
                        self.parent.connected = False
            time.sleep(5)
        return

###############################################################################
###############################################################################
# A class to help syncronize the data base access
###############################################################################
###############################################################################
class DbAccess:
    def __init__(self, dbConn, dbWorker, db):
        self.tlock = threading.Lock()
        self.dbConn = dbConn
        self.dbWorker = dbWorker
        self.db = db

    def isLocked( self ):
        return self.tlock.locked()

    def lock( self ):
        self.tlock.acquire()
        return

    def unlock( self ):
        self.tlock.release()
        return

###############################################################################
###############################################################################
# Main class 
###############################################################################
###############################################################################
class UmDbSpy(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: UmDbSpy.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.mainPanel = wx.Panel(self, -1)

        #
        # Create the Notebook
        #
        self.noteBook = wx.Notebook(self.mainPanel, -1, style=wx.NB_NOPAGETHEME)

        self.dbSummaryNoteBookPanel1 = wx.Panel(self.noteBook, -1)
        self.dbViewerNoteBookPanel2 = wx.Panel(self.noteBook, -1)
        self.dbScriptsNoteBookPanel3 = wx.Panel(self.noteBook, -1)

        # Static boxes for summary panel
        self.dbSummaryInsideStaticBox = wx.StaticBox(self.dbSummaryNoteBookPanel1, -1, "")
        self.dbSummaryInsidePanel = wx.Panel(self.dbSummaryNoteBookPanel1, -1)

        # Static boxes for viewer panel
        self.dbViewerInsideStaticBox = wx.StaticBox(self.dbViewerNoteBookPanel2, -1, "")
        self.dbViewerInsidePanel = wx.Panel(self.dbViewerNoteBookPanel2, -1)

        # Static boxes for  script panel
        self.dbScriptsInsideStaticBox = wx.StaticBox(self.dbScriptsNoteBookPanel3, -1, "")
        self.dbScriptsInsidePanel = wx.Panel(self.dbScriptsNoteBookPanel3, -1)

        #
        # Static Boxs for DB Control
        #
        self.staticBoxAroundDBServerIP = wx.StaticBox(self.mainPanel, -1, "DB Server IP")
        self.staticBoxAroundDBServerIP.SetForegroundColour( wx.WHITE )
        self.staticBoxAroundUserName = wx.StaticBox(self.mainPanel, -1, "DB User Name")
        self.staticBoxAroundUserName.SetForegroundColour( wx.WHITE )
        self.staticBoxAroundDBPassword = wx.StaticBox(self.mainPanel, -1, "DB Password")
        self.staticBoxAroundDBPassword.SetForegroundColour( wx.WHITE )
        self.staticBoxDBControl = wx.StaticBox(self.mainPanel, -1, "DB Control")
        #self.staticBoxDBControl.SetBackgroundColour("#0D47A1")
        self.staticBoxDBControl.SetForegroundColour(wx.WHITE)
        self.staticBoxAroundNoteBook = wx.StaticBox(self.mainPanel, -1, "")

        # Static boxes for DB Viewer Tab
        self.staticBoxAroundFilter = wx.StaticBox(self.dbViewerInsidePanel, -1, "")
        self.staticBoxAroundDBTableListLable = wx.StaticBox(self.dbViewerInsidePanel, -1, "")
        self.staticBoxAroundDBTableValuesLable = wx.StaticBox(self.dbViewerInsidePanel, -1, "")
        self.staticBoxAroundTableProgress = wx.StaticBox(self.dbViewerInsidePanel, -1, "Table Progress")
        self.staticBoxAroundTableProgress.SetForegroundColour( wx.BLUE )
        self.staticBoxAroundEverything = wx.StaticBox(self.dbViewerInsidePanel, -1, "")
        
        # Static boxes for Scripts Tab
        self.staticBoxAroundScriptsFilter = wx.StaticBox(self.dbScriptsInsidePanel, -1, "")
        self.staticBoxAroundScriptsDBTableListLable = wx.StaticBox(self.dbScriptsInsidePanel, -1, "")
        self.staticBoxAroundScriptsDBTableValuesLable = wx.StaticBox(self.dbScriptsInsidePanel, -1, "")
        self.staticBoxAroundScriptsTableProgress = wx.StaticBox(self.dbScriptsInsidePanel, -1, "Script Progress")
        self.staticBoxAroundScriptsTableProgress.SetForegroundColour( wx.BLUE )
        self.staticBoxAroundScriptsEverything = wx.StaticBox(self.dbScriptsInsidePanel, -1, "")

        #
        # Menu Bar
        #
        self.UmDbSpyMenuBar = wx.MenuBar()
        self.SetMenuBar(self.UmDbSpyMenuBar)

        # File Menu 
        file = wx.Menu()
        self.menuChangeFontSelected = wx.MenuItem(file, wx.Window.NewControlId(), "Change Table Fonts", "Change the font size and type of the tables", wx.ITEM_NORMAL)
        file.Append(self.menuChangeFontSelected)
        self.menuDescribeSelected = wx.MenuItem(file, wx.Window.NewControlId(), "Describe Tables", "Display the description of all tables", wx.ITEM_NORMAL)
        file.Append(self.menuDescribeSelected)
        self.menuViewSqlLogsSelected = wx.MenuItem(file, wx.Window.NewControlId(), "View SQL Commands", "View SQL Commands that have been issued", wx.ITEM_NORMAL)
        file.Append(self.menuViewSqlLogsSelected)
        self.menuEditServerIPsSelected = wx.MenuItem(file, wx.Window.NewControlId(), "Edit Server IP Cache", "Edit the Server IPs cached", wx.ITEM_NORMAL)
        file.Append(self.menuEditServerIPsSelected)
        self.menuRefreshSummarySelected = wx.MenuItem(file, wx.Window.NewControlId(), "Refresh Summary Tab", "Refresh the Summary Tab data", wx.ITEM_NORMAL)
        file.Append(self.menuRefreshSummarySelected)
        file.AppendSeparator()
        self.Exit = wx.MenuItem(file, wx.Window.NewControlId(), "Exit", "Exit from UM DB Spy", wx.ITEM_NORMAL)
        file.Append(self.Exit)
        self.UmDbSpyMenuBar.Append(file, "File")

        # Tools Menu
        tools = wx.Menu()
        if ( sys.platform == 'win32' ):
            self.menuViewLogsSelected = wx.MenuItem(tools, wx.Window.NewControlId(), "View Application Logs", "View the logs from the server", wx.ITEM_NORMAL)
            tools.Append(self.menuViewLogsSelected)
            self.menuOpenCmdSelected = wx.MenuItem(tools, wx.Window.NewControlId(), "Open Command Console", "Open an OS command terminal", wx.ITEM_NORMAL)
            tools.Append(self.menuOpenCmdSelected)
        self.menuPythonRunnerSelected = wx.MenuItem(tools, wx.Window.NewControlId(), "Python Runner", "Open a Python 'like' terminal", wx.ITEM_NORMAL)
        tools.Append(self.menuPythonRunnerSelected)
        self.menuOpenSshSelected = wx.MenuItem(tools, wx.Window.NewControlId(), "Open SSH Terminal", "Open a SSH terminal", wx.ITEM_NORMAL)
        tools.Append(self.menuOpenSshSelected)
        #self.menuOpenSshTunnelSelected = wx.MenuItem(tools, wx.Window.NewControlId(), "Open SSH Tunnel", "Open a SSH tunnel", wx.ITEM_NORMAL)
        #tools.Append(self.menuOpenSshTunnelSelected)
        tools.AppendSeparator()
        self.menuOpenDbRequest = wx.MenuItem(tools, wx.Window.NewControlId(), "Open DB", "Open up a particular DB for viewing", wx.ITEM_NORMAL)
        tools.Append(self.menuOpenDbRequest)
        self.menuIssueDbRequest = wx.MenuItem(tools, wx.Window.NewControlId(), "Issue SQL Commands", "Directly issue SQL Commands", wx.ITEM_NORMAL)
        tools.Append(self.menuIssueDbRequest)
        self.menuVolumeViewerSelected = wx.MenuItem(tools, wx.Window.NewControlId(), "View All Volume Information", "View detailed information about all volumes", wx.ITEM_NORMAL)
        tools.Append(self.menuVolumeViewerSelected)
        self.menuScaleMonitorSelected = wx.MenuItem(tools, wx.Window.NewControlId(), "View The Scale Monitor Information", "View detailed information about how this UM is behaving", wx.ITEM_NORMAL)
        tools.Append(self.menuScaleMonitorSelected)
        self.UmDbSpyMenuBar.Append(tools, "Tools")

        scripts = wx.Menu()
        self.menuScriptsAdd = wx.MenuItem(file, wx.Window.NewControlId(), "Add", "Add a new script to the list of scripts", wx.ITEM_NORMAL)
        scripts.Append(self.menuScriptsAdd)
        self.menuScriptsRemove = wx.MenuItem(file, wx.Window.NewControlId(), "Remove Selected Script", "Remove the selected script from the list of scripts", wx.ITEM_NORMAL)
        scripts.Append(self.menuScriptsRemove)
        self.menuScriptsEdit = wx.MenuItem(file, wx.Window.NewControlId(), "Edit Selected Script", "Edit the selected script", wx.ITEM_NORMAL)
        scripts.Append(self.menuScriptsEdit)
        self.menuScriptsRename = wx.MenuItem(file, wx.Window.NewControlId(), "Rename Selected Script", "Rename the selected script", wx.ITEM_NORMAL)
        scripts.Append(self.menuScriptsRename)
        self.UmDbSpyMenuBar.Append(scripts, "Scripts")
        
        # Help menu.
        self.Help = wx.Menu()
        self.Help.AppendSeparator()
        self.HelpContext = wx.MenuItem(self.Help, wx.Window.NewControlId(), "Help Context", "", wx.ITEM_NORMAL)
        self.Help.Append(self.HelpContext)
        self.UmDbSpyMenuBar.Append(self.Help, "Help")

        #
        # Status Bar
        #
        self.statusBar = self.CreateStatusBar(1, 0)

        #
        # Main Widgets for DB Control
        #
        self.dbAccessRadioBoxPanel = wx.Panel(self.mainPanel, -1)
        self.dbAccessRadioBox = wx.RadioBox(self.dbAccessRadioBoxPanel, 
                                            -1, 
                                            "", 
                                            choices=["Remote DB", "Support Bundle"], 
                                            majorDimension=0, 
                                            style=wx.RA_SPECIFY_ROWS)
        #self.dbAccessRadioBox.SetBackgroundColour("#0D47A1")
        self.dbAccessRadioBox.SetForegroundColour("#b7ceec")
        self.dbServerIP = wx.ComboBox(self.mainPanel, -1, choices=[], style=wx.CB_DROPDOWN|wx.CB_SORT|wx.TE_PROCESS_ENTER)
        self.chromeButton = wx.BitmapButton(self.mainPanel, wx.Window.NewControlId(), wx.Bitmap(".\\images\\smallchrome.png", wx.BITMAP_TYPE_ANY))
        self.fireFoxButton = wx.BitmapButton(self.mainPanel, wx.Window.NewControlId(), wx.Bitmap(".\\images\\smallfirefox.gif", wx.BITMAP_TYPE_ANY))
        self.ieButton = wx.BitmapButton(self.mainPanel, wx.Window.NewControlId(), wx.Bitmap(".\\images\\smallie.jpg", wx.BITMAP_TYPE_ANY))

        self.dbSqLiteFileName = wx.TextCtrl(self.mainPanel, -1, "", style=wx.TE_PROCESS_ENTER, size=(200, -1))
        self.dbSqLiteFileName.Hide()
        self.dbSqLiteFileButton = wx.BitmapButton(self.mainPanel, -1, wx.Bitmap(".\\images\\file.jpg", wx.BITMAP_TYPE_ANY))
        self.dbSqLiteFileButton.Hide()

        self.dbUserName = wx.TextCtrl(self.mainPanel, -1, "", style=wx.TE_PROCESS_ENTER)
        self.dbPassword = wx.TextCtrl(self.mainPanel, -1, "", style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)
        self.connectButton = wx.Button(self.mainPanel, -1, "Connect")

        # Widgets for the DB Summary tab.
        self.summaryList = wx.ListCtrl(self.dbSummaryInsidePanel, -1, style=wx.LC_REPORT)

        # Widgets for the DBViewer tab
        self.dbListLabel = wx.StaticText(self.dbViewerInsidePanel, -1, "Databases", style=wx.ALIGN_CENTRE)
        self.dbTableLabel = wx.StaticText(self.dbViewerInsidePanel, -1, "Table Entries", style=wx.ALIGN_LEFT)
        self.currentItemsLabel = wx.StaticText(self.dbViewerInsidePanel, -1, "0", style=wx.ALIGN_CENTRE)
        self.ofLabel = wx.StaticText(self.dbViewerInsidePanel, -1, " of ", style=wx.ALIGN_CENTRE)
        self.totalItemsLabel = wx.StaticText(self.dbViewerInsidePanel, -1, "0", style=wx.ALIGN_CENTRE)
        self.zeroLabel = wx.StaticText(self.dbViewerInsidePanel, -1, "0%")
        self.gauge = wx.Gauge(self.dbViewerInsidePanel, -1, 100)
        self.oneHundredLabel = wx.StaticText(self.dbViewerInsidePanel, -1, "100%")
        self.dbTableSearch = wx.TextCtrl(self.dbViewerInsidePanel, -1, "Table Search", size=(300,-1), style=wx.TE_PROCESS_ENTER|wx.TE_RICH)
        self.dbTableTree = wx.TreeCtrl(self.dbViewerInsidePanel, -1, style=wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.dbValueList = wx.ListCtrl(self.dbViewerInsidePanel, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
        self.editButton = wx.Button(self.dbViewerInsidePanel, -1, "Edit")
        self.cancelButton = wx.Button(self.dbViewerInsidePanel, -1, "Cancel", size=((70, -1)))
        self.filterButton = wx.Button(self.dbViewerInsidePanel, -1, "Post Filter")
        self.preFilterCheckBox = wx.CheckBox(self.dbViewerInsidePanel, -1, "pre-filter")
        self.exportButton = wx.BitmapButton(self.dbViewerInsidePanel, -1, wx.Bitmap(".\\images\\export.png", wx.BITMAP_TYPE_ANY))
        self.popOutButton = wx.BitmapButton(self.dbViewerInsidePanel, -1, wx.Bitmap(".\\images\\openwindow.png", wx.BITMAP_TYPE_ANY))
        self.refreshTableListButton = wx.BitmapButton(self.dbViewerInsidePanel, -1, wx.Bitmap(".\\images\\refresh.jpg", wx.BITMAP_TYPE_ANY))
        self.filterText = wx.ComboBox(self.dbViewerInsidePanel, -1, "", size=(350,-1), style=wx.CB_DROPDOWN|wx.CB_SORT|wx.TE_PROCESS_ENTER)

        # Widgets for the Scripts tab
        self.dbScriptsListLabel = wx.StaticText(self.dbScriptsInsidePanel, -1, "Script List", style=wx.ALIGN_CENTRE)
        self.dbScriptsTableLabel = wx.StaticText(self.dbScriptsInsidePanel, -1, "Result Values", style=wx.ALIGN_LEFT)
        self.currentScriptsItemsLabel = wx.StaticText(self.dbScriptsInsidePanel, -1, "0", style=wx.ALIGN_CENTRE)
        self.ofScriptsLabel = wx.StaticText(self.dbScriptsInsidePanel, -1, " of ", style=wx.ALIGN_CENTRE)
        self.totalScriptsItemsLabel = wx.StaticText(self.dbScriptsInsidePanel, -1, "0", style=wx.ALIGN_CENTRE)
        self.zeroScriptsLabel = wx.StaticText(self.dbScriptsInsidePanel, -1, "0%")
        self.gaugeScripts = wx.Gauge(self.dbScriptsInsidePanel, -1, 100)
        self.oneHundredScriptsLabel = wx.StaticText(self.dbScriptsInsidePanel, -1, "100%")
        self.dbScriptsTableList = wx.ListBox(self.dbScriptsInsidePanel, -1, choices=[], style=wx.LB_HSCROLL)
        self.dbScriptsValueList = wx.ListCtrl(self.dbScriptsInsidePanel, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.SUNKEN_BORDER)
        #self.editScriptsButton = wx.Button(self.dbScriptsInsidePanel, -1, "Edit")
        self.cancelScriptsButton = wx.Button(self.dbScriptsInsidePanel, -1, "Cancel")
        self.filterScriptsButton = wx.Button(self.dbScriptsInsidePanel, -1, "Post Filter")
        #self.preFilterScriptsCheckBox = wx.CheckBox(self.dbScriptsInsidePanel, -1, "pre-filter")
        self.filterScriptsText = wx.TextCtrl(self.dbScriptsInsidePanel, -1, "", size=(350,-1), style=wx.TE_PROCESS_ENTER)

        # Widgets for the Graph Tab
        self.graph = Graph.GraphWithTools(self.noteBook, -1)

        self.__set_properties()
        self.__do_layout()

        #
        # Register all event callbacks.
        #
        self.Bind(wx.EVT_RADIOBOX, self.dbAccessRadioHandler, self.dbAccessRadioBox)
        self.Bind(wx.EVT_BUTTON, self.sqLiteFileButtonHandler, self.dbSqLiteFileButton)

        self.Bind(wx.EVT_MENU, self.changeFontSelectedCallBack, self.menuChangeFontSelected)
        self.Bind(wx.EVT_MENU, self.tableDescribeCallBack, self.menuDescribeSelected)
        if ( sys.platform == "win32" ):
            self.Bind(wx.EVT_MENU, self.openCmdSelectedCallBack, self.menuOpenCmdSelected)
            self.Bind(wx.EVT_MENU, self.viewLogsSelectedCallBack, self.menuViewLogsSelected)
        self.Bind(wx.EVT_MENU, self.viewSqlLogsSelectedCallBack, self.menuViewSqlLogsSelected)
        self.Bind(wx.EVT_MENU, self.editServerIPsSelectedCallBack, self.menuEditServerIPsSelected)
        self.Bind(wx.EVT_MENU, self.pythonRunnerSelectedCallBack, self.menuPythonRunnerSelected)
        self.Bind(wx.EVT_MENU, self.openSshSelectedCallBack, self.menuOpenSshSelected)
        #self.Bind(wx.EVT_MENU, self.openSshTunnelSelectedCallBack, self.menuOpenSshTunnelSelected)
        self.Bind(wx.EVT_MENU, self.refreshSummarySelectedCallBack, self.menuRefreshSummarySelected)
        self.Bind(wx.EVT_MENU, self.volumeViewerSelectedCallBack, self.menuVolumeViewerSelected)
        self.Bind(wx.EVT_MENU, self.viewScaleMonitorSelectedCallBack, self.menuScaleMonitorSelected)
        self.Bind(wx.EVT_MENU, self.openDbRequestCallBack, self.menuOpenDbRequest)
        self.Bind(wx.EVT_MENU, self.issueDbRequestCallBack, self.menuIssueDbRequest)
        self.Bind(wx.EVT_MENU, self.menuBarExitCallBack, self.Exit)

        self.Bind(wx.EVT_MENU, self.addScriptsCallBack, self.menuScriptsAdd)
        self.Bind(wx.EVT_MENU, self.removeScriptsCallBack, self.menuScriptsRemove)
        self.Bind(wx.EVT_MENU, self.editScriptsCallBack, self.menuScriptsEdit)
        self.Bind(wx.EVT_MENU, self.renameScriptsCallBack, self.menuScriptsRename)

        self.Bind(wx.EVT_MENU, self.menuBarHelpContextCallBack, self.HelpContext)

        self.Bind(wx.EVT_CHECKBOX, self.preFilterCallBack, self.preFilterCheckBox)
        self.Bind(wx.EVT_BUTTON, self.connectButtonCallBack, self.connectButton)

        self.Bind(wx.EVT_TEXT, self.dbTableSearchTextEnterCallBack, self.dbTableSearch )
        self.dbTableSearch.Bind(wx.EVT_SET_FOCUS, self.dbTableSearchFocusCallBack )
        self.dbTableSearch.Bind(wx.EVT_KILL_FOCUS, self.dbTableSearchNoFocusCallBack )

        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.dbTableTreeCallBack, self.dbTableTree)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.dbTableTreeCallBack, self.dbTableTree)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.dbTableTreeRightClickCallBack, self.dbTableTree)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.editButtonCallBack, self.dbValueList)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.columnSelectForSort, self.dbValueList)
        self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.columnSelectForSort, self.dbValueList)
        self.Bind(wx.EVT_BUTTON, self.editButtonCallBack, self.editButton)
        self.Bind(wx.EVT_BUTTON, self.cancelButtonCallBack, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.exportButtonCallBack, self.exportButton)
        self.Bind(wx.EVT_BUTTON, self.popOutButtonCallBack, self.popOutButton)
        self.Bind(wx.EVT_BUTTON, self.filterButtonCallBack, self.filterButton)
        self.Bind(wx.EVT_BUTTON, self.refreshTablesButtonCallBack, self.refreshTableListButton)
        self.Bind(wx.EVT_TEXT_ENTER, self.filterButtonCallBack, self.filterText)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.listRightClickCallBack, self.dbValueList)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.closeWindowCallBack, self )
        self.Bind(wx.EVT_CLOSE, self.closeWindowCallBack, self )
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.noteBookChangeCB, self.noteBook)
        self.Bind(wx.EVT_TEXT_ENTER, self.connectButtonCallBack, self.dbServerIP)
        self.Bind(wx.EVT_COMBOBOX, self.serverIPAddressSelectedCallBack, self.dbServerIP)

        # Scripts callback for the list.
        self.Bind(wx.EVT_LISTBOX, self.dbScriptsTableListCallBack, self.dbScriptsTableList)
        self.Bind(wx.EVT_BUTTON, self.cancelScriptsButtonCallBack, self.cancelScriptsButton)
        self.Bind(wx.EVT_BUTTON, self.filterScriptsButtonCallBack, self.filterScriptsButton)
        self.Bind(wx.EVT_TEXT_ENTER, self.filterScriptsButtonCallBack, self.filterScriptsText)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.listRightClickCallBack, self.dbScriptsValueList)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.columnSelectForSort, self.dbScriptsValueList)
        self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.columnSelectForSort, self.dbScriptsValueList)

        self.Bind(wx.EVT_BUTTON, self.chromeButtonHandler, self.chromeButton)
        self.Bind(wx.EVT_BUTTON, self.fireFoxButtonHandler, self.fireFoxButton)
        self.Bind(wx.EVT_BUTTON, self.ieButtonHandler, self.ieButton)       

        # This is a ballon tip
        #self.tipballoon = BT.BalloonTip(topicon=None, toptitle="Filter Parameter",
        #                                message="To set a time filter use the format 'DD-MM-YYYY hh:mm:ss'",
        #                                shape=BT.BT_ROUNDED,
        #                                tipstyle=BT.BT_LEAVE)

        # Set the BalloonTip target
        #self.tipballoon.SetTarget(self.filterText)
        # Set the BalloonTip background colour
        #self.tipballoon.SetBalloonColour(wx.LIGHT_GREY)
        # Set the font for the balloon title
        #self.tipballoon.SetTitleFont(wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        # Set the colour for the balloon title
        #self.tipballoon.SetTitleColour(wx.BLACK)
        # Leave the message font as default
        #self.tipballoon.SetMessageFont(wx.Font(8, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
        # Set the message (tip) foreground colour
        #self.tipballoon.SetMessageColour(wx.BLACK)
        # Set the start delay for the BalloonTip
        #self.tipballoon.SetStartDelay(1000)
        # Set the time after which the BalloonTip is destroyed
        #self.tipballoon.SetEndDelay(5000)

        # end wxGlade
        self.initLocals()
        return

    ###########################################################################
    # Function to set the Font information
    ###########################################################################
    def __set_properties(self):
        # begin wxGlade: UmDbSpy.__set_properties
        self.SetTitle(SOFTWARE_VERSION)
        self.dbAccessRadioBox.SetSelection(0)
        _icon = wx.Icon()
        _icon.CopyFromBitmap(wx.Bitmap("spyvsspy-icon.gif", wx.BITMAP_TYPE_GIF))
        self.SetIcon(_icon)
        self.SetSize((1376, 693))
        self.dbServerIP.SetSize((120, -1))
        self.statusBar.SetStatusWidths([-1])
        # statusbar fields
        statusBar_fields = ["Status: OK"]
        for i in range(len(statusBar_fields)):
            self.statusBar.SetStatusText(statusBar_fields[i], i)

        # DB Control settings
        self.connectButton.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2"))
        self.mainPanel.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2")) #"Times New Roman"))
        
        # DB Viewer settings
        self.dbTableSearch.SetFont(wx.Font(9, wx.MODERN, wx.FONTSTYLE_ITALIC, wx.NORMAL, 0, "MS Shell Dlg 2"))
        self.dbTableSearch.SetForegroundColour(wx.LIGHT_GREY)
        self.editButton.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2"))
        self.filterButton.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2"))
        self.cancelButton.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2"))

        self.dbListLabel.SetMinSize((260, 19))
        self.dbListLabel.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2"))
        self.dbListLabel.SetForegroundColour(wx.BLUE)

        self.dbTableLabel.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2"))
        self.dbTableLabel.SetForegroundColour(wx.BLUE)
        self.currentItemsLabel.SetMinSize((50, 19))
        self.currentItemsLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        self.ofLabel.SetMinSize((30, 19))
        self.ofLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        self.totalItemsLabel.SetMinSize((50, 19))
        self.totalItemsLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        self.zeroLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.oneHundredLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.gauge.SetMinSize((175, 19))
        self.gauge.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.dbTableTree.SetMinSize((270, 150))

        # DB Scripts settings
        self.cancelScriptsButton.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2"))
        self.filterScriptsButton.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2"))
        self.dbScriptsListLabel.SetMinSize((210, 19))
        self.dbScriptsListLabel.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2"))
        self.dbScriptsListLabel.SetForegroundColour(wx.BLUE)
        self.dbScriptsTableLabel.SetForegroundColour(wx.BLUE)

        self.dbScriptsTableLabel.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "MS Shell Dlg 2"))
        self.currentScriptsItemsLabel.SetMinSize((50, 19))
        self.currentScriptsItemsLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        self.ofScriptsLabel.SetMinSize((30, 19))
        self.ofScriptsLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        self.totalScriptsItemsLabel.SetMinSize((50, 19))
        self.totalScriptsItemsLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        self.zeroScriptsLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.oneHundredScriptsLabel.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.gaugeScripts.SetMinSize((175, 19))
        self.gaugeScripts.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.dbScriptsTableList.SetMinSize((220, 300))
        self.chromeButton.SetToolTip("Select to open the server address in your Chrome browser")
        self.chromeButton.SetSize(self.chromeButton.GetBestSize())
        self.fireFoxButton.SetToolTip("Select to open the server address in your FireFox browser")
        self.fireFoxButton.SetSize(self.fireFoxButton.GetBestSize())
        self.ieButton.SetToolTip("Select to open the server address in your IE browser")
        self.ieButton.SetSize(self.ieButton.GetBestSize())
        self.exportButton.SetToolTip("Select to export the current table to CSV format")
        self.popOutButton.SetToolTip("Select to popout this current table to another window")
        self.refreshTableListButton.SetToolTip("Select to refresh the databases and tables")

        return

    ###########################################################################
    # Function to layout the widgets 
    ###########################################################################
    def __do_layout(self):
        self.baseSizer = wx.BoxSizer(wx.VERTICAL)

        sizerForMainPanel = wx.StaticBoxSizer(self.staticBoxAroundEverything, wx.VERTICAL)
        sizerForNoteBook = wx.StaticBoxSizer(self.staticBoxAroundNoteBook, wx.VERTICAL)

        # Sizers for the DB Controls
        self.sizerForDbControlAndImage = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerForDbControl = wx.StaticBoxSizer(self.staticBoxDBControl, wx.HORIZONTAL)
        sizerForConnectButton = wx.BoxSizer(wx.VERTICAL)
        self.sizerForDbPassword = wx.StaticBoxSizer(self.staticBoxAroundDBPassword, wx.HORIZONTAL)
        self.sizerForDbUserName = wx.StaticBoxSizer(self.staticBoxAroundUserName, wx.HORIZONTAL)
        self.sizerForDbServerIP = wx.StaticBoxSizer(self.staticBoxAroundDBServerIP, wx.HORIZONTAL)

        #
        # DB Control Layout
        #
        self.sizerForDbControl.Add(self.dbAccessRadioBoxPanel, 0)
        self.sizerForDbControl.Add((5, 20), 0, wx.ADJUST_MINSIZE, 0)

        self.sizerForDbServerIP.Add(self.dbServerIP, 1, wx.ADJUST_MINSIZE|wx.BOTTOM, 3)
        self.sizerForDbServerIP.Add(self.dbSqLiteFileName, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        self.sizerForDbServerIP.Add(self.dbSqLiteFileButton, 0, wx.EXPAND|wx.ADJUST_MINSIZE|wx.BOTTOM|wx.LEFT, 2)
        self.sizerForDbServerIP.Add(self.chromeButton, 0, wx.LEFT, 3)
        self.sizerForDbServerIP.Add(self.fireFoxButton, 0, 0, 0)
        self.sizerForDbServerIP.Add(self.ieButton, 0, 0, 0)

        self.sizerForDbControl.Add(self.sizerForDbServerIP, 3, wx.TOP, 6)
        # Spacer
        self.sizerForDbControl.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        self.sizerForDbUserName.Add(self.dbUserName, 0, wx.ADJUST_MINSIZE|wx.BOTTOM, 3)
        self.sizerForDbControl.Add(self.sizerForDbUserName, 0, wx.TOP, 6)
        # Spacer
        self.sizerForDbControl.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        self.sizerForDbPassword.Add(self.dbPassword, 0, wx.ADJUST_MINSIZE|wx.BOTTOM, 3)
        self.sizerForDbControl.Add(self.sizerForDbPassword, 0, wx.TOP, 6)
        # Spacer
        self.sizerForDbControl.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        # Spacer
        sizerForConnectButton.Add((20, 23), 0, wx.ADJUST_MINSIZE, 0)
        sizerForConnectButton.Add(self.connectButton, 0, wx.ADJUST_MINSIZE|wx.RIGHT, 7)
        self.sizerForDbControl.Add(sizerForConnectButton, 0)



        imagePath = ".\\images\\dbSpyImage90x62.png"
        img = wx.Image(imagePath, wx.BITMAP_TYPE_ANY)
        bpm = wx.StaticBitmap(self, wx.Window.NewControlId(), wx.Bitmap(img))
        self.sizerForDbControlAndImage.Add(bpm, 0, wx.LEFT|wx.TOP, 14)

        self.sizerForDbControlAndImage.Add((5, 10), 0, wx.ADJUST_MINSIZE|wx.EXPAND|wx.ALIGN_RIGHT, 0)

        self.sizerForDbControlAndImage.Add(self.sizerForDbControl, 0, wx.RIGHT|wx.BOTTOM, 4)

        sizerForMainPanel.Add(self.sizerForDbControlAndImage, 0)
        self.sizerForDbControl.Layout()
        sizerForMainPanel.Layout()

        #
        # Summary Tab Layout
        #
        dbSummaryInsideSizer = wx.StaticBoxSizer(self.dbSummaryInsideStaticBox, wx.VERTICAL)
        dbSummaryHorzSizer = wx.BoxSizer(wx.HORIZONTAL)
        dbSummaryHorzSizer.Add(self.summaryList, 1, wx.RIGHT|wx.BOTTOM|wx.EXPAND, 4)
        self.dbSummaryInsidePanel.SetAutoLayout(True)
        self.dbSummaryInsidePanel.SetSizer(dbSummaryHorzSizer)
        dbSummaryHorzSizer.Fit(self.dbSummaryInsidePanel)
        dbSummaryHorzSizer.SetSizeHints(self.dbSummaryInsidePanel)

        dbSummaryInsideSizer.Add(self.dbSummaryInsidePanel, 1, wx.EXPAND, 0)
        self.dbSummaryNoteBookPanel1.SetAutoLayout(True)
        self.dbSummaryNoteBookPanel1.SetSizer(dbSummaryInsideSizer)
        dbSummaryInsideSizer.Fit(self.dbSummaryNoteBookPanel1)
        dbSummaryInsideSizer.SetSizeHints(self.dbSummaryNoteBookPanel1)

        #
        # DB Viewer Layout
        #
        sizerForDbViewer = wx.BoxSizer(wx.VERTICAL)
        sizerForGauge = wx.StaticBoxSizer(self.staticBoxAroundTableProgress, wx.HORIZONTAL)
        sizerForDbTableValues = wx.StaticBoxSizer(self.staticBoxAroundDBTableValuesLable, wx.HORIZONTAL)
        sizerForDbViewerLables = wx.BoxSizer(wx.HORIZONTAL)
        sizerForDbTree = wx.BoxSizer(wx.VERTICAL)
        sizerForDbTreeSearchAndRefresh = wx.BoxSizer(wx.HORIZONTAL)
        sizerForDbLists = wx.BoxSizer(wx.HORIZONTAL)
        sizerForDbTableList = wx.StaticBoxSizer(self.staticBoxAroundDBTableListLable, wx.HORIZONTAL)

        sizerForDbViewerLables.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForDbTableList.Add(self.dbListLabel, 0, wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizerForDbViewerLables.Add(sizerForDbTableList, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 10)
        # Spacer
        sizerForDbViewerLables.Add((30, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForDbTableValues.Add(self.dbTableLabel, 0, wx.ADJUST_MINSIZE, 0)
        sizerForDbViewerLables.Add(sizerForDbTableValues, 0, wx.TOP, 10)
        # Spacer
        sizerForDbViewerLables.Add((40, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGauge.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGauge.Add(self.currentItemsLabel, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 2)
        sizerForGauge.Add(self.ofLabel, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 2)
        sizerForGauge.Add(self.totalItemsLabel, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 2)
        sizerForGauge.Add((30, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGauge.Add(self.zeroLabel, 0, wx.LEFT|wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 2)
        # Spacer
        sizerForGauge.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGauge.Add(self.gauge, 0, wx.EXPAND|wx.BOTTOM|wx.ADJUST_MINSIZE, 0)
        # Spacer
        sizerForGauge.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGauge.Add(self.oneHundredLabel, 0, wx.TOP|wx.ADJUST_MINSIZE, 2)
        # Spacer
        sizerForGauge.Add((20, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGauge.Add(self.cancelButton, 0, wx.ADJUST_MINSIZE, 2)
        sizerForDbViewerLables.Add(sizerForGauge, 0, wx.RIGHT|wx.BOTTOM, 2)
        sizerForDbViewerLables.Add(self.exportButton, 0, wx.ALIGN_RIGHT|wx.TOP, 14)
        sizerForDbViewerLables.Add(self.popOutButton, 0, wx.ALIGN_RIGHT|wx.TOP, 14)
        sizerForDbViewer.Add(sizerForDbViewerLables, 0, wx.EXPAND|wx.ALIGN_RIGHT, 0)
        sizerForDbTreeSearchAndRefresh.Add(self.dbTableSearch, 0, wx.TOP|wx.BOTTOM, 2)
        sizerForDbTreeSearchAndRefresh.Add(self.refreshTableListButton, 0, wx.TOP|wx.BOTTOM, 0)
        sizerForDbTree.Add(sizerForDbTreeSearchAndRefresh, 0, wx.TOP|wx.BOTTOM, 2)
        sizerForDbTree.Add(self.dbTableTree, 1, wx.EXPAND|wx.BOTTOM, 2)
        sizerForDbLists.Add(sizerForDbTree, 0, wx.EXPAND, 4)
        # Spacer
        sizerForDbLists.Add((5, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForDbLists.Add(self.dbValueList, 1, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 2)
        sizerForDbViewer.Add(sizerForDbLists, 1, wx.EXPAND, 4)

        # Filter/Button Layout
        sizerForFilter = wx.StaticBoxSizer(self.staticBoxAroundFilter, wx.HORIZONTAL)
        sizerForFilter.Add(self.editButton, 0, wx.LEFT|wx.TOP|wx.ADJUST_MINSIZE, 2)
        # Spacer
        sizerForFilter.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForFilter.Add(self.filterButton, 0, wx.LEFT|wx.TOP|wx.BOTTOM|wx.ADJUST_MINSIZE, 2)
        # Spacer
        sizerForFilter.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForFilter.Add(self.preFilterCheckBox, 0, wx.LEFT|wx.TOP, 4)
        sizerForFilter.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForFilter.Add(self.filterText, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ADJUST_MINSIZE, 2)

        dbViewerInsideSizer = wx.BoxSizer(wx.HORIZONTAL)
        dbViewerSizer = wx.StaticBoxSizer(self.dbViewerInsideStaticBox, wx.VERTICAL)
        dbViewerSizer.Add(sizerForDbViewer, 1, wx.EXPAND, 4)
        dbViewerSizer.Add(sizerForFilter, 0, wx.RIGHT|wx.ALIGN_RIGHT, 4)
        self.dbViewerInsidePanel.SetAutoLayout(True)
        self.dbViewerInsidePanel.SetSizer(dbViewerSizer)
        dbViewerSizer.Fit(self.dbViewerInsidePanel)
        dbViewerSizer.SetSizeHints(self.dbViewerInsidePanel)
        dbViewerInsideSizer.Add(self.dbViewerInsidePanel, 1, wx.EXPAND, 0)
        self.dbViewerNoteBookPanel2.SetAutoLayout(True)
        self.dbViewerNoteBookPanel2.SetSizer(dbViewerInsideSizer)
        dbViewerInsideSizer.Fit(self.dbViewerNoteBookPanel2)
        dbViewerInsideSizer.SetSizeHints(self.dbViewerNoteBookPanel2)
        
        #
        # DB Scripts Layout
        #
        sizerForDbScripts = wx.BoxSizer(wx.VERTICAL)
        sizerForGaugeScripts = wx.StaticBoxSizer(self.staticBoxAroundScriptsTableProgress, wx.HORIZONTAL)
        sizerForDbScriptsTableValues = wx.StaticBoxSizer(self.staticBoxAroundScriptsDBTableValuesLable, wx.HORIZONTAL)
        sizerForDbScriptsLables = wx.BoxSizer(wx.HORIZONTAL)
        sizerForDbScriptsLists = wx.BoxSizer(wx.HORIZONTAL)
        sizerForDbScriptsTableList = wx.StaticBoxSizer(self.staticBoxAroundScriptsDBTableListLable, wx.HORIZONTAL)

        sizerForDbScriptsTableList.Add(self.dbScriptsListLabel, 0, wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizerForDbScriptsLables.Add(sizerForDbScriptsTableList, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 10)
        # Spacer
        sizerForDbScriptsLables.Add((10, 30), 0, wx.ADJUST_MINSIZE, 0)
        sizerForDbScriptsTableValues.Add(self.dbScriptsTableLabel, 0, wx.ADJUST_MINSIZE, 0)
        sizerForDbScriptsLables.Add(sizerForDbScriptsTableValues, 0, wx.TOP, 10)
        # Spacer
        sizerForDbScriptsLables.Add((40, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGaugeScripts.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGaugeScripts.Add(self.currentScriptsItemsLabel, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 2)
        sizerForGaugeScripts.Add(self.ofScriptsLabel, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 2)
        sizerForGaugeScripts.Add(self.totalScriptsItemsLabel, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 2)
        sizerForGaugeScripts.Add((30, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGaugeScripts.Add(self.zeroScriptsLabel, 0, wx.LEFT|wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 2)
        # Spacer
        sizerForGaugeScripts.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGaugeScripts.Add(self.gaugeScripts, 0, wx.EXPAND|wx.BOTTOM|wx.ADJUST_MINSIZE, 0)
        # Spacer
        sizerForGaugeScripts.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGaugeScripts.Add(self.oneHundredScriptsLabel, 0, wx.TOP|wx.ADJUST_MINSIZE, 2)
        # Spacer
        sizerForGaugeScripts.Add((20, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForGaugeScripts.Add(self.cancelScriptsButton, 0, wx.ADJUST_MINSIZE, 2)
        sizerForDbScriptsLables.Add(sizerForGaugeScripts, 0, wx.RIGHT|wx.BOTTOM, 2)
        sizerForDbScripts.Add(sizerForDbScriptsLables, 0, wx.EXPAND|wx.ALIGN_RIGHT, 0)
        sizerForDbScriptsLists.Add(self.dbScriptsTableList, 0, wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND|wx.ADJUST_MINSIZE, 2)
        # Spacer
        sizerForDbScriptsLists.Add((5, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForDbScriptsLists.Add(self.dbScriptsValueList, 1, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND, 2)
        sizerForDbScripts.Add(sizerForDbScriptsLists, 1, wx.EXPAND, 4)

        # Filter/Button Layout
        sizerForScriptsFilter = wx.StaticBoxSizer(self.staticBoxAroundScriptsFilter, wx.HORIZONTAL)
        #sizerForScriptsFilter.Add(self.editScriptsButton, 0, wx.LEFT|wx.TOP|wx.ADJUST_MINSIZE, 2)
        # Spacer
        #sizerForScriptsFilter.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForScriptsFilter.Add(self.filterScriptsButton, 0, wx.LEFT|wx.TOP|wx.BOTTOM|wx.ADJUST_MINSIZE, 2)
        # Spacer
        #sizerForScriptsFilter.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        #sizerForScriptsFilter.Add(self.preFilterScriptsCheckBox, 0, wx.LEFT|wx.TOP, 4)
        sizerForScriptsFilter.Add((10, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizerForScriptsFilter.Add(self.filterScriptsText, 0, wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ADJUST_MINSIZE, 2)

        dbScriptsInsideSizer = wx.BoxSizer(wx.HORIZONTAL)
        dbScriptsSizer = wx.StaticBoxSizer(self.dbScriptsInsideStaticBox, wx.VERTICAL)
        dbScriptsSizer.Add(sizerForDbScripts, 1, wx.EXPAND, 4)
        dbScriptsSizer.Add(sizerForScriptsFilter, 0, wx.RIGHT|wx.ALIGN_RIGHT, 4)
        self.dbScriptsInsidePanel.SetAutoLayout(True)
        self.dbScriptsInsidePanel.SetSizer(dbScriptsSizer)
        dbScriptsSizer.Fit(self.dbScriptsInsidePanel)
        dbScriptsSizer.SetSizeHints(self.dbScriptsInsidePanel)
        dbScriptsInsideSizer.Add(self.dbScriptsInsidePanel, 1, wx.EXPAND, 0)
        self.dbScriptsNoteBookPanel3.SetAutoLayout(True)
        self.dbScriptsNoteBookPanel3.SetSizer(dbScriptsInsideSizer)
        dbScriptsInsideSizer.Fit(self.dbScriptsNoteBookPanel3)
        dbScriptsInsideSizer.SetSizeHints(self.dbScriptsNoteBookPanel3)

        #
        # Notebook Setup
        #
        self.noteBook.AddPage(self.dbSummaryNoteBookPanel1, "DB Summary")
        page = self.noteBook.GetPage(0)
        page.SetBackgroundColour("#ece9d8")

        self.noteBook.AddPage(self.dbViewerNoteBookPanel2, "DB Viewer") 
        page = self.noteBook.GetPage(1)
        page.SetBackgroundColour("#ece9d8")

        self.noteBook.AddPage(self.dbScriptsNoteBookPanel3, "Scripts")  
        page = self.noteBook.GetPage(2)
        page.SetBackgroundColour("#ece9d8")

        self.noteBook.AddPage(self.graph, "Graph")      
        page = self.noteBook.GetPage(3)
        page.SetBackgroundColour("#ece9d8")

        #self.SetBackgroundColour("#b7ceec")
        #self.SetBackgroundColour("#3F51B5")
        self.SetBackgroundColour("#0D47A1")


        self.noteBook.SetBackgroundColour(wx.NullColour)
        sizerForNoteBook.Add(self.noteBook, 1, wx.EXPAND, 0)
        sizerForMainPanel.Add(sizerForNoteBook, 1, wx.RIGHT|wx.EXPAND, 4)

        #
        # Final Main Window Layout
        #
        self.mainPanel.SetAutoLayout(True)
        self.mainPanel.SetSizer(sizerForMainPanel)
        sizerForMainPanel.Fit(self.mainPanel)
        sizerForMainPanel.SetSizeHints(self.mainPanel)
        self.baseSizer.Add(self.mainPanel, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(self.baseSizer)
        self.Layout()
        # end wxGlade

    ###########################################################################
    # Function to initialize all non wx locals
    ###########################################################################
    def initLocals( self ):
        self.dbConnections = {}
        self.dbViewerColumns = []
        self.dbViewerColumnsFull = []
        self.dbViewerFilterList = []
        self.dbViewerRows = []

        self.currentNoteBook = 0

        self.ip = None
        self.user = None
        self.passwd = None
        self.connected = False
        self.dbTimeoutTimer = None
        self.dbTimeoutCounter = 0
        self.sqLiteSelected = False
        self.isBundleInUse = False
        self.bundleDirectory = None
        self.sqLiteMysqlFileName = None
        self.sqLiteDbFiles = []

        self.dbUserName.SetValue( "root" )
        self.dbPassword.SetValue( "ugauga" )

        # This variable stores all of the databases and tables.  It is a list to 
        # preserver order
        self.databaseList = []
        self.treeHasBeenFiltered = False
        
        self.dbViewerTableSelected = ""
        self.dbViewerFilterOn = False
        self.isDbViewerPreFilterChecked = False

        self.dbScriptsColumns = []
        self.dbScriptsRows = []
        self.dbScriptsTableSelected = 0
        self.dbScriptsFilterList = []
        self.dbScriptsFilterOn = False

        # Db Viewer table timer items
        self.dbViewerTableTimer = None
        self.stopDbViewerTableTimer = 0
        self.dbViewerTableTimerStopped = 0
        self.dbViewerQueryInProgress = 0

        # Db Scripts table timer items
        self.dbScriptsTableTimer = None
        self.stopDbScriptsTableTimer = 0
        self.dbScriptsTableTimerStopped = 0
        self.dbScriptsQueryInProgress = 0

        # Need to create empty lines
        self.summaryList.InsertColumn( 0, "Item of Interest", wx.LIST_FORMAT_LEFT, 600 )
        self.summaryList.InsertColumn( 1, "Value", wx.LIST_FORMAT_CENTER, 200 )

        self.columnSelected = None 


        # Try to load up the IP file, format should be:
        #
        #   hostname/ip  username  password
        #
        self.ipHistory = {}
        print(os.environ["APPDATA"])
        try:
            ipHistoryFileName = SERVER_IP_HISTORY_FILE
            file = open(ipHistoryFileName, "r", encoding='utf8')
            for line in file.readlines():
                toks = line.strip().split()
                ip = ""
                username = ""
                password = ""
                ip = line
                if ( len(toks) > 1 ):
                    ip = toks[0]
                    username = toks[1]
                    password = ""
                    # Sometimes the password is blank
                    if ( len(toks) > 2 ):
                        password = toks[2]
                self.ipHistory[ip] = (ip, username, password)
            file.close()
        except:
            ipHistoryFileName = SERVER_IP_HISTORY_FILE
            file = open(ipHistoryFileName, "w", encoding='utf8')
            file.close()

        self.dbServerIP.Append(list(self.ipHistory.keys()))
        self.dbServerIP.SetFocus()

        # Try to load up the filter history
        #
        #   hostname/ip  username  password
        #
        self.filterHistory = []
        try:
            filterHistoryFile = os.environ["APPDATA"] + "\\UMFilterHistory.txt"
            file = open(filterHistoryFile, "r", encoding='utf8')
            self.filterHistory = file.readlines()
            file.close()
        except:
            filterHistoryFile = os.environ["APPDATA"] + "\\UMFilterHistory.txt"
            file = open(filterHistoryFile, "w", encoding='utf8')
            file.close()
        self.filterText.Append(self.filterHistory)

        # These are loaded during the connect phase.  These are definitions in the DB that 
        # define what are in some columns
        self.CHANGE_TYPE_DEF = {}
        self.CONTENTION_ANAL_ROLE_DEF = {}
        self.DYN_STATE_DEF = {}
        self.ELEMENT_TYPE_DEF = {}
        self.STAT_TYPE_DEF = {}
        self.TARGET_TYPE_DEF = {}
        self.THRESHOLD_TYPE_DEF = { 0: "PRIMARY",
                                    1: "SECONDARY"
                                  }
        self.OPERATIONS_DEF = { 0: "EQUAL",
                                1: "GREATER THAN",
                                2: "LESS THAN"
                              }
        self.EVENT_TYPE_DEF = { 1: "DYNAMIC THRESHOLD",
                                2: "VOLUME MOVE",
                                3: "POLICY GROUP LIMIT CHANGE",
                                4: "HA FAILOVER GIVEBACK",
                                5: "CLUSTER UPGRADE",
                                6: "STATIC THRESHOLD",
                                7: "SYSTEM THRESHOLD - TCI"
                              }
        self.NOTIFICATION_DYNAMIC_EVENT_OPTION = {}
        self.NOTIFICATION_LEVEL = {}
        self.NOTIFICATION_SCOPE = {}
        self.NOTIFICATION_TYPE = {}
        self.NOTIFICATION_UM_EVENT = {}

        # Now check to see if chrome and/or firefox is installed
        # Look for Chrome
        self.chromePath = os.environ['ProgramFiles'] + "\\Google\\Chrome\\Application\\chrome.exe"
        # Check if chrome in 32bit area, if not check 64 bit installation dir
        if ( not os.path.isfile(self.chromePath) ):
            # Could not find chrome in 32 bit area, look in 64 bit installation
            # dir
            if ( 'ProgramFiles(x86)' in os.environ ):
                self.chromePath = os.environ['ProgramFiles(x86)'] + "\\Google\\Chrome\\Application\\chrome.exe"
                if ( not os.path.isfile(self.chromePath) ):
                    print("Chrome not found")
                    self.chromeButton.Hide()
            else:
                #print("Program Files Win 64 not found")
                self.chromeButton.Hide()

        self.fireFoxPath = os.environ['ProgramFiles'] + "\\Mozilla Firefox\\firefox.exe"
        # Check if firefox in 32bit area, of not check 64 bit installation dir
        if ( not os.path.isfile(self.fireFoxPath) ):
            # Could not find firefox in 32 bit area, look in 64 bit installation
            # dir
            if ( 'ProgramFiles(x86)' in os.environ ):
                self.fireFoxPath = os.environ['ProgramFiles(x86)'] + "\\Mozilla Firefox\\firefox.exe"
                if ( not os.path.isfile(self.fireFoxPath) ):
                    print("FireFox not found - hiding button")
                    self.fireFoxButton.Hide()
            else:
                #print("Program Files Win 64 not found")
                self.fireFoxButton.Hide()
        
        return

    def startDbTimeoutTimer(self):
        if ( self.dbTimeoutTimer == None ):
            self.dbTimeoutTimer = MonitorDBTimeout(self)
            self.dbTimeoutTimer.start()
        self.dbTimeoutCounter = 0
        return

    ###########################################################################
    # This method will load all of the scripts/reports into the table.  We
    # have todo this at a later time because we need to know the DB version
    ###########################################################################
    def loadScripts(self):
        # Try to load up the scripts.
        self.scripts = {}
        # Place in users directory or app data
        filename = os.environ["APPDATA"] + "\\UMDbScripts.txt"
        try:
            file = open(filename, "r", encoding='utf8')
            self.scripts = eval(file.readlines()[0])
            file.close()
        except:
            file = open(filename,"w", encoding='utf8')
            file.write(repr(self.scripts))
            file.close()

        # Create some up front
        self.scripts["All Clusters"] = "select * from netapp_model.cluster"
        self.scripts["All Nodes"] = "select * from netapp_model.node"
        self.scripts["All Disks"] = "select * from netapp_model.disk"
        self.scripts["All VServers"] = "select * from netapp_model.vserver"
        self.scripts["All LUNs"] = "select * from netapp_model.lun"
        self.scripts["All Namespaces"] = "select * from netapp_model.namespace"
        self.scripts["All Volumes"] = "select * from netapp_model.volume"
        self.scripts["All Aggregates"] = "select * from netapp_model.aggregate"
        self.scripts["All RAID Groups/Plexs"] = "select * from netapp_model.raid_group"
        self.scripts["All CIFS Shares"] = "select * from netapp_model.cifs_share"
        self.scripts["All Network LIFs"] = "select * from netapp_model.network_lif"
        self.scripts["All Qtrees"] = "select * from netapp_model.qtree"
        self.scripts["All QOS Workload Detail"] = "select * from netapp_model.qos_workload_detail"
        if ( self.version < 7.3 ):
            self.scripts["All QOS Volume Workloads"] = "select * from netapp_model.qos_volume_workload"
        else:
            self.scripts["All QOS Workloads"] = "select * from netapp_model.qos_workload"
        self.scripts["Volumes with no QoS Policy"] = "select * from netapp_model.volume where qosPolicyGroupId=NULL"

        # Now load up the scripts into the list
        self.dbScriptsValueList.ClearAll()
        # Need to reformat because the list contains more information than required
        keys = list(self.scripts.keys())
        keys.sort()
        self.dbScriptsTableList.Set( list(keys) )

        return

    ###########################################################################
    # When the tabs are changed, this callback is called
    ###########################################################################
    def noteBookChangeCB( self, event ):
        #print("Note Book Changed CB " + str(event.GetSelection()))
        self.currentNoteBook = event.GetSelection()
        self.dbServerIP.SetFocus()
        return

    ###########################################################################
    # When the window is closed, this callback is called.
    ###########################################################################
    def closeWindowCallBack( self, event ):
        if ( self.dbTimeoutTimer != None ):
            self.dbTimeoutTimer.stop()
        sys.exit()
        return

###########################################################################
###########################################################################
# Main Menu Callbacks Start
###########################################################################
###########################################################################

    def chromeButtonHandler(self, event):  # wxGlade: MyFrame.<event_handler>
        ip = self.dbServerIP.GetValue()
        if ( ip == "" ):
            wx.MessageBox("Please enter in a valid server address first")
            return
        print("start \"Chrome\" \"" + self.chromePath + "\" \"https://" + ip + "\"")
        os.system("start \"Chrome\" \"" + self.chromePath + "\" \"https://" + ip + "\"")
        return

    def fireFoxButtonHandler(self, event):  # wxGlade: MyFrame.<event_handler>
        ip = self.dbServerIP.GetValue()
        if ( ip == "" ):
            wx.MessageBox("Please enter in a valid server address first")
            return
        print("start \"FireFox\" \"" + self.fireFoxPath + "\" \"https://" + ip + "\"")
        os.system("start \"FireFox\" \"" + self.fireFoxPath + "\" \"https://" + ip + "\"")
        return

    def ieButtonHandler(self, event):  # wxGlade: MyFrame.<event_handler>
        ip = self.dbServerIP.GetValue()
        if ( ip == "" ):
            wx.MessageBox("Please enter in a valid server address first")
            return
        os.system("start iexplore.exe https://" + ip)
        return


    ###########################################################################
    # SQLite file handler.
    ###########################################################################
    def sqLiteFileButtonHandler( self, event ):
        wildcards = "Mysql file/support bundle/dir (*.sql,*.7z, *.dbspy)|*.sql;*.7z;*.dbspy"
        dlg = wx.FileDialog(self, 
                            message="Open MySQL (sql), Support Bundle (7z) or previously extracted bundle", 
                            defaultDir=".", 
                            defaultFile="",
                            wildcard=wildcards,
                            style=wx.FD_OPEN|wx.FD_CHANGE_DIR )
        if ( dlg.ShowModal() == wx.ID_OK ):
            path = dlg.GetPath()
            self.dbSqLiteFileName.SetValue(path)
        dlg.Destroy()
        return

    ###########################################################################
    # Callback for the db access radio box
    ###########################################################################
    def dbAccessRadioHandler(self, event): # wxGlade: MyFrame.<event_handler>
        if ( self.dbAccessRadioBox.GetSelection() == 1):
            self.dbUserName.Disable()
            self.dbPassword.Disable()
            self.dbServerIP.Hide()
            self.chromeButton.Hide()
            self.fireFoxButton.Hide()
            self.ieButton.Hide()
            self.staticBoxAroundDBServerIP.SetLabel("SQL File/Support Bundle Zip/Dir")
            self.dbSqLiteFileName.Show()
            self.dbSqLiteFileButton.Show()
            self.sizerForDbServerIP.Layout()
            self.sizerForDbControlAndImage.Layout()
            #self.sizerForDbControl 
            self.sqLiteSelected = True
            self.Refresh()
        else:
            self.dbUserName.Enable()
            self.dbPassword.Enable()
            self.dbServerIP.Show(True)
            self.chromeButton.Show(True)
            self.fireFoxButton.Show(True)
            self.ieButton.Show(True)
            self.dbSqLiteFileName.Hide()
            self.dbSqLiteFileButton.Hide()
            self.staticBoxAroundDBServerIP.SetLabel("DB Server IP")
            self.sizerForDbServerIP.Layout()
            self.sizerForDbControlAndImage.Layout()
            self.sqLiteSelected = False
            self.Refresh()
        return

    ###########################################################################
    # Callback to describe a table in the selected list
    ###########################################################################
    def tableDescribeCallBack( self, event ):
        if ( self.sqLiteSelected == True ):
            wx.MessageBox( "Sorry, this will not work with SqLite")
            return

        # Check to make sure that we are connected to a DB.
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return

        if ( self.dbViewerTableSelected == "" ):
            wx.MessageBox( "Please select a table within a database first." )
            return

        tree = TreeViewer.TreeViewer( self, -1, "")
        tree.setParent( self )
        dataBase = self.dbViewerTableSelected.split(".")[0]
        tree.setDataBase( dataBase )
        tree.createTree()
        tree.Show()

        return

    ###########################################################################
    # Menu callback method to open a command console
    ###########################################################################
    def openCmdSelectedCallBack(self, event):
        os.system("start cmd")
        return

    ###########################################################################
    # Open a python runner tool.
    ###########################################################################
    def pythonRunnerSelectedCallBack(self, event):
        pr = PythonRunner.PythonExecutor(self, -1, "")
        pr.setParent(self)
        pr.Show()
        return

    ###########################################################################
    # Menu callback method to open a ssh terminal
    ###########################################################################
    def openSshSelectedCallBack(self, event):
        ip = self.dbServerIP.GetValue()
        dlg = wx.TextEntryDialog( None, 
                                  "Please enter SSH command string: (root@192.168.45.196)",
                                  "Open SSH",
                                  "root@" + ip,
                                  style=wx.OK|wx.CANCEL )
        retval = dlg.ShowModal()
        if ( retval == 5100 ):
            msg = dlg.GetValue()
            if (msg != "" ):
                if ( sys.platform == "win32" ): 
                    os.system("start ssh.bat " + msg)
                else:
                    cmd = "xterm -title \"ssh " + msg + "\" -e ssh " + msg + " &"
                    #print(cmd)
                    os.system(cmd)
        return

    ###########################################################################
    # Menu callback method to open a ssh tunnel
    ###########################################################################
    def openSshTunnelSelectedCallBack(self, event):
        ip = self.dbServerIP.GetValue()
        dlg = wx.TextEntryDialog( None, 
                                  "Please enter SSH command string: (root@192.168.45.196)",
                                  "Open SSH Tunnel",
                                  "root@" + ip,
                                  style=wx.OK|wx.CANCEL )
        retval = dlg.ShowModal()
        if ( retval == 5100 ):
            msg = dlg.GetValue()
            if (msg != "" ):
                dlg = wx.TextEntryDialog( None, 
                                          "Please enter port number",
                                          "SSH Tunnel Port",
                                          "2000",
                                          style=wx.OK|wx.CANCEL )
                retval = dlg.ShowModal()
                if ( retval == 5100 ):
                    port = dlg.GetValue()
                    if (port != "" ):
                        os.system("start sshTunnel.bat " + msg + " " + port)
        return


    ###########################################################################
    # Manual call to refresh the Summary Table
    ###########################################################################
    def refreshSummarySelectedCallBack(self, event):
        # Check to make sure that we are connected to a DB.
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return

        buildSummary  = BuildSummaryTable( self )
        if ( sys.platform == "win32" ):
            buildSummary.start()
        else:
            buildSummary.run()
        return

    def viewScaleMonitorSelectedCallBack( self, event ):
        # Check to make sure that we are connected to a DB.
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return

        plot = DataPlotter.DataPlotter(None, -1, "UM Performance" )
        plot.setParent(self)
        plot.setScaleMonitorViewing()
        plot.Show()
        return

    def volumeViewerSelectedCallBack( self, event ):
        # Check to make sure that we are connected to a DB.
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return

        vv = VolumeViewer.VolumeViewer( None, -1, "")
        vv.setParent(self)
        vv.initData()
        vv.Show()
        return

    ###########################################################################
    # Menu Callback to change the font
    ###########################################################################
    def changeFontSelectedCallBack(self, event):
        dialog = wx.FontDialog( None, wx.FontData() )
        if ( dialog.ShowModal() == wx.ID_OK ):
            data = dialog.GetFontData()
            font = data.GetChosenFont()
            color = data.GetColour()
            self.summaryList.SetFont(font)
            self.dbTableTree.SetFont(font)
            self.dbTableSearch.SetFont(font)
            self.dbValueList.SetFont(font)
        dialog.Destroy()
        return

    ###########################################################################
    # view the logs
    ###########################################################################
    def viewLogsSelectedCallBack( self, event ):

        logviewer = LogViewer.LogViewer(None, -1, "")
        logviewer.setServerIp( self.dbServerIP.GetValue() )
        logviewer.setParent( self )
        logviewer.Show()
        logviewer.run()
        return

    ###########################################################################
    # view the logs
    ###########################################################################
    def viewSqlLogsSelectedCallBack( self, event ):
        os.system("start notepad.exe " + SQL_FILE)
        return

    ###########################################################################
    # Edit the server ip history file
    ###########################################################################
    def editServerIPsSelectedCallBack( self, event ):
        wx.MessageBox( "NOTE: After you have finished editing this file, you will need to restart DBSpy to pick up the changes" )
        os.system("start notepad.exe " + SERVER_IP_HISTORY_FILE)
        return

    ###########################################################################
    # Open a DB view viewing remotely
    ###########################################################################
    def openDbRequestCallBack( self, event ):
        # Find out if this is a windows box they are trying to open up.
        dlg = wx.MessageDialog( self, 
                                "Is this a Windows Machine?",
                               "Windows?",
                               wx.YES_NO | wx.ICON_QUESTION )
        answer = dlg.ShowModal() == wx.ID_YES
        if ( answer == True ):
            # Windows box so we cannot ssh to it.  The user needs to open the
            # db themselves
            text = ["\n"]
            text.append("Since this is a windows box, you will need to manually open the\n")
            text.append("database for external access.\n\n")

            text.append("If this is MySQL 8.0, run these commands:\n")
            text.append("    drop user if exists umdev;\n")
            text.append("    create user \'umdev\' identified with mysql_native_password by \'ugauga\';\n")
            text.append("    grant all privileges on *.* to \'umdev\'@\'%\' with grant option;\n\n")

            text.append("If this is MySQL 7.0 or less, run these commands:\n")
            text.append("    grant all privileges on *.* to \'umdev\'@\'%\' identified by \'ugauga\' with grant option;\n")
            text.append("    flush privileges;\n\n")

            text.append("Once you issue these commands, you can use umdev/ugauga to access the DB\n\n")
       
            textBox = TextBox.TextBox(None, wx.Window.NewControlId(), "")
            textBox.setTitle( "Windows Box Setup" )
            textBox.setTextArray( text )
            textBox.Show()
            return

        # Prompt the user for the username of the machine
        dlg = wx.TextEntryDialog( None, 
                                  "Enter login name to the host where the DB is located (eg. root)",
                                  "User Name",
                                  "root",
                                  style=wx.OK|wx.CANCEL )
        retval = dlg.ShowModal()
        if ( retval == 5100 ):
            username = dlg.GetValue()
            if (username == "" ):
                wx.MessageBox( "Not a valid username" )
                return

            # Get the password for the user specified
            dlg = wx.TextEntryDialog( None, 
                                      "Enter password for specified login user",
                                      "Password",
                                      #"drp3pp3r",
                                      "",
                                      style=wx.OK|wx.CANCEL|wx.TE_PASSWORD )
            retval = dlg.ShowModal()
            if ( retval == 5100 ):
                password = dlg.GetValue()


                ip = self.dbServerIP.GetValue()

                #
                # Get the host address 
                dlg = wx.TextEntryDialog( None, 
                                          "Enter IP address of host where the DB should be opened",
                                          "IP/Host",
                                          ip,
                                          style=wx.OK|wx.CANCEL )
                retval = dlg.ShowModal()
                if ( retval == 5100 ):
                    hostname = dlg.GetValue()
                    if ( hostname == "" ):
                        wx.MessageBox( "Not a valid hostname" )
                        return

                    wx.MessageBox( "Attempting to open DB on " + hostname + " using login " + username + 
                                   ".  This will take a few seconds, please be patient." )
                    try:

                        cnopts = pysftp.CnOpts()
                        cnopts.hostkeys = None
                        conn = pysftp.Connection(host=hostname, 
                                                 username=username, 
                                                 password=password,
                                                 cnopts=cnopts)
                        # Need to find out the mysql verison because there are different grants
                        retVal = conn.execute('mysql --version')
                        if ("8.0" in str(retVal)):
                            retVal = conn.execute('mysql --user=root --password=ugauga -e \"drop user if exists umdev;  create user \'umdev\' identified with mysql_native_password by \'ugauga\'; grant all privileges on *.* to \'umdev\'@\'%\' with grant option;\"')
                            print(retVal)
                            if ( "Access denied" in str(retVal) ):
                                retVal = conn.execute('mysql --user=root -e \"drop user if exists umdev;  create user \'umdev\' identified with mysql_native_password by \'ugauga\'; grant all privileges on *.* to \'umdev\'@\'%\' with grant option;\"')
                                print(retVal)
                            if ( "Access denied" in str(retVal) ):
                                wx.MessageBox( "Failed to connect to the remote host with the password provided" )
                            else:
                                wx.MessageBox( "The DB on machine (" + hostname + ") should now be open to view, please use user 'umdev' with 'ugauga' as the password" )
                            self.dbUserName.SetValue("umdev")
                            self.dbPassword.SetValue("ugauga")
                            conn.close()
                        else:
                            # So if this is an api server then the password is blank
                            retVal = conn.execute('mysql --user=root --password=ugauga -e \"grant all privileges on *.* to \'root\'@\'%\' identified by \'ugauga\' with grant option; flush privileges;\"')
                            print(retVal)
                            if ( "Access denied" in str(retVal) ):
                                retVal = conn.execute('mysql --user=root -e \"grant all privileges on *.* to \'root\'@\'%\' identified by \'ugauga\' with grant option; flush privileges;\"')
                                print(retVal)
                            
                            if ( "Access denied" in str(retVal) ):
                                wx.MessageBox( "Failed to connect to the remote host with the password provided" )
                            else:
                                wx.MessageBox( "The DB on machine (" + hostname + ") should now be open to view, please use user 'umdev' with 'ugauga' as the password" )
                            conn.close()
                            self.dbUserName.SetValue("umdev")
                            self.dbPassword.SetValue("ugauga")
                    except Exception as exception:
                            wx.MessageBox("An error occured opening the DB: " + str(exception))
        return

    ###########################################################################
    # Issue a raw mysql command to the db
    ###########################################################################
    def issueDbRequestCallBack( self, event ):
        # Are we connected
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return
        sqlCommands = SQLCommands.SQLCommands(None, -1, "")
        sqlCommands.setParent(self)
        sqlCommands.Show()
        return


    ###########################################################################
    # Callback for the add scripts button
    ###########################################################################
    def addScriptsCallBack( self, event ):
        self.noteBook.SetSelection(2)
        # Prompt the user for a name of the script
        dlg = wx.TextEntryDialog( None, 
                                  "Enter New Script Name",
                                  style=wx.OK|wx.CANCEL)
        retval = dlg.ShowModal()
        if ( retval == 5100 ):
            scriptName = dlg.GetValue()
            # Make sure that the name does not already exist
            if ( scriptName in self.scripts.keys() ):
                wx.MessageBox( "A Script with that same name already exists." )
                return

            # Now prompt the user for the sql commands
            dlg = wx.TextEntryDialog( None, 
                                      "Enter Script SQL statement",
                                      style=wx.OK|wx.CANCEL )
            retval = dlg.ShowModal()
            if ( retval == 5100 ):
                scriptSql = dlg.GetValue()
                self.scripts[scriptName] = scriptSql

                # Now set new script and update file
                self.dbScriptsValueList.ClearAll()
                # Need to reformat because the list contains more information than required
                keys = list(self.scripts.keys())
                keys.sort()
                self.dbScriptsTableList.Set( list(keys) )

                self.updateScriptsFile()
        return

    ###########################################################################
    # Utility to update the scripts file.
    ###########################################################################
    def updateScriptsFile( self ):
        filename = os.environ["APPDATA"] + "\\UMDbScripts.txt"
        try:
            file = open(filename, "w", encoding='utf8')
            file.write(repr(self.scripts))
            file.close()
        except:
            wx.MessageBox( "Failed to update scripts file" )

        return

    ###########################################################################
    # Callback for the remove scripts button
    ###########################################################################
    def removeScriptsCallBack( self, event ):
        self.noteBook.SetSelection(2)
        selected = self.dbScriptsTableList.GetSelections()
        if ( len(selected) == 0 ):
            wx.MessageBox( "Please select a script from the list" )
            return
        keys = list(self.scripts.keys())
        keys.sort()
        retval = wx.MessageBox( "Are you sure you want to remove: " + keys[selected[0]], 
                                style=wx.OK|wx.CANCEL)
        if ( retval != 4 ):
            return

        self.scripts.pop(keys[selected[0]])

        # Now set new script and update file
        self.dbScriptsValueList.ClearAll()
        # Need to reformat because the list contains more information than required
        keys = list(self.scripts.keys())
        keys.sort()
        self.dbScriptsTableList.Set( list(keys) )

        self.updateScriptsFile()

        return

    ###########################################################################
    # Callback for the edit scripts button
    ###########################################################################
    def editScriptsCallBack( self, event ):
        self.noteBook.SetSelection(2)
        selected = self.dbScriptsTableList.GetSelections()
        if ( len(selected) == 0 ):
            wx.MessageBox( "Please select a script from the list" )
            return

        keys = list(self.scripts.keys())
        keys.sort()
        scriptName = keys[selected[0]]
        # Now prompt the user for the sql commands
        dlg = wx.TextEntryDialog( None,
                                  keys[selected[0]], 
                                  "Modify Script SQL statement",
                                  defaultValue=self.scripts[scriptName],
                                  style=wx.OK|wx.CANCEL )
        retval = dlg.ShowModal()
        if ( retval == 5100 ):
            scriptSql = dlg.GetValue()
            self.scripts[scriptName] = scriptSql

            self.updateScriptsFile()

        return

    ###########################################################################
    # Callback for the rename scripts button
    ###########################################################################
    def renameScriptsCallBack( self, event ):
        self.noteBook.SetSelection(2)
        selected = self.dbScriptsTableList.GetSelections()
        if ( len(selected) == 0 ):
            wx.MessageBox( "Please select a script from the list" )
            return

        keys = list(self.scripts.keys())
        keys.sort()
        scriptName = keys[selected[0]]
        # Now prompt the user for the name change
        dlg = wx.TextEntryDialog( None,
                                  keys[selected[0]], 
                                  "Rename Script to...",
                                  defaultValue=scriptName,
                                  style=wx.OK|wx.CANCEL )
        retval = dlg.ShowModal()
        if ( retval == 5100 ):
            newScriptName = dlg.GetValue()
            scriptSql = self.scripts[scriptName]
            self.scripts.pop(scriptName)
            self.scripts[newScriptName] = scriptSql

            # Now set new script and update file
            self.dbScriptsValueList.ClearAll()
            # Need to reformat because the list contains more information than required
            keys = list(self.scripts.keys())
            keys.sort()
            self.dbScriptsTableList.Set( list(keys) )

            self.updateScriptsFile()

        return

    ###########################################################################
    # Callback for the Help button
    ###########################################################################
    def menuBarHelpContextCallBack( self, event ):
        #help = htmlHelp( None, "Akorri DB Viewer Help Context", "HelpMain.htm" )
        #help.Show()
        return

    ###########################################################################
    # Callback for the About button
    ###########################################################################
    def menuBarAboutCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        return

    ###########################################################################
    # Callback for the Exit button
    ###########################################################################
    def menuBarExitCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        sys.exit()
        return

###########################################################################
###########################################################################
# Main Menu Callbacks End
###########################################################################
###########################################################################

###########################################################################
###########################################################################
# Main Control DB Start
###########################################################################
###########################################################################

    ###########################################################################
    # Find a free connection.
    ###########################################################################
    def findFreeConnection( self ):
        for conn in self.dbConnections:
            if ( not conn.isLocked() ):
                conn.lock()
                #print("Returning Conn = " + str(conn))
                return conn

        # If no free connections, then free them because this should never be the case
        for conn in self.dbConnections:
            conn.unlock()

        #wx.MessageBox("No connections are free " + str(len(self.dbConnections)))
        self.dbConnections[0].lock()
        return self.dbConnections[0]

    ###########################################################################
    # My Sql function to execute the command and fetch all of the data
    ###########################################################################
    def executeAll( self, cmd, ignoreError=False ):
        # Need to walk the connections and find out which ones are not locked
        # and use that.

        # Log the sql command
        log = time.ctime() + " : " + cmd
        SQL_LOG.write(log + "\n")
        SQL_LOG.flush()
        multiCmd=False
        if ( ";" in cmd ):
            multiCmd=True
        rows = ()
        if ( not self.sqLiteSelected ):
            conn = self.findFreeConnection()
            try:
                self.dbTimeoutCounter = 0
                conn.dbWorker.execute( cmd, multiCmd )
                rows = conn.dbWorker.fetchall()
            except mysql.connector.Error as e:
                if ( ignoreError == False ): 
                    wx.MessageBox( "Query Failure (execute all): " + str((e.args[0], e.args[1])) )
                if ( conn ): 
                    conn.unlock()
                    conn = None
                if ( e.args[0] != 1064 and e.args[0] != 1054 ):
                    self.connect()
                    conn = self.findFreeConnection()
                    conn.dbWorker.execute( cmd, multiCmd )
                    rows = conn.dbWorker.fetchall()
                return ["Error"]
            except ImportError as e:
                # It looks like when we get this error, the connections
                # have timed out, so need to reconnect.
                self.connect()
                conn = self.findFreeConnection()
                conn.dbWorker.execute( cmd, multiCmd )
                rows = conn.dbWorker.fetchall()
                return ["Error"]
            except Exception as e:
                traceback.print_exc()
                return ["Error"]
            finally:
                if ( conn ): conn.unlock()

            # So the new mysql connector that I am using will return everything
            # in bytearray format.  So need to reformat the rows for unicode.
            newRows = []
            for row in rows:
                r = []
                for column in row:
                    try:
                        r.append(column.decode('utf-8'))
                    except AttributeError:
                        r.append(column)
                newRows.append(r)
            rows = newRows
        else:
            try:
                #print("CMD Before: " + cmd)
                db, cmd = self.sqLiteFindDB(cmd)
                if ( "now" in cmd ):
                    cmd = "select datetime('now')"
                elif ( "show tables" in cmd ):
                    cmd = "select name from sqlite_master where type = 'table'"
                elif ( "show columns" in cmd ):
                    cmd = "PRAGMA table_info('" + cmd.split()[-1] + "')"

                #print("CMD AFTER: " + cmd)
                #print(db)

                if ( not 'sqLiteDbs' in os.getcwd().replace("\\", "/") ):
                    os.chdir(self.bundleDirectory + "\\sqLiteDbs")
                dbConn = sqlite3.connect(db)
                dbWorker = dbConn.cursor()
                dbWorker.execute( cmd )
                rows = dbWorker.fetchall()
                os.chdir(BASE_DIR)
                #print(rows)
                # If this was a show columns request, then we need to reformat.
                if ( "PRAGMA" in cmd ):
                  newrows = []
                  for row in rows:
                     newrows.append(row[1:])
                  rows = newrows

            except sqlite3.Error as e:
                wx.MessageBox( "Failed to connect to Sqlite Servers: " + str(e.args[0]) )
                return ["Error"]
            
        return rows

    ###########################################################################
    # This method will send a command with no result expected
    ###########################################################################
    def executeNoResult( self, cmd ):
        # Need to walk the connections and find out which ones are not locked
        # and use that.
        # Log the sql command
        log = time.ctime() + " : " + cmd
        SQL_LOG.write(log + "\n")
        SQL_LOG.flush()
        multiCmd=False
        if ( ";" in cmd ):
            multiCmd=True
        if ( not self.sqLiteSelected ):
            conn = self.findFreeConnection()
            try:
                self.dbTimeoutCounter = 0
                conn.dbWorker.execute( cmd, multiCmd )
                conn.dbConn.commit()
            except mysql.connector.Error as e:
                if ( conn ): 
                    conn.unlock()
                    conn = None
                wx.MessageBox( "Query Failure (execute no result): " + str((e.args[0], e.args[1])) )
                if ( e.args[0] != 1064 and e.args[0] != 1054 ):
                    self.connect()
                    conn = self.findFreeConnection()
                    conn.dbWorker.execute( cmd, multiCmd )
                    conn.dbConn.commit()
            finally:
                if ( conn ): conn.unlock()
        else:
            try:
                #print("CMD Before: " + cmd)
                db, cmd = self.sqLiteFindDB(cmd)
                if ( "now" in cmd ):
                    cmd = "select datetime('now')"
                elif ( "show tables" in cmd ):
                    cmd = "select name from sqlite_master where type = 'table'"
                elif ( "show columns" in cmd ):
                    cmd = "PRAGMA table_info('" + cmd.split()[-1] + "')"

                #print("CMD AFTER: " + cmd)
                #print(db)

                if ( not 'sqLiteDbs' in os.getcwd().replace("\\", "/") ):
                    os.chdir(self.bundleDirectory + "\\sqLiteDbs")
                dbConn = sqlite3.connect(db)
                dbWorker = dbConn.cursor()
                dbWorker.execute( cmd )
                dbConn.commit()
                os.chdir(BASE_DIR)

            except sqlite3.Error as e:
                wx.MessageBox( "Failed to connect to Sqlite Servers: " + str(e.args[0]) )
                return ["Error"]
       
        return 

    ###########################################################################
    # A sqlite helper method to find the db to call
    ###########################################################################
    def sqLiteFindDB(self, cmd ):
        db = "netapp_model.sqlite"
        if ( "netapp_performance" in cmd ):
            db = "netapp_performance.sqlite"
            cmd = cmd.replace("netapp_performance.", "")
        elif ( "netapp_model" in cmd ):
            db = "netapp_model.sqlite"
            cmd = cmd.replace("netapp_model.", "")
        elif ( "opm" in cmd ):
            db = "opm.sqlite"
            cmd = cmd.replace("opm.", "")
        elif ( "acquisition" in cmd ):
            db = "acquisition.sqlite"
            cmd = cmd.replace("acquisition.", "")
        elif ( "scalemonitor" in cmd ):
            db = "scalemonitor.sqlite"
            cmd = cmd.replace("scalemonitor.", "")
        elif ( "ocum" in cmd ):
            db = "ocum.sqlite"
            cmd = cmd.replace("ocum.", "")

        return (db, cmd)


    ###########################################################################
    # This method will send a command with no result expected, but pass back
    # connection.  This should connection can then be used to pass to the
    # fetchOne method to fetch the data.
    ###########################################################################
    def executeForFetching( self, cmd ):
        # Need to walk the connections and find out which ones are not locked
        # and use that.
        log = time.ctime() + " : " + cmd
        SQL_LOG.write(log + "\n")
        SQL_LOG.flush()
        multiCmd=False
        if ( ";" in cmd ):
            multiCmd=True
        conn = None
        if ( not self.sqLiteSelected ):
            conn = self.findFreeConnection()
            try:
                conn.dbWorker.execute( cmd, None, multiCmd )
                self.dbTimeoutCounter = 0
            except mysql.connector.Error as e:
                if ( e.args[1] != "Unread result found." ):
                    wx.MessageBox( "Query Failure (execute for fetching): " + str((e.args[0], e.args[1])) )
                if ( e.args[0] != 1064 and e.args[0] != 1054 ):
                    self.connect()
                    conn = self.findFreeConnection()
                    conn.dbWorker.execute( cmd, None, multiCmd )
                else:
                    conn = None
        else:
            db, cmd = self.sqLiteFindDB(cmd)

            if ( not 'sqLiteDbs' in os.getcwd().replace("\\", "/") ):
                os.chdir(self.bundleDirectory + "\\sqLiteDbs")
            dbConn = sqlite3.connect(db)
            dbWorker = dbConn.cursor()
            dbWorker.execute( cmd )
            conn = DbAccess(dbConn, dbWorker, db)
            os.chdir(BASE_DIR)
            conn.lock()
        return conn

    ###########################################################################
    # Fetch one method.  executeNoResult must be called first.
    ###########################################################################
    def fetchOne( self, conn ):
        row = conn.dbWorker.fetchone()
        r = []
        if ( row != None ):
            for c in row:
                try:
                    r.append(c.decode('utf-8'))
                except AttributeError:
                    r.append(c)
                except UnicodeDecodeError:
                    r.append(c)
                except:
                    r.append(c)
        return r

    ###########################################################################
    # Function to refresh the tables.
    ###########################################################################
    def refreshTables(self):
        global DATABASES
        # Nothing todo if we are using a sqlite version
        if ( self.sqLiteSelected ):
            return

        self.populateDbTree( "", False )
        return

    ###########################################################################
    # Actual connect function
    # This will actually create a connection per database.
    ###########################################################################
    def connect( self ):
        global DATABASES

        # Now try to connect.  We need to see if we are using IP or sqLite
        if ( not self.sqLiteSelected ):
            os.chdir(BASE_DIR)
            self.dbConnections = []
            try:
                self.startDbTimeoutTimer()
                dbConn = mysql.connector.connect( host=self.ip, 
                                                  user=self.user, 
                                                  password=self.passwd, 
                                                  db="",
                                                  auth_plugin='mysql_native_password',
                                                  autocommit=True,
                                                  connection_timeout=86400,
                                                  client_flags=[ClientFlag.MULTI_STATEMENTS])
                dbWorker = dbConn.cursor(buffered=True)
                self.dbConnections.append( DbAccess(dbConn, dbWorker, "") )
                dbWorker.execute( "show databases" )
                rows = dbWorker.fetchall()
                DATABASES = []
                for row in rows:
                    if ( MUST_FILTER_DBS == True and 
                         (row[0] in FILTER_DBS or "#mysql" in row[0]) ): continue
                    print(row[0])
                    DATABASES.append( row[0] )
            
                # Make 10 connections to the db.
                for i in range(0, 9):
                    dbConn = mysql.connector.connect( host=self.ip, 
                                                      user=self.user, 
                                                      passwd=self.passwd, 
                                                      db="",
                                                      auth_plugin='mysql_native_password',
                                                      autocommit=True,
                                                      connection_timeout=86400,
                                                      client_flags=[ClientFlag.MULTI_STATEMENTS] )
                    dbWorker = dbConn.cursor(buffered=True)
                    self.dbConnections.append( DbAccess(dbConn, dbWorker, "") )
                self.connected = True
                self.dbTimeoutCounter = 0

            except mysql.connector.Error as e:
                wx.MessageBox( "Failed to connect to DB Server: " + self.ip + str((e.args[0], e.args[1])) )
                return False
        else:
            # First start the db session
            DATABASES = []
            for db in self.sqLiteDbFiles:
                DATABASES.append(db.split(".")[0])
            DATABASES.sort()
            self.connected = True
        return True

    ###########################################################################
    # This method will convert a MysqlDump file into a Sqlite file
    # Since sqlite does not support a single file with mulitple databases,
    # we need to break out the DB's while we are converting.
    ###########################################################################
    def convertMysqlFileToSqlite( self ):
        if ( sys.platform == "win32" ):
            self.convertMysqlToSqLite.start()
        else:
            self.convertMysqlToSqLite.run()
        self.progressBar.Show()

        return 

    ###########################################################################
    # Helper to get the number of lines in a file
    ###########################################################################
    def numberOfLinesInFile( self, fileName ):
        with open(fileName, encoding='utf8') as f:
            for i, l in enumerate(f):
                pass
        return i + 1
                
    ###########################################################################
    # Callback for when the server IP address drop down is selected.
    ###########################################################################
    def serverIPAddressSelectedCallBack( self, event ):
        # We want to grab the IP and see if there is a username and password
        # associated with this.
        ip = self.dbServerIP.GetValue()

        if ( ip in self.ipHistory.keys() ):
            ip, username, password = self.ipHistory.get(ip)

            if ( username != "" ):
                self.dbUserName.SetValue(username)
                self.dbPassword.SetValue(password)
        return

    ###########################################################################
    # Callback for the connect button.
    ###########################################################################
    def connectButtonCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        self.isBundleInUse = False
        # Try and connect to the database
        if ( not self.sqLiteSelected ):
            ip = self.dbServerIP.GetValue()
            if ( ip == None or ip == "" ):
                wx.MessageBox( "Invalid DB Server Address" )
                return

            # Is this IP address in our history list? If not, then write to file.
            dbUserName = self.dbUserName.GetValue()
            dbPassword = self.dbPassword.GetValue()
            if ( not ip in self.ipHistory.keys() ):
                self.ipHistory[ip] = (ip, dbUserName, dbPassword)
                ipHistoryFileName = SERVER_IP_HISTORY_FILE
                file = open(ipHistoryFileName, "w", encoding='utf8')
                for key in self.ipHistory.keys():
                    xip, xun, xp = self.ipHistory[key]
                    file.write(xip+" "+xun+" "+xp+"\n")
                file.close()
                self.dbServerIP.Append([ip])
            elif ( self.ipHistory[ip][1] == "" or 
                   self.ipHistory[ip][1] != dbUserName or
                   self.ipHistory[ip][2] != dbPassword ):
                # Check to see if the password is empty, if so then need to write
                # the new password into the file. We need to write the whole file
                # out
                ipHistoryFileName = SERVER_IP_HISTORY_FILE
                file = open(ipHistoryFileName, "w", encoding='utf8')
                self.ipHistory[ip] = (ip, dbUserName, dbPassword)
                for key in self.ipHistory.keys():
                    xip, xun, xp = self.ipHistory[key]
                    file.write(xip+" "+xun+" "+xp+"\n")
                file.close()

            if ( not dbUserName ):
                wx.MessageBox( "Must Supply a DataBase User Name" )
                return
            self.ip = ip
            self.user = dbUserName
            self.passwd = dbPassword

            # Now reset everything and connect
            self.resetUIAndConnect()
        else:
            os.chdir(BASE_DIR)
            # SQL Lite has been chosen.
            fileName = self.dbSqLiteFileName.GetValue()
            self.sqLiteMysqlFileName = fileName
            if ( fileName == None or fileName == "" ):
                wx.MessageBox( "Please select a Mysql (sql) file, a support bundle zip file or a previously extracted support bundle" )
                return

            # If this file contains a "*.7z" extension then this is a support bundle.  We only want to
            # extract a few files for now. 
            #         1.) the database export file
            #         2.) the log files
            if ( "7z" in fileName ):
                dlg = wx.MessageDialog( self, 
                           "Note: Depending upon the file size, this could take some time to extract and process.  Continue?",
                           "Extract File?",
                           wx.YES_NO | wx.ICON_QUESTION )
                answer = dlg.ShowModal() == wx.ID_YES
                if ( answer == False ):
                    return

                while ( True ):
                    dlg = wx.DirDialog(self, 
                                        message="Specify directory to extract this support bundle", 
                                        defaultPath=".", 
                                        style=wx.FD_OPEN|wx.FD_CHANGE_DIR )
                    if ( dlg.ShowModal() == wx.ID_OK ):
                        path = dlg.GetPath()
                        self.bundleDirectory = path
                        break
                    else:
                        return
                    dlg.Destroy()

                self.isBundleInUse = True

                os.chdir(self.bundleDirectory)

                # Need progress bar to show user that status
                self.progressBar = ProgressBar.ProgressBar(None, -1, "")
                self.convertMysqlToSqLite = ConvertMySqlToSqLite( self, self.bundleDirectory, self.bundleDirectory + "\\" + SQL_FILE_NAME, self.resetUIAndConnect )
                self.progressBar.setCancelCallBack( self.convertMysqlToSqLite.cancel )

                # Start a text box first
                textBox = TextBox.TextBox(None, wx.Window.NewControlId(), "")
                textBox.setTitle( "Extracting : " + fileName )
                textBox.disableOkButton()
                textBox.Show()
                extractThread = ExtractSupportBundle(self.bundleDirectory, fileName, textBox, self, self.extractSuccessCallback)
                extractThread.start()

                return
            elif ( "dbspy" in fileName ):
                # This is a bundle file that has already been extracted.  So really 
                # just need to setup some stuff.
                # Look in the directory to see if there are any log files.  If so
                # then this directory was extracted from a bundle, mark it as
                # such.
                self.bundleDirectory = os.path.dirname(fileName)
                files = os.listdir(self.bundleDirectory)
                for f in files:
                    if ("log" in f):
                        self.isBundleInUse = True
                        break

                # Need to setup the sqLiteFiles first.
                dirFiles = os.listdir(self.bundleDirectory+"\\sqLiteDbs")
                self.sqLiteDbFiles = []
                for f in dirFiles:
                    if ("sqlite" in f):
                        self.sqLiteDbFiles.append(f.split(".")[0])
                self.resetUIAndConnect()
                return
            else:
                # If this is a MYSQL file (*.sql) then we need to convert to a sqlite file
                dlg = wx.MessageDialog( self, 
                               "Note: Depending upon the file size, this could take some time.  Continue?",
                               "Convert File?",
                               wx.YES_NO | wx.ICON_QUESTION )
                answer = dlg.ShowModal() == wx.ID_YES
                if ( answer == False ):
                    return

                while ( True ):
                    dlg = wx.DirDialog(self, 
                                        message="Specify directory to store SQLite files", 
                                        defaultPath=".", 
                                        style=wx.FD_OPEN|wx.FD_CHANGE_DIR )
                    if ( dlg.ShowModal() == wx.ID_OK ):
                        path = dlg.GetPath()
                        self.bundleDirectory = path
                        break
                    else:
                        return
                    dlg.Destroy()

                mySqlFile = self.dbSqLiteFileName.GetValue()
                self.progressBar = ProgressBar.ProgressBar(None, -1, "")
                self.convertMysqlToSqLite = ConvertMySqlToSqLite( self, self.bundleDirectory, mySqlFile, self.resetUIAndConnect )
                self.progressBar.setCancelCallBack( self.convertMysqlToSqLite.cancel )

                # Ok, need to convert the file to sqlite files
                self.convertMysqlFileToSqlite()

        return

    def extractSuccessCallback( self, parent ):
            # Ok, need to convert the file to sqlite files
            parent.convertMysqlFileToSqlite()
            return

    

    ###########################################################################
    # Reset UI and connect
    ########################################################################## 
    def resetUIAndConnect(self):
        self.currentItemsLabel.SetLabel( "0" )
        self.totalItemsLabel.SetLabel( "0" )
        self.setGauge(0)

        # Now try to connect.
        if ( self.connect() == False ): return 

        version = None
        try:
            version = self.executeAll( "select * from netapp_model.version" )[0]
        except Exception as inst:
            version = [0,0,0,0,0]
     
        self.version = eval(str(version[1])+"."+str(version[2]))
        self.versionString = str(version[1])+"."+str(version[2])+"."+str(version[3])+"."+str(version[4])

        if (self.version == 0.0):
            wx.MessageBox( "This DB is not compatable, but browsing will still work")
            self.populateDbTree( "", False )
            return

        # Warn the user if they are trying to use a version less than 7.2
        if ( self.version < 7.2 ):
            wx.MessageBox( "This DB version ("+self.versionString+") is not compatable with this version of software (it might work)" )


        self.opm_version = ""
        try:
            version = self.executeAll( "select * from opm.version", ignoreError=True)[0]
            self.opm_version = str(version[1])+"."+str(version[2])+"."+str(version[3])+"."+str(version[4])
        except Exception as inst:
            print(inst)

        self.loadScripts()

        buildSummary  = BuildSummaryTable( self )
        if ( sys.platform == "win32" ):
            buildSummary.start()
        else:
            buildSummary.run()

        self.dbTableSearch.SetFont(wx.Font(9, wx.MODERN, wx.FONTSTYLE_ITALIC, wx.NORMAL, 0, "MS Shell Dlg 2"))
        self.dbTableSearch.SetForegroundColour(wx.LIGHT_GREY)
        self.dbTableSearch.SetValue("Table Search")

        # Populate the tree.
        self.populateDbTree( "", False )

        if( self.sqLiteSelected == False ):
            self.SetTitle(SOFTWARE_VERSION + " - " + self.ip)
        else:
            self.SetTitle(SOFTWARE_VERSION + " - " + self.sqLiteMysqlFileName)

        # Now load all of the tables, only if version 2.0
        if ( self.opm_version != "" ):
            ver = eval(self.opm_version.split(".")[0])
            if ( ver >= 2 ):
                self.loadDefinitionTable( "opm.change_type_definition", self.CHANGE_TYPE_DEF )
                self.loadDefinitionTable( "opm.contention_analysis_role_definition", self.CONTENTION_ANAL_ROLE_DEF )
                self.loadDefinitionTable( "opm.dyn_state_definition", self.DYN_STATE_DEF )
                self.loadDefinitionTable( "opm.element_type_definition", self.ELEMENT_TYPE_DEF )
                self.loadDefinitionTable( "opm.stat_type_definition", self.STAT_TYPE_DEF )
                self.loadDefinitionTable( "opm.target_type_definition", self.TARGET_TYPE_DEF )
                self.loadDefinitionTable( "opm.notification_level_definition", self.NOTIFICATION_LEVEL )
                self.loadDefinitionTable( "opm.notification_dynamic_event_option_definition", self.NOTIFICATION_DYNAMIC_EVENT_OPTION )
                self.loadDefinitionTable( "opm.notification_scope_definition", self.NOTIFICATION_SCOPE )
                self.loadDefinitionTable( "opm.notification_type_definition", self.NOTIFICATION_TYPE )
                self.loadDefinitionTable( "opm.notification_umevent_definition", self.NOTIFICATION_UM_EVENT )

        # Now kick off the graph window to show the clusters.
        self.graph.reset()
        self.graph.setParent(self)
        self.graph.createTree( 0, "CLUSTER", "netapp_model.cluster")

        return

    ###########################################################################
    # This method will populate the db tree.
    ###########################################################################
    def populateDbTree( self, filter, useCache ):
 
        if ( useCache == False ):
            self.dbTableTree.DeleteAllItems()
            self.dbValueList.ClearAll()
            self.dbScriptsValueList.ClearAll()
            self.databaseList = []
            self.root = self.dbTableTree.AddRoot("Databases")
            for db in DATABASES:
                tableList = self.executeAll( "show tables from " + db )
                # Need to reformat because the list contains more information than required
    
                database = []
                parent = self.dbTableTree.AppendItem( self.root, db )
                for table in tableList:
                    item = self.dbTableTree.AppendItem( parent, table[0] )
                    # This is an index of name, tree item and a boolean to indicate if the
                    # item is in the tree or not.
                    database.append( [table[0], item, parent, True] )
                self.databaseList.append(database)

            self.dbTableTree.Expand( self.root )
        else:
            # We want to filter out some of the tables
            for db in self.databaseList:
                prev = None
                for table in db:
                    # If the table name is not in the filter and it is in the list
                    # then remove from the tree.
                    if ( filter not in table[0] and table[3] == True ):
                        self.dbTableTree.Delete(table[1])
                        table[3] = False
                    elif ( filter in table[0] and table[3] == False ):
                        # If the filter is in the table name but the table is
                        # not in the tree, we must insert it.
                        if ( prev != None ):
                            item = self.dbTableTree.InsertItem( table[2], prev[1], table[0] )
                            table[1] = item
                        else:
                            # See if the parent has children
                            item = None
                            if ( not self.dbTableTree.ItemHasChildren( table[2] ) ):
                                item = self.dbTableTree.AppendItem( table[2], table[0] )
                            else:
                                item = self.dbTableTree.PrependItem( table[2], table[0] )
                            table[1] = item

                        table[3] = True
                    prev = table


        return

    ###########################################################################
    # This will query the DB for table to id mappings 
    ###########################################################################
    def loadDefinitionTable( self, table, mappingTable ):
        mappingTable.clear()
        try:
            maps = self.executeAll( "select * from " + table )
            for m in maps:
                mappingTable[m[0]] = m[1]
        except:
            pass
        return

###########################################################################
###########################################################################
# Main Control DB End
###########################################################################
###########################################################################

###########################################################################
###########################################################################
#    DB Viewer Methods Start
###########################################################################
##############################################################################


    ###########################################################################
    # A method that will return a list of strings based on the DB columns
    # that were passed in.
    ###########################################################################
    def reformatColumns( self, columns ):
        newColumns = []
        for col in columns:
            newColumns.append(str(col[0]))
        return newColumns

    ###########################################################################
    # Helper function to get the column index based on a column name since it
    # can change based on schema.
    ###########################################################################
    def findColumnIndex(self, columnName, columns):
        index = -1

        walker = 0
        found = False
        for col in columns:
            if ( columnName.lower() == col.lower() ):
                found = True
                break
            walker = walker + 1

        if ( found == True ): 
            index = walker
        else:
            print("Failed to find index for column name: " + columnName)
            print(str(columns))
            try:
                1/0
            except Exception as err: 
                print(Exception, err)
        return index

    ###########################################################################
    # Method to return the tableName and selected item on the screen.
    ###########################################################################
    def getTableNameSelectedItemAndColumns( self ):
        db = ""
        tableName = ""
        selection = None
        rows = []
        columns = []

        if ( self.currentNoteBook == VIEWER_TAB ):
            tableName = self.dbViewerTableSelected
            columns = self.dbViewerColumns
            # Loop over the items to make sure that we get the first item
            rows = self.dbViewerRows
            if ( self.dbViewerFilterOn == True ):
                rows = self.dbViewerFilterList

            for i in range(0, len(rows)):
                if ( self.dbValueList.IsSelected(i) ):
                    selection = rows[i]
                    break
        else:
            # We are on the scripts tab
            columns = self.dbScriptsColumns
            keys = list(self.scripts.keys())
            keys.sort()
            script = self.scripts[keys[self.dbScriptsTableSelected]]
            tableName = self.getTable(script).lower()
            # Loop over the items to make sure that we get the first item
            rows = self.dbScriptsRows
            if ( self.dbScriptsFilterOn == True ):
                rows = self.dbScriptsFilterList

            for i in range(0, len(rows)):
                if ( self.dbScriptsValueList.IsSelected(i) ):
                    selection = rows[i]
                    break


        return tableName, selection, columns

    ###########################################################################
    # Simple function to build the PopUp Menu that shows up when you right
    # select an item.
    ###########################################################################
    def buildPopUp( self ):
        # Build the PopUpMenu
        self.menu = wx.Menu()
        self.menuDict = {}

        tableName, selection, columns = self.getTableNameSelectedItemAndColumns()

        # Build the filter by value menu.
        filterByValueMenu = wx.Menu() 
        a = datetime.datetime(10,2,5)
        count = 0
        for item in selection:
            # Ignore the Date information
            if ( (type(item) == type(a)) or (item == "") or (item == None)):
                count += 1
                continue;
            id = wx.Window.NewControlId() 
            mitem = filterByValueMenu.Append( id, columns[count] + ": " + str(item))
            if ( sys.platform == "win32" ):
                self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, mitem)
            else :
                self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, filterByValueMenu)
            self.menuDict[id] = str(item)
            count += 1
        self.menu.AppendSubMenu( filterByValueMenu, "Filter By Value")

        # Build the filter by column/value menu.
        filterByColumnMenu = wx.Menu() 
        count = 0
        for item in selection:
            # Ignore the Date information
            if ( (type(item) == type(a)) or (item == "") or (item == None)):
                count += 1
                continue;
            id = wx.Window.NewControlId() 
            mitem = filterByColumnMenu.Append( id, columns[count] + " = " + str(item))
            if ( sys.platform == "win32" ):
                self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, mitem)
            else:
                self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, filterByColumnMenu)
            self.menuDict[id] = columns[count] + " = " + str(item)
            count += 1
        self.menu.AppendSubMenu( filterByColumnMenu, "Filter By Column")

        # Need to add other items based on the db and tables selected.
        if ( "netapp_model" in tableName and 
             (tableName == "netapp_model.aggregate" or 
              tableName == "netapp_model.disk" or
              tableName == "netapp_model.lun" or
              tableName == "netapp_model.namespace" or
              tableName == "netapp_model.qos_policy_group" or
              "lif" in tableName or
              "cifs_share" in tableName or
              "vserver" in tableName or
              "node" in tableName or
              "file" in tableName or
              tableName == "netapp_model.cluster" or
              "network_lif" in tableName or
              "fcp_lif" in tableName or
              "fcp_port" in tableName or
              "network_port" in tableName or
              "qos_volume_workload" in tableName or
              "qos_workload" in tableName or
              "qos_workload_detail" in tableName or
              "qos_workload_constituent" in tableName or
              "volume" in tableName ) 
            ):
            index = self.findColumnIndex( "objid", columns )

            # Get all of the columns that are potentials that we can link to
            links = []
            for column in columns[3:]:
                if ( "Id" in column and 
                     not "flex" in column and
                     not "clone" in column and
                     not "sis" in column and
                     not "snap" in column and
                     not "clone" in column and
                     not "export" in column and
                     not "objectstore" in column and
                     not "nvram" in column and
                     not "cpu" in column and
                     not "system" in column and
                     not "partner" in column and
                     not "Partner" in column and
                     not "Identifier" in column and
                     not "Service" in column ):
                    links.append(column)
            
            if ( len(links) != 0 and "cluster" not in tableName):
                openIdMenu = wx.Menu() 
                for link in links:
                    id = wx.Window.NewControlId() 
                    item = openIdMenu.Append( id, link[:-2] + " detail")
                    if ( sys.platform == "win32" ):
                        self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, item )
                    else:
                        wx.EVT_MENU( openIdMenu, id, self.popUpMenuCallBack )
                    self.menuDict[id] = link[:-2] + " detail"
                    # Add stats info
                    id = wx.Window.NewControlId() 
                    item = openIdMenu.Append( id, link[:-2] + " stats")
                    if ( sys.platform == "win32" ):
                        self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, item )
                    else:
                        wx.EVT_MENU( openIdMenu, id, self.popUpMenuCallBack )
                    self.menuDict[id] = link[:-2] + " stats"

                self.menu.AppendSubMenu( openIdMenu, "Inspect "+tableName.split(".")[1]+"s")
                
            if ( "cifs_share" not in tableName and
                 tableName != "lif" and
                 "qos_policy_group" not in tableName and
                 "objectstore" not in tableName):
                id = wx.Window.NewControlId() 
                item = self.menu.Append( id, "View Statistics" )
                self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, item)
                self.menuDict[id] = "View Statistics"

            id = wx.Window.NewControlId() 
            item = self.menu.Append( id, "Edit" )
            self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, item )
            self.menuDict[id] = "Edit"

            # Do not allow graphing the topology on certain objects
            if ( "qos_workload" not in tableName and
                 "qos_volume_workload" not in tableName and
                 "qos_workload" not in tableName and
                 "qos_policy_group" not in tableName and
                 "vserver" not in tableName and
                 "node" not in tableName and
                 "namespace" not in tableName and
                 "port" not in tableName and
                 "lif" not in tableName and
                 "objectstore" not in tableName and
                 "cluster" not in tableName ):
                id = wx.Window.NewControlId() 
                item = self.menu.Append( id, "Graph Topology" )
                self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, item )
                self.menuDict[id] = "Graph Topology"

            if ( ("volume" in tableName and "objectstore" not in tableName) or
                 "lun" in tableName or
                 "file" in tableName and
                 "map" not in tableName and
                 "import" not in tableName and
                 "flex" not in tableName and
                 "qos_volume" not in tableName ):

                if ( "volume" in tableName or 
                     ("lun" in tableName and self.version >= 7.3) or
                     ("file" in tableName and self.version >= 7.3)):
                    # Add the qos detail menu item
                    id = wx.Window.NewControlId() 
                    item = self.menu.Append( id, "View Qos Detail" )
                    self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, item )
                    self.menuDict[id] = "View Qos Detail"
                
                    # Add the qos visit Topology
                    id = wx.Window.NewControlId() 
                    itme = self.menu.Append( id, "View Qos Topology" )
                    self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, item)
                    self.menuDict[id] = "View Qos Topology"

            # For qos Policy, we want to allow the ability to view the qos mappings
            if ( "qos_policy_group" in tableName ):
                # Add the qos mapping menu item
                id = wx.Window.NewControlId() 
                item = self.menu.Append( id, "View Qos Mappings" )
                self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, item)
                self.menuDict[id] = "View Qos Mappings"
       

        elif ( "opm" in tableName and ("event_occurrence" in tableName or 
                "event_participant" in tableName) ):
            item = self.menu.Append( id, "Inspect Event" )
            self.Bind(wx.EVT_MENU, self.popUpMenuCallBack, item )
            self.menuDict[id] = "Inspect Event"

        return

    ###########################################################################
    # When user right clicks in the list, a pop up menu will appear
    ###########################################################################
    def listRightClickCallBack( self, event ):
        self.buildPopUp()
        respos = self.ScreenToClient(wx.GetMousePosition())
        self.PopupMenu( self.menu, respos )
        return

    ###########################################################################
    # Callback for the pop up menu
    ###########################################################################
    def popUpMenuCallBack( self, event ):
        menu = self.menuDict[ event.GetId() ]
        #print(menu)
        if ( "Edit" in menu ):
            self.editButtonCallBack( event )
        elif ( "Add" in menu ):
            self.graphAddSelectedCallBack( event )
        elif ( "detail" in menu ):
            self.exploreElement( event, menu )
        elif ( "stats" in menu ):
            self.viewStatisticsCB( event, menu )
        elif ( menu == "View Statistics" ):
            self.viewStatisticsCB( event, None )
        elif ( menu == "View Collection Performance" ):
            self.viewCollectionPerformance( event )
        elif ( menu == "Inspect Event" ):
            self.inspectEvent( event )
        elif ( menu == "Graph Topology" ):
            self.graphElement( event, menu )
        elif ( menu == "View Qos Detail" ):
            self.viewQosDetail( event )
        elif ( menu == "View Qos Topology" ):
            self.viewVisitTopology( event, menu )
        elif ( menu == "View Qos Mappings" ):
            self.viewQosMappings( event )
        #elif ( menu == "Export Qos Stats for Excel" ):
        #    self.exportQosStatsForExcel( event )
        else:
            # This is a filter request.
            if ( self.currentNoteBook == VIEWER_TAB ):
                self.filterText.SetValue( menu )
                self.filterButtonCallBack(None)
            else:
                self.filterScriptsText.SetValue( menu )
                self.filterScriptsButtonCallBack(None)
        return

    ###########################################################################
    # Simple function to set the gauge value
    ###########################################################################
    def setGauge( self, pos ):
        self.gauge.SetValue( pos )
        return

    ###########################################################################
    # Callback to save off the volumes qos statistics to an Excel xml formatted
    # file. Need to:
    #    o - Find out how many days to save
    #    o - Find out the filename
    ###########################################################################
    def exportQosStatsForExcel( self, event ):
        table, selection, columns = self.getTableNameSelectedItemAndColumns()
        volId = selection[0]

        dlg = wx.TextEntryDialog( None, 
                                  "Please enter number of days to save",
                                  "Number of days to save",
                                  "3",
                                  style=wx.OK|wx.CANCEL )
        retval = dlg.ShowModal()
        if ( retval == 5100 ):
            days = dlg.GetValue()
            # Get the filename to save.
            filename = wx.FileSelector("Save file as", ".", "")
            if ( filename ):
                exporter = QosStatsToExcelXml.QosStatsToExcelXml( self, volId, int(days), filename )
        return

    ###########################################################################
    # Inspect the event occurrence
    ###########################################################################
    def inspectEvent( self, event ):
        table, selection, columns = self.getTableNameSelectedItemAndColumns()

        # Need to find the index for the column so we can pull the id.
        idToQuery = selection[0]
        if ( "event_participant" in table and "stats" not in table ):
            idToQuery = selection[1]
        ev = EventOccurrenceView.EventOccurrenceView(None, -1, "")
        ev.setParent(self)
        ev.setSelection( idToQuery ) 
        ev.Show()
        return

    ###########################################################################
    # Callback from the popup to view a clusters collection performance
    ###########################################################################
    def viewCollectionPerformance( self, event ):

        table, selection, columns = self.getTableNameSelectedItemAndColumns()

        plot = DataPlotter.DataPlotter(None, -1, "Plot Cluster Collection Performance" )
        plot.setParent(self)
        plot.setObject(table, selection, columns)
        plot.Show()
        return


    ###########################################################################
    # Callback from the popup to view statistics on an element.
    ###########################################################################
    def viewStatisticsCB( self, event, menu ):

        table, selection, columns = self.getTableNameSelectedItemAndColumns()

        # If the menu is not null, then this is coming from a sub menu and we 
        # need to get the table, selection and columns
        if (menu != None):
            queryTable = menu.split()[0]
            index = self.findColumnIndex( queryTable+"Id", columns )
            idToQuery = selection[index]
            table = "netapp_model." + queryTable
            selection = self.executeAll("select * from " + table + " where objid = " + str(idToQuery))[0]
            columns = self.executeAll( "show columns from " + table)
            columns = self.reformatColumns( columns )

        # Make sure that the original query has the elementId in its results.
        objIdIndex = self.findColumnIndex( "objid", columns )
        if ( objIdIndex == -1 ):
            wx.MessageBox( "Original Query does not contain the objid so can not inspect" )
            return
      
        plot = DataPlotter.DataPlotter(None, -1, "Plot Data" )
        plot.setParent(self)
        plot.setObject(table, selection, columns)
        plot.Show()
        return

    ###########################################################################
    # Callback for when focus is on the search 
    ###########################################################################
    def dbTableSearchFocusCallBack( self, event ):
        if ( self.dbTableSearch.GetValue() == "Table Search" ):
            self.dbTableSearch.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "MS Shell Dlg 2"))
            self.dbTableSearch.SetForegroundColour(wx.BLACK)
            self.dbTableSearch.SetValue("")
        return

    ###########################################################################
    # Callback for when focus is removed from the search
    ###########################################################################
    def dbTableSearchNoFocusCallBack( self, event ):
        if ( self.dbTableSearch.GetValue() == "" ):
            self.dbTableSearch.SetFont(wx.Font(9, wx.MODERN, wx.FONTSTYLE_ITALIC, wx.NORMAL, 0, "MS Shell Dlg 2"))
            self.dbTableSearch.SetForegroundColour(wx.LIGHT_GREY)
            self.dbTableSearch.SetValue("Table Search")
        return

    ###########################################################################
    # Callback for the filter text enter
    ###########################################################################
    def dbTableSearchTextEnterCallBack( self, event ):
        filter = self.dbTableSearch.GetValue()
        if ( filter == "Table Search" ): return

        if ( len(filter) > 0 ):
            self.dbTableTree.UnselectAll()
            self.populateDbTree( filter, True )
            self.treeHasBeenFiltered = True
        else: 
            if ( self.treeHasBeenFiltered == True ):
                self.dbTableTree.UnselectAll()
                self.populateDbTree( "", True )
                self.treeHasBeenFiltered = False
        # Now need to start to filter the table.
        return

    ###########################################################################
    # Callback to handle the selection of table elements
    ###########################################################################
    def dbTableTreeCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return
        item = event.GetItem()
        # If the item is the "Database" or database, then ignore.
        table = self.dbTableTree.GetItemText(item)
        if ( table == "Databases" or table in DATABASES):
            return

        # Need to find the database we are in.
        parent = self.dbTableTree.GetItemParent(item)
        database = self.dbTableTree.GetItemText(parent)

        table = database + "." + table


        self.statusBar.SetStatusText("Current Table: " + table)

        self.tableSelection( table )
        return


    ###########################################################################
    # Callback to handle the right select selection of table elements
    ###########################################################################
    def dbTableTreeRightClickCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        item = event.GetItem()

        # If the item is the "Database" or database, then ignore.
        table = self.dbTableTree.GetItemText(item)
        if ( table == "Databases" or table in DATABASES):
            return

        # Need to find the database we are in.
        parent = self.dbTableTree.GetItemParent(item)
        database = self.dbTableTree.GetItemText(parent)

        table = database + "." + table

        tableName, selection, columns = self.getTableNameSelectedItemAndColumns()

        # Build the PopUpMenu
        self.menu = wx.Menu()
        self.menuDict = {}
        id = wx.Window.NewControlId()
        item = self.menu.Append( id, "Show Create Table" )
        self.menuDict[id] = ("Show Create Table", table );
        self.Bind(wx.EVT_MENU, self.tableTreePopUpMenuCallBack, item )

        id = wx.Window.NewControlId()
        item = self.menu.Append( id, "Describe Table" )
        self.menuDict[id] = ("Describe Table", table );
        self.Bind(wx.EVT_MENU, self.tableTreePopUpMenuCallBack, item )

        pos =  event.GetPoint()
        newpos = ()
        newpos = (pos[0]+20, pos[1]+180)
        self.PopupMenu( self.menu, newpos )

        return
    
    ###########################################################################
    # Callback for the table tree pop up.
    ###########################################################################
    def tableTreePopUpMenuCallBack( self, event ):
        menu = self.menuDict[ event.GetId() ]
        #print(menu)
        resultTup = []
        title = ""
        if ( "Create" in menu[0] ):
            cmd = "show create table " + menu[1]
            title = "Create Table For: " + menu[1]
            results = self.executeAll( cmd );
            resultTup = results[0]
        elif ( "Describe" in menu[0] ):
            cmd = "describe " + menu[1]
            title = "Describe Table For: " + menu[1]
            results = self.executeAll( cmd );
            resultTup.append( "Table Desscription:\n")
            for r in results:
                resultTup.append( "  Field: " + r[0] + "\n    Type: " + r[1] + "\n    Null: " + str(r[2]) + "\n    Key: " + str(r[3]) + "\n    Default: " + str(r[4]) + "\n    Extra:" + str(r[5]) + "\n")
            
        # Need to format the output.
        textBox = TextBox.TextBox(None, wx.Window.NewControlId(), "")
        textBox.setTitle( title )
        textBox.setTextArray( resultTup )
        textBox.Show()
        return

    ###########################################################################
    # Function to handle the table selections
    ###########################################################################
    def tableSelection( self, table ):
        while ( (self.dbViewerQueryInProgress == 1) and (self.dbViewerTableTimerStopped == 0) ):
            self.stopDbViewerTableTimer = 1
            wx.GetApp().Yield()
        self.dbViewerQueryInProgress = 1

        # Do this on a seperate timer
        if ( self.dbViewerTableTimer != None and self.stopDbViewerTableTimer != 0 ):
            self.stopDbViewerTableTimer = 1
            # Wait for the thread to complete
            while ( self.dbViewerTableTimerStopped == 0 ):
                time.sleep(1)
            self.dbViewerTableTimer = None

        self.dbViewerFilterList = []
        self.dbViewerFilterOn = False
        self.dbValueList.ClearAll()
        # Get the columns
        self.dbViewerTableSelected = table
        columns = self.executeAll( "show columns from " + self.dbViewerTableSelected )
        # Need to reformat
        self.dbViewerColumns = []
        self.dbViewerColumnsFull = columns
        self.dbViewerRows = []
        index = 0
        for col in columns:
            self.dbViewerColumns.append( col[0] )
            if ( "time" not in col[0] ):
                self.dbValueList.InsertColumn( index, col[0], wx.LIST_FORMAT_LEFT, 120 )
            else:
                self.dbValueList.InsertColumn( index, col[0], wx.LIST_FORMAT_LEFT, 230 )
            index = index + 1

        # If this is the continuous_event_occurrance table, make sure to grab the threshold policies
        # to display.
        if ( "continuous_event_occurrence" in self.dbViewerTableSelected ):
            cmd = "select id, name from opm.threshold_policy"
            tps = self.executeAll( cmd )
            self.thresholdPolicies = {}
            for tp in tps:
                self.thresholdPolicies[tp[0]] = tp[1]

        self.dbViewerTableTimer = ViewerTableLoader( self, table )
        if ( sys.platform == "win32" ):
            self.dbViewerTableTimer.start()
        else:
            self.dbViewerTableTimer.run()
        return

    ###########################################################################
    # When user right or left clicks in the table a pop up menu will appear
    ###########################################################################
    def columnSelectForSort( self, event ):

        # This is the id of the column where the event was selected on
        self.columnSelected = event.GetColumn()
        self.sortMenuDict = {}

        # Build the PopUpMenu
        self.columnMenu = wx.Menu()

        id = wx.Window.NewControlId() 
        item = self.columnMenu.Append( id, "Ascending" )
        self.Bind(wx.EVT_MENU, self.colClickCallBack, item )
        self.sortMenuDict[id] = "Ascending"

        id = wx.Window.NewControlId() 
        item = self.columnMenu.Append( id, "Descending" )
        self.Bind(wx.EVT_MENU, self.colClickCallBack, item )
        self.sortMenuDict[id] = "Descending"

        respos = self.ScreenToClient(wx.GetMousePosition())
        self.PopupMenu( self.columnMenu, respos )
        return

    ###########################################################################
    # Callback for the sorting of the columns
    ###########################################################################
    def colClickCallBack( self, event ):
        column = self.columnSelected
        id = event.GetId()
        direction = self.sortMenuDict[id]
        reverse = False
        if ( direction == "Descending" ): reverse = True

        table = ""
        rows = []
        columns = []
        listObject = None

        if ( self.currentNoteBook == VIEWER_TAB ):
            table = self.dbViewerTableSelected
            columns = self.dbViewerColumns
            listObject = self.dbValueList
            # Now reset the rows.
            self.dbValueList.DeleteAllItems()
            # Setup the rows
            self.dbViewerRows = sorted( self.dbViewerRows, key=lambda x: "" if x[column] is None else x[column], reverse=reverse )
            rows = self.dbViewerRows
            if ( self.dbViewerFilterOn == True ):
                self.dbViewerFilterList = sorted( self.dbViewerFilterList, key=lambda x: "" if x[column] is None else x[column], reverse=reverse )
                rows = self.dbViewerFilterList
        else:
            keys = list(self.scripts.keys())
            keys.sort()
            table = self.getTable(self.scripts[ keys[self.dbScriptsTableSelected ] ])
            columns = self.dbScriptsColumns
            listObject = self.dbScriptsValueList
            # Now reset the rows.
            self.dbScriptsValueList.DeleteAllItems()
            # Setup the rows
            self.dbScriptsRows = sorted( self.dbScriptsRows, key=lambda x: "" if x[column] is None else x[column], reverse=reverse )
            rows = self.dbScriptsRows
            if ( self.dbScriptsFilterOn == True ):
                self.dbScriptsFilterList = sorted( self.dbScriptsFilterList, key=noneSorter )
                self.dbScriptsFilterList = sorted( self.dbScriptsFilterList, key=lambda x: "" if x[column] is None else x[column], reverse=reverse )
                rows = self.dbScriptsFilterList

        index = 0
        ltable = lower(table)
        for value in rows:
            col = 1
            listObject.InsertItem( index, str(value[0]) )
            for item in value[1:]:
                setitem = item
                lcolumn = lower(str(columns[col]))
                setitem = decodeColumnValue( self, setitem, ltable, lcolumn )

                try:
                    listObject.SetItem( index, col, str(setitem) )
                except Exception as inst:
                    pass
                    #print("failed on " + str(setitem))
                    #print(inst)
                col = col + 1
            index = index + 1
        return

    def addToFilterHistory(self, filter):
        if ( filter not in self.filterHistory ):
            filterHistoryFileName = os.environ["APPDATA"] + "\\UMFilterHistory.txt"
            file = open(filterHistoryFileName, "a", encoding='utf8')
            file.write(filter+"\n")
            file.close()
            self.filterHistory.append(filter)
            self.filterText.Append([filter])
        return

    ###########################################################################
    # Callback for the filter button
    ###########################################################################
    def filterButtonCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        # If the pre-Filter button is set, then we can not do post filters
        if ( self.isDbViewerPreFilterChecked == True ):
            wx.MessageBox( "Can not apply post filter when pre-filter is checked" )
            return

        table = self.dbViewerTableSelected
        ltable = lower(table)

        filter = self.filterText.GetValue()
        self.addToFilterHistory(filter)
        self.dbValueList.ClearAll()
        complex = False
        if ( filter ):
            try:
                # Is there a complex filter?
                if ( ("=" in filter) or (">" in filter) or ("<" in filter) ) or ("(" in filter): complex = True
                self.dbViewerFilterOn = True
                self.dbViewerFilterList = []
                # Setup the columns
                index = 0
                for col in self.dbViewerColumns:
                    self.dbValueList.InsertColumn( index, col, wx.LIST_FORMAT_LEFT, 120 )
                    index = index + 1

                index = 0
                # Setup the rows
                for row in self.dbViewerRows:
                    col = 1
                    # Is the filter in any of the items
                    found = 0
                    if ( not complex ):
                        for value in row:
                            try:
                                if ( filter in str(value) ):
                                    found = 1
                                    break
                            except:
                                continue
                    else:
                        # Need to build the dictionary of possible values, this is how we will 
                        # Use python to evaluate our objects later.
                        d = {}
                        for i in range(len(self.dbViewerColumns)):
                            d[self.dbViewerColumns[i].lower()] = str(row[i])
    
                        # Now build the eval string
                        evalString = ""
                        skip = 0
                        for s in filter.split():
                            if ( skip == 1 ):
                                # Is s a string?
                                try:
                                    eval(s)
                                    evalString += " " + s + " "
                                except:
                                    evalString += " \"" + s + "\" "
                                skip = 0
                                continue
                            if ( (s == "=") or 
                                 (s == "<") or 
                                 (s == ">") or 
                                 (s == ">=") or 
                                 (s == "<=") ):
                                    ss = s
                                    if ( s == "=" ):
                                        ss = "=="
                                    evalString += " " + ss + " "
                                    skip = 1
                            elif ( (s == "and") or 
                                   (s == "or") ):
                                evalString += " " + s + " "
                            else:
                                try:
                                    eval(d[s.lower()])
                                    evalString += " " + d[s.lower()] + " "
                                except:
                                    try: 
                                        evalString += " \"" + d[s.lower()] + "\" "
                                    except:
                                        wx.MessageBox( "Invalid Filter, needs to be python based syntax if using Post Filter.  Also make sure to use spaces between values and equal signs")
    
                        if ( eval(evalString) ): found = 1
                        #print(evalString)
    
                    if ( not found ): 
                        continue
                    self.dbValueList.InsertItem( index, str(row[0]) )
                    for item in row[1:]:
                        setitem = item
                        lcolumn = lower(str(self.dbViewerColumns[col]))
                        setitem = decodeColumnValue( self, setitem, ltable, lcolumn )

                        try:
                            self.dbValueList.SetItem( index, col, str(setitem) )
                        except Exception as inst:
                            print("failed on " + str(setitem))
                        col = col + 1
                    index = index + 1
                    self.dbViewerFilterList.append(row)

                if ( len(self.dbViewerFilterList) == 0 ):
                    wx.MessageBox( "No Matches Found" )
                else:
                    self.currentItemsLabel.SetLabel( str(len(self.dbViewerFilterList)) )
                    self.totalItemsLabel.SetLabel( str(len(self.dbViewerFilterList)) )
            except:
                raise
                wx.MessageBox( "Invalid Filter, please see Help for format." )
                # Setup the columns
                self.dbViewerFilterOn = False
                self.dbViewerFilterList = []
                index = 0
                for col in self.dbViewerColumns:
                    self.dbValueList.InsertColumn( index, col, wx.LIST_FORMAT_LEFT, 120 )
                    index = index + 1
                index = 0
                # Setup the rows
                for value in self.dbViewerRows:
                    col = 1
                    self.dbValueList.InsertItem( index, str(value[0]) )
                    for item in value[1:]:
                        self.dbValueList.SetItem( index, col, str(item) )
                        col = col + 1
                    index = index + 1
            
        else:
            # Setup the columns
            self.dbViewerFilterOn = False
            self.dbViewerFilterList = []
            index = 0
            for col in self.dbViewerColumns:
                self.dbValueList.InsertColumn( index, col, wx.LIST_FORMAT_LEFT, 120 )
                index = index + 1
            index = 0
            # Setup the rows
            for value in self.dbViewerRows:
                col = 1
                self.dbValueList.InsertItem( index, str(value[0]) )
                for item in value[1:]:
                    lcolumn = lower(str(self.dbViewerColumns[col]))
                    setitem = decodeColumnValue( self, item, ltable, lcolumn )

                    try:
                        self.dbValueList.SetItem( index, col, str(setitem) )
                    except Exception as inst:
                        pass
                        #print("Failed on " + str((index, col)) + " " + str(setitem))
                        #print(inst)
                    col = col + 1
                index = index + 1
            self.currentItemsLabel.SetLabel( str(len(self.dbViewerRows)) )
            self.totalItemsLabel.SetLabel( str(len(self.dbViewerRows)) )
        return


    ###########################################################################
    # Call back handler to do pre filter
    ###########################################################################
    def preFilterCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        if ( self.preFilterCheckBox.IsChecked() ):
            #wx.MessageBox( "Filter will be applied to next selected Table" )
            self.isDbViewerPreFilterChecked = True
        else: 
            self.isDbViewerPreFilterChecked = False
        return

    ###########################################################################
    # If there are changes, then commit them to the database
    ###########################################################################
    def commitChanges( self, selection, new, old ):
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return
        same = 1
        for i in range( len(new) ):
            if ( new[i] != str(old[i]) ):
                same = 0
        if ( same == 1 ): return

        # Commit to the database.
        table = self.dbViewerTableSelected
        for i in range( len(new) ):
            if ( str(new[i]) != str(old[i]) ):
                temp1 = str(new[i])
                temp2 = str(new[0])
                cmd = "UPDATE " + table + " SET " + self.dbViewerColumnsFull[i][0] + " = \'" + temp1 + "\' WHERE " + self.dbViewerColumnsFull[0][0] + " = " + temp2
                #print(cmd)
                self.executeNoResult( cmd )
        # In order to see the changes we need to reconnect beause MYSQLdb caches the data.
        # So reconnect and then reselect the data.
        #self.connectButtonCallBack(1)
        self.tableSelection( self.dbViewerTableSelected )
        return

    ###########################################################################
    # Cancel button handler
    ###########################################################################
    def cancelButtonCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        if ( self.stopDbViewerTableTimer == 0 ):
            self.stopDbViewerTableTimer = 1
        self.dbTableTree.Enable(True)
        return

    ###########################################################################
    # PopOut button handler
    ###########################################################################
    def popOutButtonCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return
        tableName, selection, columns = self.getTableNameSelectedItemAndColumns()
        if ( tableName == None or tableName == "" ):
            wx.MessageBox( "Must select a database table first" )
            return
        tss = TableSnapShot.TableSnapShot(None, -1, "")
        tss.setParent(self)
        if ( len(self.dbViewerFilterList) == 0 ):
            tss.setSelection(tableName, columns, self.dbViewerRows)
        else:
            tss.setSelection(tableName, columns, self.dbViewerFilterList)
        tss.Show()
        return

    ###########################################################################
    # refresh table button handler
    ###########################################################################
    def refreshTablesButtonCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        if ( not self.connected ):
            return
        self.refreshTables()
        return

    ###########################################################################
    # Export button handler
    ###########################################################################
    def exportButtonCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return
        tableName, selection, columns = self.getTableNameSelectedItemAndColumns()
        if ( tableName == None or tableName == "" ):
            wx.MessageBox( "Must select a database table first" )
            return
        te = TableExporter.TableExporter(None, -1, "")
        te.setParent(self)
        te.setTable(tableName)
        te.setColumns(columns)
        te.Show()

        return

    ###########################################################################
    # Callback to graph a particular element
    ###########################################################################
    def graphElement(self, event, menu ):
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return
        #print("Graphing Element")
        tableName, selection, columns = self.getTableNameSelectedItemAndColumns()

        # Make sure that the original query has the elementId in its results.
        objIdIndex = self.findColumnIndex( "objid", columns )
        if ( objIdIndex == -1 ):
            wx.MessageBox( "Original Query does not contain the objid so can not Graph" )
            return

        graph = ElementGraphWindow.ElementGraphWindow(None)
        graph.setParent(self)
        graph.setTitle( "Topology Graph" )
        graph.createTree( selection[objIdIndex], "IO", tableName )
        graph.Show()
        return

    ###########################################################################
    # Callback to graph the visit tree 
    ###########################################################################
    def viewVisitTopology(self, event, menu ):
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return
        tableName, selection, columns = self.getTableNameSelectedItemAndColumns()

        # Make sure that the original query has the elementId in its results.
        objIdIndex = self.findColumnIndex( "objid", columns )
        if ( objIdIndex == -1 ):
            wx.MessageBox( "Original Query does not contain the objid so can not Graph" )
            return

        nameIdIndex = -1
        title = "Topology QoS Graph For Volume: "
        if ( "volume" in tableName ):
            nameIdIndex = self.findColumnIndex( "name", columns )
        elif ( "lun" in tableName ):
            nameIdIndex = self.findColumnIndex( "path", columns )
            title = "Topology QoS Graph For LUN: "
        else:
            # file
            nameIdIndex = self.findColumnIndex( "uuid", columns )
            title = "Topology QoS Graph For File: "
        name = selection[nameIdIndex]
        title = title + name

        tv = ElementGraphWindow.ElementGraphWindow(None)
        tv.setParent(self)
        tv.setTitle( title )
        tv.createTree( selection[objIdIndex], "VISIT", tableName )
        tv.Show()
        return

    ###########################################################################
    # Callback to view the volumes qos details
    ###########################################################################
    def viewQosDetail(self, event):
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return
        table, selection, columns = self.getTableNameSelectedItemAndColumns()

        # Need to find the index for the column so we can pull the id.
        idToQuery = selection[0]
        nameIdIndex = -1
        if ( "volume" in table ):
            nameIdIndex = self.findColumnIndex( "name", columns )
        elif ( "lun" in table ):
            nameIdIndex = self.findColumnIndex( "path", columns )
        else:
            # file
            nameIdIndex = self.findColumnIndex( "uuid", columns )
        name = selection[nameIdIndex]

        ev = QosView.QosViewer(self, -1, "")
        ev.setParent(self)
        if ( ev.setSelection( idToQuery, name, table ) ):
            ev.Show()
        return

    ###########################################################################
    # Callback to view the volumes qos mappings
    ###########################################################################
    def viewQosMappings(self, event):
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return
        table, selection, columns = self.getTableNameSelectedItemAndColumns()

        # Need to find the index for the column so we can pull the id.
        idToQuery = selection[0]

        qpm = QosPolicyMapping.QosPolicyMapping(None, -1, "")
        qpm.setParent(self)
        # If this policy has no objects mapped to it, warn the user
        retVal = qpm.setQosPolicy( selection ) 
        qpm.Show()
        if ( retVal == False ):
            wx.MessageBox( " This QoS Policy does not have any objects mapped to it " )
        return

    ###########################################################################
    # Callback to explore an element.
    ###########################################################################
    def exploreElement(self, event, menu):
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return

        table, selection, columns = self.getTableNameSelectedItemAndColumns()

        # Need to find the index for the column so we can pull the id.
        queryTable = menu.split()[0]
        index = self.findColumnIndex( queryTable+"Id", columns )
        idToQuery = selection[index]

        if ( "Node" in queryTable ):
            queryTable = "node"
        elif ( "qosPolicyGroup" in queryTable ):
            queryTable = "qos_policy_group"
        columns = self.executeAll("show columns from netapp_model." + queryTable)
        columns = self.reformatColumns( columns )
        data = self.executeAll("select * from netapp_model." + queryTable + " where objid="+str(idToQuery))[0]

        ev = ViewAndEdit.ViewAndEditFrame(self, -1, "")
        ev.setParent(self)
        ev.setValues( "netapp_model."+queryTable, columns, data, 0, False )

        return

    ###########################################################################
    # Callback function for the Edit button handler
    ###########################################################################
    def editButtonCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return
        # If nothing selected, exit
        table, selection, columns = self.getTableNameSelectedItemAndColumns()
        selected = self.dbValueList.GetFirstSelected()
        if ( selected == -1 ):
            wx.MessageBox( " Please select an item in the list " )
            return

        # Is the fiter on? If so, then it is a different index, need to find the true index
        if ( self.dbViewerFilterOn == True ):
            filterRow = self.dbViewerFilterList[ selected ]
            # Now find the read index from the columns
            index = 0
            for i in self.dbViewerRows:
                if ( i == filterRow ):
                    selected = index
                    break
                index = index + 1
        
        editWin = ViewAndEdit.ViewAndEditFrame(self)
        editWin.setParent(self)
        editWin.setValues( table, self.dbViewerColumns, self.dbViewerRows[selected], selected, True )
        return

###########################################################################
###########################################################################
#    DB Viewer Methods End
###########################################################################
###########################################################################

###########################################################################
###########################################################################
#    DB Scripts Methods Start
###########################################################################
###########################################################################

    ###########################################################################
    # Scripts Cancel button handler
    ###########################################################################
    def cancelScriptsButtonCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        if ( self.stopDbScriptsTableTimer == 0 ):
            self.stopDbScriptsTableTimer = 1
        self.dbScriptsTableList.Enable(True)
        return

    ###########################################################################
    # Simple function to set the gauge value
    ###########################################################################
    def setGaugeScripts( self, pos ):
        self.gaugeScripts.SetValue( pos )
        return

    ###########################################################################
    # Callback to handle the selection of table elements
    ###########################################################################
    def dbScriptsTableListCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>
        # Check to make sure that we are connected to a DB.
        if ( not self.connected ):
            wx.MessageBox( "Must be connected to a DB to use this" )
            return
        selected = self.dbScriptsTableList.GetSelections()
        self.scriptsTableSelection( selected[0] )
        return

    def getTable(self, script):
        items = script.split()
        fromIndex = 0
        for i in range(0, len(items)):
            if ( items[i] == "from" ):
                fromIndex = i
                break
        
        # table should be right after from
        return items[fromIndex+1]

    def isWildCard( self, script ):
        items = script.lower().split()
        if ( items[0] == "select" and items[1] == "*" ): return True
        return False
        
    ###########################################################################
    # Function to handle the table selections
    ###########################################################################
    def scriptsTableSelection( self, selected ):
        while ( (self.dbScriptsQueryInProgress == 1) and (self.dbScriptsTableTimerStopped == 0) ):
            self.stopDbScriptsTableTimer = 1
            wx.GetApp().Yield()
        self.dbScriptsQueryInProgress = 1

        # Do this on a seperate timer
        if ( self.dbScriptsTableTimer != None and self.stopDbScriptsTableTimer != 0 ):
            self.stopDbScriptsTableTimer = 1
            # Wait for the thread to complete
            while ( self.dbScriptsTableTimerStopped == 0 ):
                time.sleep(1)
            self.dbScriptsTableTimer = None

        self.dbScriptsFilterOn = False
        self.dbScriptsValueList.ClearAll()
        self.dbScriptsTableSelected = selected

        # Get the script requested to run.
        keys = list(self.scripts.keys())
        keys.sort()
        script = self.scripts[keys[selected]]

        # Get the columns
        # First get all the columns and breakdown
        try:
            table = self.getTable( script )
            wildCard = self.isWildCard(script)
            columns = []
            if ( wildCard == True ):
                columns = self.executeAll( "show columns from " + table )
            else:
                items = script.split()
                start = False
                for item in items[1:]:
                    if ( item.lower() == "from" ): break
                    cols = item.split(",")
                    for col in cols:
                        if ( col == "" ): continue
                        columns.append([col])
               
            # Need to reformat
            self.dbScriptsColumns = []
            self.dbScriptsRows = []
            index = 0
            lscript = script.lower()
            for col in columns:
                self.dbScriptsColumns.append( col[0] )
                self.dbScriptsValueList.InsertColumn( index, col[0], wx.LIST_FORMAT_LEFT, 120 )
                index = index + 1

            self.dbScriptsTableTimer = DbScriptsTableLoad( self, selected )
            if ( sys.platform == "win32" ):
                self.dbScriptsTableTimer.start()
            else:
                self.dbScriptsTableTimer.run()
        except:
            self.dbScriptsTableList.Enable(True)

        return

    ###########################################################################
    # Callback for the Scripts filter button
    ###########################################################################
    def filterScriptsButtonCallBack(self, event): # wxGlade: UmDbSpy.<event_handler>

        keys = list(self.scripts.keys())
        keys.sort()
        script = self.scripts[ keys[self.dbScriptsTableSelected] ]
        ltable = self.getTable(script).lower()

        filter = self.filterScriptsText.GetValue()
        self.dbScriptsValueList.ClearAll()
        complex = False
        if ( filter ):
            try:
                # Is there a complex filter?
                if ( ("=" in filter) or (">" in filter) or ("<" in filter) ) or ("(" in filter): complex = True
                self.dbScriptsFilterOn = True
                self.dbScriptsFilterList = []
                # Setup the columns
                index = 0
                for col in self.dbScriptsColumns:
                    self.dbScriptsValueList.InsertColumn( index, col, wx.LIST_FORMAT_LEFT, 120 )
                    index = index + 1

                index = 0
                # Setup the rows
                for row in self.dbScriptsRows:
                    col = 1
                    # Is the filter in any of the items
                    found = 0
                    if ( not complex ):
                        for value in row:
                            try:
                                if ( filter in str(value) ):
                                    found = 1
                                    break
                            except:
                                continue
                    else:
                        # Need to build the dictionary of possible values, this is how we will 
                        # Use python to evaluate our objects later.
                        d = {}
                        for i in range(len(self.dbScriptsColumns)):
                            d[self.dbScriptsColumns[i].lower()] = str(row[i])
    
                        # Now build the eval string
                        evalString = ""
                        skip = 0
                        for s in filter.split():
                            if ( skip == 1 ):
                                # Is s a string?
                                try:
                                    eval(s)
                                    evalString += " " + s + " "
                                except:
                                    evalString += " \"" + s + "\" "
                                skip = 0
                                continue
                            if ( (s == "=") or 
                                 (s == "<") or 
                                 (s == ">") or 
                                 (s == ">=") or 
                                 (s == "<=") ):
                                    ss = s
                                    if ( s == "=" ):
                                        ss = "=="
                                    evalString += " " + ss + " "
                                    skip = 1
                            elif ( (s == "and") or 
                                   (s == "or") ):
                                evalString += " " + s + " "
                            else:
                                try:
                                    eval(d[s.lower()])
                                    evalString += " " + d[s.lower()] + " "
                                except:
                                    evalString += " \"" + d[s.lower()] + "\" "
    
                        if ( eval(evalString) ): found = 1
                        #print(evalString)
    
                    if ( not found ): 
                        continue
                    self.dbScriptsValueList.InsertItem( index, str(row[0]) )
                    for item in row[1:]:
                        setitem = item
                        lcolumn = lower(str(self.dbScriptsColumns[col]))
                        setitem = decodeColumnValue( self, setitem, ltable, lcolumn )

                        try:
                            self.dbScriptsValueList.SetItem( index, col, str(setitem) )
                        except Exception as inst:
                            print("failed on " + str(setitem))
                        col = col + 1
                    index = index + 1
                    self.dbScriptsFilterList.append(row)

                if ( len(self.dbScriptsFilterList) == 0 ):
                    wx.MessageBox( "No Matches Found" )
                else:
                    self.currentScriptsItemsLabel.SetLabel( str(len(self.dbScriptsFilterList)) )
                    self.totalScriptsItemsLabel.SetLabel( str(len(self.dbScriptsFilterList)) )
            except:
                raise
                wx.MessageBox( "Invalid Filter, please see Help for format." )
                # Setup the columns
                self.dbScriptsFilterOn = False
                self.dbScriptsFilterList = []
                index = 0
                for col in self.dbScriptsColumns:
                    self.dbScriptsValueList.InsertColumn( index, col, wx.LIST_FORMAT_LEFT, 120 )
                    index = index + 1
                index = 0
                # Setup the rows
                for value in self.dbScriptsRows:
                    col = 1
                    self.dbScriptsValueList.InsertItem( index, str(value[0]) )
                    for item in value[1:]:
                        self.dbScriptsValueList.SetItem( index, col, str(item) )
                        col = col + 1
                    index = index + 1
            
        else:
            # Setup the columns
            self.dbScriptsFilterOn = False
            self.dbScriptsFilterList = []
            index = 0
            for col in self.dbScriptsColumns:
                self.dbScriptsValueList.InsertColumn( index, col, wx.LIST_FORMAT_LEFT, 120 )
                index = index + 1
            index = 0
            # Setup the rows
            for value in self.dbScriptsRows:
                col = 1
                self.dbScriptsValueList.InsertItem( index, str(value[0]) )
                for item in value[1:]:
                    lcolumn = lower(str(self.dbScriptsColumns[col]))
                    setitem = decodeColumnValue( self, item, ltable, lcolumn )

                    try:
                        self.dbScriptsValueList.SetItem( index, col, str(setitem) )
                    except Exception as inst:
                        pass
                        #print("Failed on " + str((index, col)) + " " + str(setitem))
                        #print(inst)
                    col = col + 1
                index = index + 1
            self.currentScriptsItemsLabel.SetLabel( str(len(self.dbScriptsRows)) )
            self.totalScriptsItemsLabel.SetLabel( str(len(self.dbScriptsRows)) )
        return

    def hardExit( self ):
        sys.exit()
        return

###########################################################################
###########################################################################
#    DB Scripts Methods End
###########################################################################
###########################################################################

###########################################################################
# Sorting None
###########################################################################
def noneSorter(item):
    if not item:
        return ""
    return item

class htmlHelp( wx.Frame ):
    def __init__(self, parent, title, page):
        wx.Frame.__init__(self, parent, -1, title, size=(600,400))
        html = wx.html.HtmlWindow(self)
        if ( "gtk2" in wx.PlatformInfo ):
            html.SetStandardFonts()
        html.LoadPage(page)
        return


###############################################################################
# Helper to execute script code
# Return true: success / false: failure
###############################################################################
def executePythonScript( scriptName ):
    pythonScript = open(scriptName, "r", encoding='utf8').read()
    try:
        exec(pythonScript)
        return True
    except Exception as exception: 
        buffer = StringIO()
        sys.stderr = buffer
        traceback.print_exc()
        sys.stderr = sys.__stderr__
        print(buffer.getvalue())
        return False

    return True
 
###############################################################################
# Helper method to parse the incoming arguments
# Return True if the application should exit after running the script
###############################################################################
def parseCommandLine():
    global MUST_FILTER_DBS, SHOW_LICENSE
    if ( "-h" in sys.argv or "-?" in sys.argv ):
        print()
        print("Usage: UmDbSpy.(py|exe) -s <script name> -h|? -x")
        print("    -h|? : show this help")
        print("    -s <script> : run a python script")
        print("    -x : do not start the UI (good if you only want to run")
        print("         the script)")
        print()
        return False
    if ( "-s" in sys.argv ):
        index = sys.argv.index("-s")
        # See if the user did not pass in the filename
        if ( index+1 >= len(sys.argv) ):
            print()
            print("Please specify the script filename after the -s")
            print()
            return False
        scriptName = sys.argv[index+1]
        # Run the code
        success = executePythonScript(scriptName)
        if ( success == False ):
            return False
    if ( "-x" in sys.argv ):
        return False
    if ( "-n" in sys.argv ):
        MUST_FILTER_DBS = False     
    if ( "-l" in sys.argv ):
        SHOW_LICENSE = False

    return True

###############################################################################
# Setup logging to goto file.
###############################################################################
class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''
 
   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())
 
#logging.basicConfig(
#   level=logging.DEBUG,
#   format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
#   filename="UmDbSpy.log",
#   filemode='a'
#)

#stdout_logger = logging.getLogger('STDOUT')
#sl = StreamToLogger(stdout_logger, logging.INFO)
#sys.stdout = sl
 
#stderr_logger = logging.getLogger('STDERR')
#sl = StreamToLogger(stderr_logger, logging.ERROR)
#sys.stderr = sl


###############################################################################
# Main starting point for the app
###############################################################################
if __name__ == "__main__":

    ###########################################################################
    # Set the global exception
    ###########################################################################
    #sys.excepthook = mainExceptHook

    ###########################################################################
    # Check to see if sombody just wants to run a python script.
    ###########################################################################
    if ( len(sys.argv) > 1 ):
        showUI = parseCommandLine()
        if ( not showUI ):
            sys.exit()

    mainApp = wx.App(0)


    BASE_DIR = os.getcwd()
    path = os.path.abspath(os.path.dirname(__file__))
    #wx.MessageBox( "BASE_DIR = " + path )
    #wx.InitAllImageHandlers()
    UmDbSpy = UmDbSpy(None, -1, "")
    #frame = wx.Frame(UmDbSpy, -1, "UM Db Spy")

    if ( SHOW_LICENSE ):
        sla = SoftwareLicenseAgreement.SoftwareAgreement(None, -1, "")
        sla.setParent(UmDbSpy)
        sla.Show()

    imagePath = "images\\umDbSpySplash.png"
    bitmap = wx.Bitmap(imagePath, wx.BITMAP_TYPE_PNG)
    shadow = wx.WHITE
    splash = AS.AdvancedSplash(UmDbSpy, bitmap=bitmap, timeout=3000,
                               agwStyle=AS.AS_TIMEOUT |
                               AS.AS_CENTER_ON_SCREEN |
                               AS.AS_SHADOW_BITMAP,
                               shadowcolour=shadow)
    splash.Show()
    mainApp.SetTopWindow(UmDbSpy)
    UmDbSpy.Show()
    #vc = VersionCheck.VersionCheck()
    #if ( sys.platform == "win32" ):
    #    vc.start()
    #else:
#       vc.run()
    mainApp.MainLoop()



