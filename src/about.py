# -*- coding: utf-8 -*-
'''
Created on Feb 22, 2011

@author: Yadavito
'''

import sys
import platform

import PySide
from PySide.QtGui import *
from PySide.QtCore import *

from fonts import Fonts
from constants import __version__

class Filter(QObject):
    def eventFilter(self, object, event):
        
        if event.type() == QEvent.MouseButtonPress:
            if object.parent().logoToggle:
                object.parent().setStyleSheet("QWidget { background-color: rgb(0, 0, 0); }")
                object.parent().aboutApp.setStyleSheet("QLabel { color: rgb(255, 255, 255); }")
                object.parent().about.setStyleSheet("QLabel { color: rgb(255, 255, 255); }")
                object.parent().closeAbout.setStyleSheet("QPushButton { color: rgb(255, 255, 255); }")
 
                #object.parent().setStyleSheet("QFrame { border: 1px white;  }")
                
                object.setPixmap(object.parent().logo_2nd)
                object.parent().logoToggle = False
                
            elif not object.parent().logoToggle:
                object.parent().setStyleSheet("QWidget { background-color: rgb(255, 255, 255); }")
                object.parent().aboutApp.setStyleSheet("QLabel { color: rgb(0, 0, 0); }")
                object.parent().about.setStyleSheet("QLabel { color: rgb(0, 0, 0); }")
                object.parent().closeAbout.setStyleSheet("QPushButton { color: rgb(0, 0, 0); }")
                
                object.setPixmap(object.parent().logo_1st)
                object.parent().logoToggle = True
        
        return False

class About(QFrame):
     
    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        
        #self.logo_scene = QGraphicsScene()
        #self.logo = QGraphicsView()
        
        ### components ###
        self.aboutApp = QLabel(u'')
        self.logo = QLabel(u'')
        self.about = QLabel(u'')
        self.closeAbout = QPushButton(u'')
        
        ### actions ###
        self.closeAbout.clicked.connect(self.hide)
        
        ### layout ###
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        
        self.layout.addWidget(self.aboutApp)
        self.layout.addWidget(self.logo)
        self.layout.addWidget(self.about)
        
        self.main_layout.addLayout(self.layout)
        self.main_layout.addWidget(self.closeAbout)
        
        self.setLayout(self.main_layout)
        
        self.filter = Filter()
        self.logoToggle = False
        
        self.initializeComposition()
        self.initializeComponents()
        
    def initializeComposition(self):
        
        A_WIDTH = 300
        A_HEIGHT = 200
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
        self.setStyleSheet("QWidget { background-color: rgb(255, 255,255); }")
        
        desktop = QApplication.desktop().screenGeometry()

        self.setGeometry(QRect((desktop.width() - A_WIDTH)/2, (desktop.height() - A_HEIGHT)/2, A_WIDTH, A_HEIGHT))

        
    def initializeComponents(self):
        self.logo_1st = QPixmap("../res/suzu.png")
        self.logo_2nd = QPixmap("../res/suzu_neo.png")
        
        self.logo.setPixmap(self.logo_1st)
        self.logo.installEventFilter(self.filter)
        self.logo.setAlignment(Qt.AlignCenter)
        
        self.logoToggle = True
        
        self.aboutApp.setText(u'SUZU （鈴）\nNonstop Spaced Repetition\nLearning System')
        self.about.setText(u'Application:\t' + __version__ + '\nPython:\t' + platform.python_version() + 
                           '\nPySide:\t' + PySide.__version__ + '\nQtCore:\t' + PySide.QtCore.__version__ + 
                           '\nPlatform:\t' + platform.system())
        
        self.aboutApp.setAlignment(Qt.AlignCenter)
        self.about.setAlignment(Qt.AlignCenter)
        
        self.closeAbout.setText(u'善し！')
        self.closeAbout.setFont(QFont(Fonts.HiragiNoMyoutyouProW3, 18))
        #self.closeAbout.setGeometry(QRect(0,0,self.about.width(), self.about.height()))


        #self.logo_scene.addItem(QGraphicsPixmapItem(self.logo_1st))
        #self.logo.setScene(self.logo_scene)

app = QApplication(sys.argv)
app.setStyle('plastique')

about = About()
about.show()

sys.exit(app.exec_())