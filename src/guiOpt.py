# -*- coding: utf-8 -*-
'''
Created on Feb 16, 2011

@author: Yadavito
'''

import sys

from PySide.QtCore import *
from PySide.QtGui import *
#from gui import Quiz

class Filter(QObject):
    def eventFilter(self, object, event):

        if event.type() == QEvent.HoverLeave:
            object.setStyleSheet("QLabel { color: rgb(0, 0, 0); }")

        if event.type() == QEvent.HoverEnter:
            object.setStyleSheet("QLabel { color: rgb(0, 5, 255); }")
            print object.text()
            
        return False

class OptionsDialog(QDialog):
    
    def __init__(self, parent=None):
        super(OptionsDialog, self).__init__(parent)
        
        #self.lcd = QLCDNumber()
        self.intervalDial = QDial()
        self.countdownDial = QDial()
        self.labelTest = QLabel()
        self.labelTest.setText(u'This is a test!')
        self.labelSecond = QLabel()
        self.labelSecond.setText(u'This is a second label!')

        
        #self.labelTest.setMouseTracking(True)
        self.labelTest.setAttribute(Qt.WA_Hover, True)
        self.labelSecond.setAttribute(Qt.WA_Hover, True)

        self.filter = Filter(self.labelTest)
        self.labelTest.installEventFilter(self.filter)
        self.labelSecond.installEventFilter(self.filter)
        
        self.layout_horizontal = QHBoxLayout()

        self.layout_horizontal.addWidget(self.labelTest)
        self.layout_horizontal.addWidget(self.labelSecond)
        self.layout_horizontal.addWidget(self.intervalDial)
        self.layout_horizontal.addWidget(self.countdownDial)
        #self.setLayout(self.layout_horizontal)
        
        self.grid_layout = QGridLayout()#QHBoxLayout()#
        self.grid_layout.setSpacing(0)
        self.labels = []
        #test = [u'あ',u'い',u'ゆ',u'や',u'ら',u'り',u'る',u'れ',u'ろ',u'ま',u'む',u'み',u'め',u'も',u'な',u'に',u'ぬ',u'ね',u'の' ]
        test = [u'空',u'は',u'青い～',u'～ね',u'として',u'軈て',u'、',u'れ',u'ろ',u'ま',u'む',u'み',u'め',u'ものがたり～',u'ならない',u'。' ]
        i = 0
        j = 0
        r = 1   #rows span
        c = 1   #columns span
        n = 16
        for t in test:
            label = QLabel(t)
            label.setFont(QFont(u'ヒラギノ丸ゴ Pro W4', 18))
            #label.setStyleSheet("QLabel { background-color: rgb(255, 255, 255); }")
            #label.font().setStyleStrategy(QFont.PreferQuality)

            label.setAttribute(Qt.WA_Hover, True)
            label.installEventFilter(self.filter)
            
            self.labels.append(label)
            
            if len(label.text()) > 1: c = len(label.text())
            else: c = 1
            
            print i, j, r, c
            print label.text()
            
            if j + c > n: i = i + 1; j = 0
            
            self.grid_layout.addWidget(self.labels.pop(), i, j, r, c)
            #self.grid_layout.setColumnStretch(j,0.1)
            
            if j <= n: j = j + c
            else: j = 0; i = i + 1
        

        #self.grid_layout.setMargin(20)
        self.grid_layout.setGeometry(QRect(100,100,100,100))
        self.grid_layout.setSizeConstraint(self.grid_layout.SetFixedSize)
        #self.grid_layout.setContentsMargins(10, 10, 10, 10)
        #self.grid_layout.setColumnMinimumWidth(0,3)
        #self.grid_layout.setSizeConstraint(QLayout.SizeConstraint(2))
        #self.grid_layout.setSizeConstraint()
        self.setLayout(self.grid_layout)
        
        self.initializeComponents()
    
    def initializeComposition(self):
        raise NotImplementedError
    
    def initializeComponents(self):
        self.intervalDial.setNotchesVisible(True)
        self.intervalDial.setRange(1,10)
        self.intervalDial.setSingleStep(1)
        
        self.setStyleSheet("QWidget { background-color: rgb(255, 255, 255); }")

        #self.intervalDial.setStyleSheet("QDial { background-color: rgb(255, 170, 0) ; }")
        

app = QApplication(sys.argv)

options = OptionsDialog()
options.show()

sys.exit(app.exec_())