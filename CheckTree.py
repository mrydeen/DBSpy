import wx

#wx.PlatformInfo=('wxMSW')

wxEVT_CHECKTREECTRL = wx.NewEventType()
EVT_CHECKTREECTRL = wx.PyEventBinder(wxEVT_CHECKTREECTRL, 1)
class CheckTreeCtrlEvent(wx.PyCommandEvent):
    '''
       This event is fired when an item is checked/unchecked.
    '''
    def __init__(self, eventType, id):
        wx.PyCommandEvent.__init__(self, eventType, id)
        self._eventType = eventType

    def SetItem(self, item):
        self._item = item

    def GetItem(self):
        return self._item


CT_AUTO_CHECK_CHILD = 0x9000
CT_AUTO_TOGGLE_CHILD = 0x10000
class CheckTreeCtrl(wx.TreeCtrl):
    '''
       This class was build to be almost identical to `wx.TreeCtrl` plus
       adding support to checked/unchecked items
    '''
    def __init__(self, parent, id, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.TR_HAS_BUTTONS,
                 validator=wx.DefaultValidator, name="checkTree"):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)
        self.__style = style
        self.__il = wx.ImageList(20, 18)
        bmp = self.__MakeBitmap(0, wx.NullBitmap, 20, 18)
        self.__il.Add(bmp)

        bmp = self.__MakeBitmap(1, wx.NullBitmap, 20, 18)
        self.__il.Add(bmp)

        wx.TreeCtrl.SetImageList(self, self.__il)

        self.Bind(wx.EVT_LEFT_DOWN, self.__OnLeftDown)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.__OnActivate, self)
        #self.Bind(wx.EVT_LEFT_DCLICK, self.__OnLeftDClick)
        if not 'wxGTK' in wx.PlatformInfo:
            self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.__OnItemExpanded, self)
            self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.__OnItemCollapsed, self)


    def __MakeBitmap(self, bmp1, bmp2, width, height):
        # Makes a bitmap composed by the checkbox and the user image
        # if it is defined
        bitmap = wx.Bitmap(width, height, -1)

        mdc1 = wx.MemoryDC()
        mdc1.SelectObject( bitmap )
        mdc1.SetBackground(wx.Brush(self.GetBackgroundColour()))
        mdc1.Clear()

        if bmp1:
            if 'wxGTK' in wx.PlatformInfo:
                mdc1.DrawLines([(1,1),(1,14), (13,14), (13,1), (1,1)])
                mdc1.DrawCheckMark(4,4,6,8)
            else:
                mdc1.DrawCheckMark(0,0,18,18)
                mdc1.DrawLines([(1,1),(1,14), (13,14), (13,1), (1,1)])
        else:
            mdc1.DrawLines([(1,1),(1,14), (13,14), (13,1), (1,1)])

        mdc1.SetBackground(wx.Brush(self.GetBackgroundColour()))

        if bmp2 != wx.NullBitmap:
            w = bmp2.GetWidth() + 13
            mdc2 = wx.MemoryDC()
            mdc2.SelectObject(bmp2)
            mdc1.Blit(20,0, w, height, mdc2, 0,0, wx.COPY, True)

        return bitmap


    def __OnItemExpanded(self, evt):
        item = evt.GetItem()
        if item:
            ischeck = self.IsItemChecked(item)
            self.__CheckItem(item, ischeck)
        evt.Skip()


    def __OnItemCollapsed(self, evt):
        item = evt.GetItem()
        if item:
            ischeck = self.IsItemChecked(item)
            self.__CheckItem(item, ischeck)
        evt.Skip()


    def __DoCheckItem(self, item, which, checked, i):
            if i > -1: # There is an image to `which` state                    
                if checked == None: # Toggle check
                    if i % 2 == 0: # Even
                        wx.TreeCtrl.SetItemImage(self,item, i+1, which)
                    else: # Odd
                        wx.TreeCtrl.SetItemImage(self,item, i-1, which)
                else: # Force check/uncheck
                    if checked: # Force check
                        if i % 2 == 0: # Even
                            wx.TreeCtrl.SetItemImage(self,item, i+1, which)
                        else: # Odd
                            wx.TreeCtrl.SetItemImage(self,item, i, which)
                    else: # Force uncheck
                        if i % 2 == 0: # Even
                            wx.TreeCtrl.SetItemImage(self,item, i, which)
                        else: # Odd
                            wx.TreeCtrl.SetItemImage(self,item, i-1, which)


    def __CheckItem(self, item, checked=None):
        if self.__il.GetImageCount() == 2:
            normal = self.GetItemImage(item, wx.TreeItemIcon_Normal)
            self.__DoCheckItem(item, wx.TreeItemIcon_Normal, checked, normal)
            return

        if 'wxGTK' in wx.PlatformInfo:
            normal = self.GetItemImage(item, wx.TreeItemIcon_Normal)
            selected = self.GetItemImage(item, wx.TreeItemIcon_Selected)
            expanded = self.GetItemImage(item, wx.TreeItemIcon_Expanded)
            selectedexpanded = self.GetItemImage(item,
                                          wx.TreeItemIcon_SelectedExpanded)

            self.__DoCheckItem(item, wx.TreeItemIcon_Normal,
                               checked, normal)
            self.__DoCheckItem(item, wx.TreeItemIcon_Selected,
                               checked, selected)
            self.__DoCheckItem(item, wx.TreeItemIcon_Expanded,
                               checked, expanded)
            self.__DoCheckItem(item, wx.TreeItemIcon_SelectedExpanded,
                               checked, selectedexpanded)

        else:
            if not self.GetChildrenCount(item):
                normal = self.GetItemImage(item, wx.TreeItemIcon_Normal)
                selected = self.GetItemImage(item, wx.TreeItemIcon_Selected)
                self.__DoCheckItem(item, wx.TreeItemIcon_Normal, checked, normal)
                self.__DoCheckItem(item, wx.TreeItemIcon_Selected, checked, selected)
            else:
                if self.IsExpanded(item):
                    expanded = self.GetItemImage(item, wx.TreeItemIcon_Expanded)
                    normal = self.GetItemImage(item, wx.TreeItemIcon_Normal)
                    if expanded%2 == 1: normal += 1
                    self.__DoCheckItem(item, wx.TreeItemIcon_Normal,
                                       checked, normal)
                    self.__DoCheckItem(item, wx.TreeItemIcon_Selected,
                                       checked, normal)
                    self.__DoCheckItem(item, wx.TreeItemIcon_SelectedExpanded,
                                       checked, expanded)
                    self.__DoCheckItem(item, wx.TreeItemIcon_Expanded,
                                       checked, expanded)
                else:
                    expanded = self.GetItemImage(item, wx.TreeItemIcon_Expanded)
                    normal = self.GetItemImage(item, wx.TreeItemIcon_Normal)
                    if expanded%2 == 1: normal += 1
                    self.__DoCheckItem(item, wx.TreeItemIcon_Expanded,
                                       checked, expanded)
                    self.__DoCheckItem(item, wx.TreeItemIcon_SelectedExpanded,
                                       checked, expanded)
                    self.__DoCheckItem(item, wx.TreeItemIcon_Selected,
                                       checked, normal)
                    self.__DoCheckItem(item, wx.TreeItemIcon_Normal,
                                       checked, normal)


    def __AutoToggleChild(self, item):
        # Transverse the tree and toggle items
        (child, cookie) = self.GetFirstChild(item)
        while child.IsOk():
            self.__CheckItem(child)
            self.__AutoToggleChild(child)
            (child, cookie) = self.GetNextChild(item, cookie)


    def __AutoCheckChild(self, item, checked):
        # Transverse the tree and check/uncheck items
        (child, cookie) = self.GetFirstChild(item)
        while child.IsOk():
            self.__CheckItem(child, checked)
            self.__AutoCheckChild(child, checked)
            (child, cookie) = self.GetNextChild(item, cookie)


    def __CheckEvent(self, item):
        self.__CheckItem(item)

        if self.__style & CT_AUTO_CHECK_CHILD:
            ischeck = self.IsItemChecked(item)
            self.__AutoCheckChild(item, ischeck)
        elif self.__style & CT_AUTO_TOGGLE_CHILD:
            self.__AutoToggleChild(item)

        e = CheckTreeCtrlEvent(wxEVT_CHECKTREECTRL, self.GetId())
        e.SetItem(item)
        e.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(e)


    def __OnLeftDown(self, evt):
        pt = evt.GetPosition()
        item, flags = self.HitTest(pt)
        if flags & wx.TREE_HITTEST_ONITEMICON:
            self.__CheckEvent(item)
        evt.Skip()


    def __OnActivate(self, evt):
        item = evt.GetItem()
        self.__CheckEvent(item)
        evt.Skip()


#    def __OnLeftDClick(self, evt):
#        pt = evt.GetPosition()
#        item, flags = self.HitTest(pt)
#        if not flags & wx.TREE_HITTEST_ONITEMICON:
#            self.Toggle(item)
#        evt.Skip()


    def CheckItem(self, item, checked=True):
        '''
        Programatically Check `item` Child's ignoring the style flag and
        do not generate EVT_CHECKTREECTRL event.
        '''
        self.__CheckItem(item, checked)
        if self.__style & CT_AUTO_CHECK_CHILD:
            ischeck = self.IsItemChecked(item)
            self.__AutoCheckChild(item, ischeck)
        elif self.__style & CT_AUTO_TOGGLE_CHILD:
            self.__AutoToggleChild(item)


    def CheckChilds(self, item, checked=True):
        '''
        Programatically check/uncheck `item` Childs'.
        Do not generate EVT_CHECKTREECTRL events.
        '''
        if checked == None:
            self.__AutoToggleChild(item)
        else:
            self.__AutoCheckChild(item, checked)


    #def ToggleItem(self, item):
    #    '''
    #    Programatically toggle `item`.
    #    Do not generate EVT_CHECKTREECTRL event.
    #    '''
    #    self.__CheckItem(item, None)
    #    if self.__style & CT_AUTO_CHECK_CHILD:
    #        ischeck = self.IsItemChecked(item)
    #        self.__AutoCheckChild(item, ischeck)
    #    elif self.__style & CT_AUTO_TOGGLE_CHILD:
    #        self.__AutoToggleChild(item)

    #def ToggleChilds(self, item):
    #    '''
    #    Programatically toggle `item` Childs'.
    #    Do not generate EVT_CHECKTREECTRL events.
    #    '''
    #    self.__AutoToggleChild(item)


    def IsItemChecked(self, item):
        '''
        Verify the check/uncheck state of an item.
        Return : False if `item` is not checked.
                 True if `item` is checked.
        '''
        aux = self.GetItemImage(item, wx.TreeItemIcon_SelectedExpanded)
        if aux > -1: return bool(aux % 2)

        aux = self.GetItemImage(item, wx.TreeItemIcon_Expanded)
        if aux > -1: return bool(aux % 2)

        aux = self.GetItemImage(item, wx.TreeItemIcon_Selected)
        if aux > -1: return bool(aux % 2)

        aux = self.GetItemImage(item, wx.TreeItemIcon_Normal)
        if aux > -1: return bool(aux % 2)

        # We never should get here, but if something went wrong
        # return False anyway
        return False


    def AddRoot(self, text, image=0, selImage=-1, data=None):
        '''
        Almost the same as wx.TreeCtrl.AddRoot but don't let the user set
        an image index less than 0 and a selImage different than -1.
        '''
        #if image < 0: image = 0
        return wx.TreeCtrl.AddRoot(self, text, image, -1, data)


    def AppendItem(self, parent, text, image=0, selImage=-1, data=None):
        '''
        Almost the same as wx.TreeCtrl.AppendItem but don't let the user set
        an image index less than 0 and a selImage different than -1.
        '''
        #if image < 0: image = 0
        return wx.TreeCtrl.AppendItem(self, parent, text, image, -1, data)


    def PrependItem(self, parent, text, image=-1, selImage=-1, data=None):
        '''
        Almost the same as wx.TreeCtrl.PrependItem but don't let the user set
        an image index less than 0 and a selImage different than -1.
        '''
        if image < 0: image = 0
        return wx.TreeCtrl.PrependItem(self, parent, text, image, -1, data)


    def SetItemImage(self, item, image, which = wx.TreeItemIcon_Normal,
                     checked=False):
        '''
        Almost the same as wx.TreeCtrl.SetItemImage, except that we can
        set the checkbox check/uncheck state.
        '''
        wx.TreeCtrl.SetItemImage(self, item, image * 2 + int(checked), which)


    def __SetImageList(self, il):
        # The user have is own image list, so we must double the images.
        # For every user image we must add two. One with checkbox uncheck 
        # plus the user image and the other with checkbox check and the same
        # user image. So the even images index are the uncked items and the
        # odd images index are the checked items
        ic = il.GetImageCount()
        self.__il.RemoveAll()
        del self.__il
        w,h = il.GetSize(0)
        w += 20
        self.__il = wx.ImageList(w, h)
        for i in range(ic):
            bmp1 = self.__MakeBitmap(False, il.GetBitmap(i), w, h)
            self.__il.Add(bmp1)
            bmp2 = self.__MakeBitmap(True, il.GetBitmap(i), w, h)
            self.__il.Add(bmp2)
        del il

    def AssignImageList(self, il):
        '''
        See wx.TreeCtrl.AssignImageList.
        '''
        self.__SetImageList(il)
        wx.TreeCtrl.AssignImageList(self, self.__il)


    def SetImageList(self, il):
        '''
        See wx.TreeCtrl.SetImageList.
        '''
        self.__SetImageList(il)
        wx.TreeCtrl.SetImageList(self, self.__il)
