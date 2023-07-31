#!/usr/bin/python

#
# (c) Copyright 2008 NetApp, Inc. The code is provided "as is" without
# support or warranties of any kind.  The user is licensed to use the
# code for any legal purpose.
#

#
# $Id: NaServer.py,v 1.1 2007/08/18 14:13:16 jgc Exp jgc $      
# 

__version__ = '0.1'

import socket
import urllib
import xml.sax
import sys
import re
import types

from xml.sax.xmlreader import InputSource
from NaElement import *

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
    pass

class NaAPIFailedException(Exception):
    
    def __init__(self, message, errno=None):
        self.message = message
        self.errno = errno
        return

    def getError(self):
        return self.errno
    
    def getReason(self):
        return self.message
    
    def __str__(self):
        return 'NaAPIFailedException: %s, %s' % (self.errno, self.message)
    
    pass

##
##
class NaServer(object):
    
    _transport_types = ('http', 'https')
    
    _login_styles = ('login', 'hosts')
    
    _server_types = {
        ##type     : (port, url_path)
        'filer'    : (None, '/servlets/netapp.servlets.admin.XMLrequest_filer'),
        'netcache' : (None, '/servlets/netapp.servlets.admin.XMLrequest'),
        'agent'    : (4092, '/apis/XMLrequest'),
        'dfm'      : (8081, '/apis/XMLrequest'),
        };
    
    def __init__(self, server, major_version = 1, minor_version = 0):
        
        self.server = server
        self.major_version = major_version
        self.minor_version = minor_version
        self.vfiler = ''
        self.user = 'root'
        self.password = ''
        self.style = 'login'
        self.transport_type = 'http'
        self.port = None
        self.url_path = None
        self.xmldtd = 'file:/etc/netapp_filer.dtd'
        self.xmlns = 'http://www.netapp.com/filer/admin'
        self.snoop = 0
        
        self.setServerType('filer')
        self.setTransportType('http')
        self.setLoginStyle('login')
        
        return
    
    
    def setVfilerTunneling(self, vfiler):
        
        # XXX not tested.
        
        if self.major_version >= 1 and self.minor_version >= 7:
            # XXX - vfiler naming constraints not yet validated - this is a guess.
            if re.search(r'[^\w\-_]', vfiler): raise NaAPIFailedException('invalid characters in vfiler name')
            self.vfiler = vfiler
        else:
            raise NaAPIFailedException('API version must be > 1.7 to support vfiler tunnelling')
        
        return
    
    
    def setApiVersion(self, major_version, minor_version):
        
        '''Set the API version for requests'''
        
        self.major_version = major_version
        self.minor_version = minor_version
        return
    
    
    def setKeepAliveEnabled(self, keepalive):
        raise NotImplementedError
    
    
    def setAdminUser(self, user, password):
        '''Set the username and password for ONTAPI authentication'''
        self.user = user
        self.password = password
        return
    
    def setLoginStyle(self,  style):
        style = style.lower()
        if style not in self._login_styles:
            return self.fail(13001, 'NaServer.setStyle bad style %s' % style)
        self.style = style
        return None
    
    setStyle = setLoginStyle
    
    def getLoginStyle(self):
        return self.style
    
    getStyle = getLoginStyle
    
    def setServerType(self, server_type):
        
        '''Set the server type.  This controls the base URI and default port
        for a particular server type'''
        
        server_type = server_type.lower()
        info = self._server_types.get(server_type)
        if info is None:
            raise ValueError('bad server_type', server_type)
        
        url_port, url_path = info
        
        self.server_type = server_type
        self.url_path = url_path
        
        if self.port is None:
            self.port = url_port
            pass
        
        return None
    
    
    def getServerType(self):
        return self.server_type
    

    def setTransportType(self, transport_type):
        '''Set the connection transport type'''
        if transport_type not in self._transport_types:
            raise ValueError('invalid transport type', transport_type)
        self.transport_type = transport_type
        return
    
    
    def getTransportType(self):
        return self.transport_type
    
    
    def setPort(self, port):
        
        '''Set TCP port used to connected to the device.'''
        
        self.port = int(port)
        return
    
    
    def getPort(self):
        '''Get TCP port used for connections to device.'''
        return self.port
    
    
    def setSnoop(self, value):
        '''Set debugging of ZAPI calls'''
        self.snoop = value
        return
    
    
    def _setupHandlers(self, url):
        
        handlers = []
        
        passwdmgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        passwdmgr.add_password(None, url, self.user, self.password)
        handler = urllib.request.HTTPBasicAuthHandler(passwdmgr)
        handlers.append(handler)

        if self.snoop:
            handlers.append(urllib.request.HTTPHandler(debuglevel=1))
            handlers.append(urllib.request.HTTPSHandler(debuglevel=1))
            pass
        
        opener = urllib.request.build_opener(*handlers)
        
        urllib.request.install_opener(opener)
        
        return
    
    
    def _buildUrl(self):
        
        destination = self.server
        if self.port:
            destination += ':%s' % self.port
            pass
        
        url = '%s://%s%s' % (self.transport_type, destination, self.url_path)
        return url
    
    
    def _build_xml_header(self):
        
        ## XXX - is this name space correct for the other devices (dfm, etc?)
        
        header  = "<?xml version='1.0' encoding='UTF-8' ?>\n"
        header += "<!DOCTYPE netapp SYSTEM '%s'>\n" % self.xmldtd
        header += "<netapp version='%s.%s' xmlns='%s'" % (self.major_version, self.minor_version, self.xmlns)
        
        if self.vfiler: header += ' vfiler="%s"' % self.vfiler
        
        header += '>'
        
        return header
    
    
    def _build_xml_footer(self):
        return '</netapp>'
    
    
    def invokeElem(self, element):
        
        '''invoke a single ontapi API call and return an NaElement of the
        result''' 

        url = self._buildUrl()
        self._setupHandlers(url)
        #print( "Url = " + url)

        request = urllib.request.Request(url)
        
        header = self._build_xml_header()
        content = element.toEncodedString()
        footer = self._build_xml_footer()
        
        command = '%s%s%s' % (header, content, footer)
        #print("Command = " + command)
        
        request.data = command.encode('utf-8')
        #print(str(request))
        
        response = urllib.request.urlopen(request)
        #print(response)
        
        text = response.read().decode('utf-8')
        #print( "Text = " + text)
        
        handler = NetAppHandler()
        
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.setFeature(xml.sax.handler.feature_external_ges, 0)
        parser.setFeature(xml.sax.handler.feature_external_pes, 0)
        
        inputsrc = InputSource()
        inputsrc.setByteStream(StringIO(text))
        x = parser.parse(inputsrc)
        
        netapp = handler.results
        
        if netapp.name != 'netapp':
            raise NaAPIFailedException('top stack XML reply is not <netapp>')
        results = netapp.getChildByName('results')
        if results is None:
            raise NaAPIFailedException('missing results')
        
        if self.snoop:
            print(sys.stderr, results.toPrettyString())
            pass
        
        
        status = results.getAttr('status')
        if status != 'passed':
            errno = int(results.getAttr('errno'))
            reason = results.getAttr('reason')
            raise NaAPIFailedException(reason, errno)
        
        del request
        del response
        
        return results
    
    
    def invoke(self, command, args={}):
        
        '''build and invoke an API command.  The arguments are supplied a
        dictionary'''
        
        element = NaElement(command)
        
        for name, value in args.items():
            
            element.addNewChild(name, value)
            pass
        
        return self.invokeElem(element)
    
    
    def close(self):
        return
    
    pass


##
##
##
class NetAppHandler(xml.sax.handler.ContentHandler):
    
    def __init__(self):
        self.root = NaElement('')
        self.stack = []
        return
    
    def startDocument(self):
        self.stack = []
        self.stack.append(self.root)
        return
    
    def endDocument(self):
        self.results = self.root.children[0]
        return
    
    def startElement(self, name, attrs):
        
        element = NaElement(name)
        self.stack.append(element)
        
        for attr_name in attrs.getNames():
            attr_value = attrs.getValue(attr_name)
            element.setAttr(attr_name, attr_value)
            pass
        
        return
    
    def endElement(self, name):
        node = self.stack.pop()
        top = self.stack[-1]
        top.addChildElem(node)
        
        return
    
    def characters(self, data):
        top = self.stack[-1]
        top.appendContent(data)
        return
    
    pass

