# -*- coding: utf-8 -*-
'''
Created on Apr 10, 2011

@author: Yadavito
'''

# external #
from PySide.QtCore import *
from PySide.QtGui import *

# own #
from settings.constants import *

class QuickLoad(QDialog):
    def __init__(self, options, parent=None):
        super(QuickLoad, self).__init__(parent)
        
        self.options = options
        
        self.layout = QVBoxLayout()
        
        self.showOnStart = QCheckBox('Show this on start')
        separator = QFrame(); separator.setFrameShape(QFrame.HLine); separator.setFrameShadow(QFrame.Sunken)
        self.loadDb = QCheckBox('Database (sqlite)')
        self.loadEdict = QCheckBox('Edict (dict)')
        self.loadRadk = QCheckBox('Raddict (dict)')
        self.loadKanjidic = QCheckBox('Kanjidic (xml)')
        self.loadJmdict = QCheckBox('Jmdict (pickled)')
        self.loadGroups = QCheckBox('Kanji.Odyssey (pickled)')
        
        self.saveAndClose = QPushButton(u'どうしよう')
        
        self.layout.addWidget(self.showOnStart)
        self.layout.addWidget(separator)
        self.layout.addWidget(self.loadDb)
        self.layout.addWidget(self.loadEdict)
        self.layout.addWidget(self.loadRadk)
        self.layout.addWidget(self.loadKanjidic)
        self.layout.addWidget(self.loadJmdict)
        self.layout.addWidget(self.loadGroups)
        
        self.layout.addWidget(self.saveAndClose)
        
        self.setLayout(self.layout)
        
        self.initComposition()
        self.initComponents()
        self.initActions()
        
    def initComposition(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint )
        self.setFixedSize(QSize(L_WIDTH, L_HEIGHT))
        
    def initComponents(self):
        self.layout.setAlignment(Qt.AlignCenter)
    
    def initActions(self):
        self.actionsMenu = QMenu()
        self.actionsMenu.addAction(QAction('Accept and continue', self, triggered=self.saveAndHide))
        self.actionsMenu.addAction(QAction("Don't bug me anymore", self, triggered=self.okayJpeg))
        self.actionsMenu.addSeparator()
        self.actionsMenu.addAction(QAction('Save', self, triggered=self.saveNoClose))
        self.actionsMenu.addAction(QAction('Reset', self, triggered=self.resetDefaults))
        self.actionsMenu.addAction(QAction('Check all', self, triggered=self.checkAll))
        self.actionsMenu.addAction(QAction('Unheck all', self, triggered=self.uncheckAll))
        
        self.saveAndClose.setMenu(self.actionsMenu)
        
    def updateStatus(self):
        self.showOnStart.setChecked(self.options.isLoadingOnStart())
        self.loadDb.setChecked(self.options.isLoadingDb())
        self.loadEdict.setChecked(self.options.isLoadingEdict())
        self.loadKanjidic.setChecked(self.options.isLoadingKdict())
        self.loadRadk.setChecked(self.options.isLoadingRadk())
        self.loadJmdict.setChecked(self.options.isLoadingJmdict())
        self.loadGroups.setChecked(self.options.isLoadingGroups())
        
    def saveStatus(self):
        self.options.setLoadingOnStart(self.showOnStart.isChecked())
        self.options.setLoadingDb(self.loadDb.isChecked())
        self.options.setLoadingEdict(self.loadEdict.isChecked())
        self.options.setLoadingKdict(self.loadKanjidic.isChecked())
        self.options.setLoadingRadk(self.loadRadk.isChecked())
        self.options.setLoadingJmdict(self.loadJmdict.isChecked())
        self.options.setLoadingGroups(self.loadGroups.isChecked())
        
    def showEvent(self, event):
        self.updateStatus()
            
    def saveAndHide(self):
        self.saveStatus()
        self.hide()        
    
    def resetDefaults(self):
        self.updateStatus()
    
    def saveNoClose(self):
        self.saveStatus()
        
    def okayJpeg(self):
        self.showOnStart.setChecked(False)
        self.saveAndHide()
    
    def checkAll(self):
        for item in xrange(0, self.layout.count()):
            widget = self.layout.itemAt(item).widget()
            if isinstance(widget, QCheckBox):
                widget.setChecked(True)
    
    def uncheckAll(self):
        for item in xrange(0, self.layout.count()):
            widget = self.layout.itemAt(item).widget()
            if isinstance(widget, QCheckBox):
                widget.setChecked(False)