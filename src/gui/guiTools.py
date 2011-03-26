# -*- coding: utf-8 -*-
'''
Created on Mar 26, 2011

@author: Yadavito
'''

# internal #
import sys, os

# external #
from PySide.QtCore import *
from PySide.QtGui import *

# own #
from settings.constants import *

class Tools(QDialog):
    def __init__(self, parent=None):
        super(Tools, self).__init__(parent)
        
        # flags #
        self.flags = {}
        
        self.mainLayout = QGridLayout()
        
        self.downloadKanjidic = QToolButton()
        self.downloadJmidct = QToolButton()
        self.downloadEdict = QToolButton()
        
        self.statusKanjidict = QLabel()
        self.statusJmdict = QLabel()
        self.statusEdict = QLabel()
        
        self.mainLayout.addWidget(self.downloadKanjidic)
        self.mainLayout.addWidget(self.downloadJmidct)
        self.mainLayout.addWidget(self.downloadEdict)
        
        self.mainLayout.addWidget(self.statusKanjidict, 0, 1)
        self.mainLayout.addWidget(self.statusJmdict, 1, 1)
        self.mainLayout.addWidget(self.statusEdict, 2, 1)
        
        separator = QFrame(); separator.setFrameShape(QFrame.HLine);  separator.setFrameShadow(QFrame.Sunken)
        self.mainLayout.addWidget(separator, 3, 0, 1, 2)
        
        self.pickleJmdict = QToolButton()
        self.statusDump = QLabel()
        self.downloadProgress = QProgressBar()                  
                                 
        self.mainLayout.addWidget(self.pickleJmdict)
        self.mainLayout.addWidget(self.statusDump, 4, 1)
        self.mainLayout.addWidget(self.downloadProgress, 5, 0, 1, 2)
        
        self.setLayout(self.mainLayout)
        
        self.initComposition()
        self.initComponents()
        self.initActions()
        
    def initComposition(self):
        self.setWindowFlags(Qt.Tool)
        self.setWindowTitle(u'Suzu tools')
        
        desktop = QApplication.desktop().screenGeometry()
        self.move( (desktop.width() - T_WIDTH)/2, (desktop.height() - T_HEIGHT)/2 )
        
    def initComponents(self):
        self.mainLayout.setAlignment(Qt.AlignCenter)
        
        self.downloadKanjidic.setText(u'Download kanjidic')
        self.downloadJmidct.setText(u'Download jmdict')
        self.downloadEdict.setText(u'Download edict')
        self.pickleJmdict.setText(u'Piclke edict')
        
        self.downloadKanjidic.setMinimumWidth(100) 
        self.downloadJmidct.setMinimumWidth(100) 
        self.downloadEdict.setMinimumWidth(100) 
        self.pickleJmdict.setMinimumWidth(100) 
        
        self.statusDump.setAlignment(Qt.AlignCenter)
        self.statusJmdict.setAlignment(Qt.AlignCenter)
        self.statusKanjidict.setAlignment(Qt.AlignCenter)
        self.statusEdict.setAlignment(Qt.AlignCenter)
                                              
        self.downloadProgress.setHidden(True)
        
    def initActions(self):
        pass
    
    #-------------- actions -----------------#
    def checkResources(self):
        self.flags = { 'kanjidic' : os.path.exists(PATH_TO_RES + KANJIDIC2), 'jmdict' : os.path.exists(PATH_TO_RES + JMDICT), 
                      'jmdict_pkl' : os.path.exists(PATH_TO_RES + JMDICT_DUMP), 'edict' : True }
    
    def updateStatus(self):
        if self.flags['kanjidic']:
            self.statusKanjidict.setText(u'Availiable')
            self.downloadKanjidic.setDisabled(True)
        else:
            self.statusKanjidict.setText(u'Not availiable')
            self.downloadKanjidic.setEnabled(True)
            
        if self.flags['jmdict']:
            self.statusJmdict.setText(u'Availiable')
            self.downloadJmidct.setDisabled(True)
        else:
            self.statusJmdict.setText(u'Not availiable')
            self.downloadJmidct.setEnabled(True)
            
        if self.flags['edict']:
            self.statusEdict.setText(u'Availiable')
            self.downloadEdict.setDisabled(True)
        else:
            self.statusEdict.setText(u'Not availiable')
            self.downloadEdict.setEnabled(True)

        if self.flags['jmdict_pkl']:
            self.statusDump.setText(u'Availiable')
            self.pickleJmdict.setDisabled(True)
        elif self.flags['jmdict']:
            self.statusDump.setText(u'Not availiable')
            self.pickleJmdict.setEnabled(True)
        else:
            self.statusDump.setText(u'Not downloaded')
            self.pickleJmdict.setDisabled(True)
            
    def showEvent(self, event):
        self.checkResources()
        self.updateStatus()
    
if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('plastique')
    
    tool = Tools()
    tool.show()
    
    sys.exit(app.exec_())