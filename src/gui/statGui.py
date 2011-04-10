# -*- coding: utf-8 -*-
'''
Created on Mar 29, 2011

@author: Yadavito
'''

# external #
from PySide.QtCore import *
from PySide.QtGui import *

class StatsInfo(QDialog):
    def __init__(self, db, parent=None):
        super(StatsInfo, self).__init__(parent)
        
        self.db = db
        
        self.initComposition()
        self.initComponents()
        self.initActions()
        
    #---------- initialization ----------#
    def initComposition(self):
        self.setWindowFlags(Qt.Tool)
    
    def initComponents(self):
        pass
    
    def initActions(self):
        pass
    
    #-------------- actions -------------#
    def initStats(self):
        self.statistics = self.db.getAllSessions()
        
    def showEvent(self, event):
        self.initStats()
        
