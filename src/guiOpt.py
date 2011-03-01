# -*- coding: utf-8 -*-
'''
Created on Feb 16, 2011

@author: Yadavito
'''

import sys

from PySide.QtCore import *
from PySide.QtGui import *

from constants import *

class OptionsDialog(QFrame):
    
    def __init__(self, parent=None):
        super(OptionsDialog, self).__init__(parent)
        
        # runtime group
        self.appOptionsGroup = QGroupBox('Runtime')
        self.appOptionsGroup.setAlignment(Qt.AlignCenter)
        self.checkAutostart = QCheckBox('Begin quiz on application start')
        self.checkEnableLog = QCheckBox('Enable errors logging')
        self.checkEnableFade = QCheckBox('Enable fade effect')
        self.checkAlwaysOnTop = QCheckBox('Always on top')
        self.checkSoundSignal = QCheckBox('Announce quiz with sound')
        self.checkSplashScreen = QCheckBox('Splash screen on launch')
        
        self.appLayout = QVBoxLayout()
        self.appLayout.addWidget(self.checkAutostart)
        self.appLayout.addWidget(self.checkSplashScreen)
        self.appLayout.addWidget(self.checkAlwaysOnTop)
        self.appLayout.addWidget(self.checkSoundSignal)
        self.appLayout.addWidget(self.checkEnableFade)
        self.appLayout.addWidget(self.checkEnableLog)
        
        self.appOptionsGroup.setLayout(self.appLayout)
        
        # fonts group
        self.appFontsGroup = QGroupBox('Fonts')
        self.appFontsGroup.setAlignment(Qt.AlignCenter)
        self.selectSentenceFont = QFontComboBox()
        
        self.fontsLayout = QVBoxLayout()
        self.fontsLayout.addWidget(self.selectSentenceFont)
        
        self.appFontsGroup.setLayout(self.fontsLayout)
        
        # srs group
        self.srsGroup = QGroupBox('SRS Tweaks')
        self.srsGroup.setAlignment(Qt.AlignCenter)
        
        # dictionary group
        self.dictGroup = QGroupBox('JMdict')
        self.dictGroup.setAlignment(Qt.AlignCenter)
        
        # database group
        self.dbGroup = QGroupBox('Database')
        self.dbGroup.setAlignment(Qt.AlignCenter)
                
        # toolbox
        self.toolbox = QToolBox()
        self.toolbox.addItem(self.appOptionsGroup, 'Application')
        self.toolbox.addItem(self.appFontsGroup, 'Fonts')
        self.toolbox.addItem(self.srsGroup, 'Spaced Repetition System')
        self.toolbox.addItem(self.dictGroup, 'Dictionaries')
        self.toolbox.addItem(self.dbGroup, 'Studying items')
        
        # main layout
        self.mainLayout = QVBoxLayout()
        
        #self.accept = QPushButton()
        self.bBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Reset | QDialogButtonBox.Discard )#| QDialogButtonBox.Help)
        self.mainLayout.addWidget(self.toolbox)
        self.mainLayout.addWidget(self.bBox)
        
        self.setLayout(self.mainLayout)
        
        '''
        #self.lcd = QLCDNumber()
        self.intervalDial = QDial()
        self.countdownDial = QDial()
        self.labelTest = QLabel()
        self.labelTest.setText(u"<font style='font-family: Cambria'>This is a test!</font>")
        self.labelSecond = QLabel()
        self.labelSecond.setText(u'This is a second label!')
        '''
        
        self.initializeComposition()
        self.initializeComponents()
    
    def initializeComposition(self):
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        desktop = QApplication.desktop().screenGeometry()

        self.setGeometry(QRect((desktop.width() - O_WIDTH)/2, (desktop.height() - O_HEIGHT)/2, O_WIDTH, O_HEIGHT))

        self.setStyleSheet("QWidget { background-color: rgb(255, 255, 255) }")
        
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum))
    
    def initializeComponents(self):
        #self.toolbox.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.appLayout.setAlignment(Qt.AlignCenter)
        self.mainLayout.setAlignment(Qt.AlignCenter)

        '''
        self.intervalDial.setNotchesVisible(True)
        self.intervalDial.setRange(1,10)
        self.intervalDial.setSingleStep(1)
        '''
        
        #self.intervalDial.setStyleSheet("QDial { background-color: rgb(255, 170, 0) ; }")
        
    def initializeActions(self):
        raise NotImplementedError

'''
app = QApplication(sys.argv)
app.setStyle('plastique')

options = OptionsDialog()
options.show()

sys.exit(app.exec_())
'''
