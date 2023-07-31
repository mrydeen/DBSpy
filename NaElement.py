#!/usr/bin/python

#
# (c) Copyright 2008 NetApp, Inc. The code is provided "as is" without
# support or warranties of any kind.  The user is licensed to use the
# code for any legal purpose.
#

#
# $Id: NaElement.py,v 1.1 2007/08/18 14:13:08 jgc Exp jgc $	
#

__version__ = '0.1'

import re
import xml.sax.saxutils
import arc4

class NetAppObject(dict):
    
    def __init__(self):
        dict.__init__(self)
        self._firstname = None
        
        return
    
    def __setitem__(self, name, value):
        if self._firstname is None: self._firstname = name
        dict.__setitem__(self, name, value)
        return
    
#    def __getattribute__(self, name):
#        try:
#            return dict.__getitem__(self, name)
#        except KeyError:
#            return None
#
#        pass
    
    def __getattr__(self, name):
        try:
            return dict.__getitem__(self, name)
        except KeyError:
            pass
        try:
            return dict.__getattr__(self, name)
        except KeyError:
            return None
        pass
    
    def __repr__(self):
        value = self.get(self._firstname)
        return '<NetAppObject: %s=%s>' % (self._firstname, value)
    
    pass


class NaElement:
    
    def __init__(self, name, content=None):
        
        '''Construct an NaElement with specified name and content'''
        
        self.name = name
        self.children = []
        self.attributes = {}
        self.content = None
        
        if content is not None:
            self.setContent(content)
            pass
        
        return
    
    def addChildElem(self, element):
        
        '''Add a child element.'''
        
        self.children.append(element)
        return
    
    def addNewChild(self, name, content):
        
        '''Add a new child element with a given name and content.'''
        
        self.addChildElem(NaElement(name, content))
        return
    
    def addNewEncryptedChild(self, name, content, key):
        
        '''Encrypts data contained in content.'''
        
        if len(key) != 16:
            
            # XXX - this is rather odd.  I would have thought it would
            # be better to return an error for an invalid key
            # length.. This is what the Perl version of ONTAPI seems
            # to be doing, so I'll copy it for the moment.
            
            key += "abracadabradubya";
            key = key[:16]
            pass
        
        encrypted_content = arc4.ARC4(key).crypt(content)
        
        self.addNewChild(name, encrypted_content)
        return
    
    def getAttr(self, name):
        
        '''Get the value of an attribute.'''
        
        return self.attributes[name]
    
    def getChildByName(self, name):
        
        '''Find and return the chid element with a specified name.'''
        
        for child in self.children:
            if child.name == name:
                return child
            pass
        
        return None
    
    def getChildContent(self, name):
        
        '''Find a child with specified name and return its string content.'''
        
        for child in self.children:
            if child.name == name:
                return child.content
            pass
        
        return None
    
    def getChildEncryptedContent(self, name, key):
        
        '''Find a child with the specified name and returns the decrypted content.'''
        
        encrypted_content = self.getChildContent(name)
        
        if len(key) != 16:
            
            # this is rather odd.  I would have thought it would be
            # better to return an error for an invalid key
            # length.. This is what the Perl version of ONTAPI seems
            # to be doing, so I'll copy it for the moment.
            
            key += "abracadabradubya";
            key = key[:16]
            pass
        
        content = arc4.ARC4(key).crypt(encrypted_content)
        
        return content
    
    def getChildIntValue(self, name):
        
        '''Find a child with the specified name and return its content as an int value.'''
        
        for child in self.children:
            if child.name == name:
                return int(child.content)
            pass
        
        return None
    
    def getChildren(self):
        
        '''Get the list of children.'''
        
        return self.children

    def getContent(self):
        
        '''Get the value of the content of this element.'''
        
        return self.content
    
    def getEncryptedContent(self):
        
        '''Decrypts and returns the value of the content of this element.'''
        
        ## XXX - how can you decrypt without a key?
        raise NotImplementedError

    def getName(self):
        
        '''Get the name of this element.'''
        
        return self.name

    def hasChildren(self):
        
        '''Determine if there are children.'''
        
        return bool(self.children)
    
    def setContent(self, content):
        
        '''Set the value of the content to this element.'''
        
        self.content = str(content)
        return
    
    def setName(self, name):
        
        '''Set the name of this element.'''
        self.name = name
        return
    
    
    #-------------------------------------    
    
    ##
    ##
    def setAttr(self, name, value):
        self.attributes[name] = value
        return
    
    ##
    ##
    def appendContent(self, content):
        if self.content is None:
            self.content = str(content)
        else:
            self.content += str(content)
            pass
        return
    
    ##
    ##
    def getChildrenByName(self, name):
        
        '''Find and return the chid element with a specified name.'''
        
        results = []
        
        for child in self.children:
            if child.name == name:
                results.append(child)
                pass
            pass
        
        return results
    
    ##
    ##
    def toObjectList(self):
        
        name = self.name
        list = []
        for child in children:
            for grandchild in child:
                list.append(grandchild.contents)
                pass
            pass
        return list
    
    ##
    ##
    def toObjectArray(self, key='name'):
        
        blah = {}
        for child in self.children:
            naobject = child.toNetAppObject()
            name = naobject.__dict__.get(key)
            blah[name] = naobject
            pass
        
        return blah
    
    ##
    ##
    def toObjects(self):
        
        if self.content is None:
            ## 
            pass
        pass
    
    
    
    ## -----------------------------------------
    ##
    ##
    def old_testConvert(self, objlist):
        
        ## firstly lets test to see if this array is suitable for
        ## conversion to a dictionary.
        
        keyset = set()
        maxlen = 0
        
        ## find the maximum length of the underlying objects and build
        ## a set of the first names in each object.
        
        for obj in objlist:
            maxlen = max(maxlen, len(obj))
            keyset.add(obj.firstname)
            pass
        
        ## if all the underlying objects have the same first name and
        ## the max length of all the attributes of the objects is
        ## larger than one, then we can assume that this object list
        ## can be converted to an array of objects using the firstname
        ## as the key
        
        if maxlen > 1 and len(keyset) == 1:
            #print('XXXXX converting object list -> ', keyset, len(keyset), maxlen, objlist)
            content2 = {}
            key = keyset.pop()
            for obj in objlist:
                name = obj[key]
                content2[name] = obj
                #print(' building x[%s] = %s' % (name, obj))
                pass
            content = content2
            pass
        
        return content
    
    ##
    ##
    def old_toNetAppObject(self, names=[], depth=0):
        
        blah = NetAppObject()
        
        for child in self.children:
            #print('%schild.name = %s' % (' ' * depth, child.name))
            safename = str(child.name)
            
            if child.content is None and child.children:
                
                content = []
                for grandchild in child.children:
                    naobject = grandchild.toNetAppObject(names, depth+1)
                    content.append(naobject)
                    pass
                #content = self.testConvert(content)
                pass
            else:
                content = child.content
                pass
            
            blah[safename] = content
            
            pass
        
        return blah

    ##
    ##
    def testConvert(self, objlist):
        
        keyset = set()
        maxlen = 0
        
        for obj in objlist:
            maxlen = max(maxlen, len(obj))
            keyset.add(obj._firstname)
            pass
        
        if maxlen > 1 and len(keyset) == 1:
            
            content2 = {}
            key = keyset.pop()
            for obj in objlist:
                name = obj[key]
                content2[name] = obj
                
                pass
            content = content2
            pass
        
        return content
    
    ##
    ##
    def mapObjects(self, **kwargs):
        
        objects = kwargs.get('objects', [])
        dicts = kwargs.get('dicts', [])
        lists = kwargs.get('lists', [])
        ints = kwargs.get('ints', [])
        
        ##
        ##
        if self.content:
            
            if self.name in ints:
                return int(self.content)
            else:
                return self.content
            pass
        
        ##
        ##
        if self.name in objects:
            
            result = NetAppObject()
            for child in self.children:
                safename = str(re.subn(r'[^\w]', '_', child.name)[0])
                result[safename] = child.mapObjects(**kwargs)
                pass
            return result
        
        ##
        ##
        if self.name in dicts:
            
            results = {}
            
            for child in self.children:
                result = child.mapObjects(**kwargs)
                results[result.name] = result
                pass
            return results
        
        ##
        ##
        if self.name in lists:
            
            results = []
            for child in self.children:
                for grandchild in child.children:
                    result = grandchild.mapObjects(**kwargs)
                    results.append(result)
                    pass
                pass
            return results
        
        ##
        ##
        if self.children:
            results = []
            for child in self.children:
                results.append(child.mapObjects(**kwargs))
                pass
            return results
        
        return
    
    ##
    ##
    def toNetAppObject(self, names=[], depth=0):
        
        blah = NetAppObject()
        
        for child in self.children:
            print('%schild.name = %s, child.content=%s, child.children=%s' % (' ' * depth, child.name, child.content, child.children))
            safename = re.subn(r'[^\w]', '_', child.name)[0]
            safename = str(safename)
            
            if child.content is None and child.children:
                print('looping on child', child.name)
                content = []
                
                for grandchild in child.children:
                    print('looping on grandchild', grandchild.name)
                    naobject = grandchild.toNetAppObject(names, depth+1)
                    content.append(naobject)
                    pass
                #content = self.testConvert2(content)
                pass
            else:
                content = child.content
                pass
            
            blah[safename] = content
            pass
        
        return blah
    
    ##
    ##
    def getChildrenFlattenedContent(self, name1, name2):
        
        ''' '''
        
        results = []
        for child1 in self.children:
            if child1.name == name1:
                for child2 in child1.children:
                    if child2.name == name2:
                        results.append(child2.content)
                        pass
                    pass
                pass
            pass
        
        return results
    
    
    def getChildrenFlattened(self):
        ''' '''
        
        output = {}
        for child in self.children:
            output[child.name] = child.content
            pass
        return output
    
    ##
    ##
    def toEncodedString(self):
        
        attrs = []
        for name, value in self.attributes.items():
            attrs.append(' %s=%s' % (name, xml.sax.saxutils.quoteattr(value)))
            pass
        attr_str = ''.join(attrs)
        
        output = '<%s%s>' % (self.name, attr_str)
        
        for child in self.children:
            output += child.toEncodedString()
            pass
        
        if self.content is not None:
            output += xml.sax.saxutils.escape(self.content)
            pass
        
        output += '</%s>' % (self.name)
        return output
    
    ##
    ##
    def toPrettyString(self, prefix='', maxdepth=0, depth=0):
        
        indent = '%s%s' % (prefix, '  ' * depth)
        
        attrstr = ''.join([ ' %s=%s' % (name, xml.sax.saxutils.quoteattr(value)) for (name,value) in self.attributes.items()])
        
        output = []
        if not self.children:
            content = self.content
            if content is None: content = ''
            content = xml.sax.saxutils.escape(content)
            output.append('%s<%s%s>%s</%s>' % (indent, self.name, attrstr, content, self.name))
        else:
            output.append('%s<%s%s>' % (indent, self.name, attrstr))
            
            for child in self.children:
                output.append(child.toPrettyString(prefix, maxdepth, depth + 1))
                pass
            output.append('%s</%s>' % (indent, self.name))
            pass
        
        return '\n'.join(output)
    
    ##
    ##
    def toNodeString(self, prefix='', maxdepth=0, depth=0):
        
        results = []
        result = '%sNode: %s=%s [%s]' % ('  ' * depth, self.name, self.content, ' '.join([ '%s=%s' % (name, value) for name,value in self.attributes.items() ] ))
        results.append(result)
        for child in self.children:
            results.append(child.toNodeString(prefix, maxdepth, depth+1))
            pass
        
        return '\n'.join(results)
    
    pass

