# -*- coding: utf-8 -*-
'''
Created on Mar 6, 2011

@author: Yadavito
'''

#from PySide.QtCore import QThread, QTimer

from jtools.jisho import JishoClient
from jdict.db import DBBackgroundUpdater

import ctypes
from ctypes import wintypes
import win32con

from threading import Thread, Event

class BackgroundDownloader(Thread):
    '''It seems, such implementation does not cause slight lags in qt (as opposed to QThread one)'''
    def __init__(self, pause):
        Thread.__init__(self)
        
        self.mayUpdate = False            
        self.hasItemsToUpdate = True
        
        self.waitFor = (pause * 60)/2
        
        self.dbUpdater = DBBackgroundUpdater()
        
        self.event = Event()

    def run(self):
        print 'Imma in yȯr background, updating yȯrz db'
        while not self.event.is_set():
            if self.mayUpdate and self.hasItemsToUpdate:
                item = self.dbUpdater.getSomeItem()
                if item is None : self.hasItemsToUpdate = False; print 'No more items to update'
                else:
                    self.dbUpdater.addExamples(item, JishoClient.getExamples(item.character))
                    print 'Added examples for ' + item.character
            self.event.wait(self.waitFor)

    def stop(self):
        self.event.set()
        
class GlobalHotkeyManager(Thread):
    def __init__(self, function, key):
        Thread.__init__(self)
        self.function = function
        self.key = key
        
        self.byref = ctypes.byref
        self.user32 = ctypes.windll.user32
        
        self.event = Event()

        #TODO: add configurable modifiers & multiple hotkeys
        
        self.id = 1
        self.modifiers = win32con.MOD_CONTROL + win32con.MOD_ALT
        self.vk = ord(self.key)
    
    def registerHotkey(self):        
        if not self.user32.RegisterHotKey(None, self.id, self.modifiers, self.vk):
                print "Unable to register id", id
        else:
            print 'registered ' + str(self.id) + ' ' + self.key
        
    def messageLoop(self):
        try:
            msg = wintypes.MSG()
            #while self.user32.GetMessageA (self.byref (msg), None, 0, 0) != 0 and not self.event.is_set():
            while self.user32.GetMessageA (self.byref (msg), None, 0, 0) != 0:
                if msg.message == win32con.WM_HOTKEY:
                    self.function()
        
            self.user32.TranslateMessage (self.byref (msg))
            self.user32.DispatchMessageA (self.byref (msg))
            
        finally:
            self.unregisterHotkeys()
            print 'ok'
    
    def unregisterHotkeys(self):
        self.user32.UnregisterHotKey(None, self.id)
        
    def run(self):
        self.registerHotkey()
        self.messageLoop()

    def stop(self):
        self.event.set()

#byref = ctypes.byref
#user32 = ctypes.windll.user32
#
#HOTKEYS = {
#  1 : (win32con.VK_F3, win32con.MOD_WIN),
#  2 : (win32con.VK_F4, win32con.MOD_WIN)
#}
#
#def handle_win_f3 ():
#    os.startfile (os.environ['TEMP'])
#
#def handle_win_f4 ():
#    user32.PostQuitMessage (0)
#
#HOTKEY_ACTIONS = {
#  1 : handle_win_f3,
#  2 : handle_win_f4
#}
#
##
## RegisterHotKey takes:
##  Window handle for WM_HOTKEY messages (None = this thread)
##  arbitrary id unique within the thread
##  modifiers (MOD_SHIFT, MOD_ALT, MOD_CONTROL, MOD_WIN)
##  VK code (either ord ('x') or one of win32con.VK_*)
##
#for id, (vk, modifiers) in HOTKEYS.items ():
#    print "Registering id", id, "for key", vk
#    if not user32.RegisterHotKey (None, id, modifiers, vk):
#        print "Unable to register id", id
#
##
## Home-grown Windows message loop: does
##  just enough to handle the WM_HOTKEY
##  messages and pass everything else along.
##
#try:
#    msg = wintypes.MSG()
#    while user32.GetMessageA (byref (msg), None, 0, 0) != 0:
#        if msg.message == win32con.WM_HOTKEY:
#            action_to_take = HOTKEY_ACTIONS.get(msg.wParam)
#            if action_to_take:
#                action_to_take()
#
#    user32.TranslateMessage (byref (msg))
#    user32.DispatchMessageA (byref (msg))
#
#finally:
#    for id in HOTKEYS.keys ():
#        user32.UnregisterHotKey (None, id)


#def my_fun():
#    print '!'    
#
#test = GlobalHotkeyManager(my_fun, 'Q')
#test.start()
#import time
#time.sleep(10)
#test.stop()

#class BackgroundDownloader(QThread):
#    
#        def __init__(self, pause):
#            QThread.__init__(self)
#            
#            self.mayUpdate = False            
#            self.hasItemsToUpdate = True
#            self.dbUpdater = DBBackgroundUpdater()
#            
#            self.updatetimer = QTimer()
#            self.updatetimer.timeout.connect(self.addExamples)
#            self.updatetimer.start( (pause * 60 * 1000)/2 )     #half the pause time
#            
#        def addExamples(self):
#            if self.mayUpdate and self.hasItemsToUpdate:          #TODO: also should not update while options/qdict are shown
#                item = self.dbUpdater.getSomeItem()
#                if item is None : self.hasItemsToUpdate = False
#                else:
#                    self.dbUpdater.addExamples(item, JishoClient.getExamples(item.character))
#                    print 'Example added in background!'

#class HotkeyHooker(QThread):
#
#    def __init__(self, key):
#        #threading.Thread.__init__(self)
#        QThread.__init__(self)
#        self.key = key
#        #self.finished = threading.Event()
#
#    def OnKeyboardEvent(self, event):
#
#        if event.Key == self.key and event.Ascii == 0:
#            #qdict.showQDict = not qdict.showQDict    #nonstop hooking
#            if quiz.isHidden():
#                qdict.showQDict = True  #while qdict is visible - no hooks!
#            else:
#                self.emit(SIGNAL('noQdict')) 
#        return True
#    
#    def run(self):
#        hm = pyHook.HookManager()
#        hm.KeyDown = self.OnKeyboardEvent
#        hm.HookKeyboard()
#        pythoncom.PumpMessages()

#class HotkeyHooker(Thread, QObject): 
#
#    def __init__(self, key):
#        Thread.__init__(self)
#        self.key = key
#        #self.finished = threading.Event()
#
#    def OnKeyboardEvent(self, event):
#
#        if event.Key == self.key and event.Ascii == 0:
#            #qdict.showQDict = not qdict.showQDict    #nonstop hooking
#            if quiz.isHidden():
#                qdict.showQDict = True  #while qdict is visible - no hooks!
##            else:
##                self.emit(SIGNAL('noQdict')) 
#        return True
#    
#    def run(self):
#        hm = pyHook.HookManager()
#        hm.KeyDown = self.OnKeyboardEvent
#        hm.HookKeyboard()
#        pythoncom.PumpMessages()