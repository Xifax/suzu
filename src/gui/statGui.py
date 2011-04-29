# -*- coding: utf-8 -*-
'''
Created on Mar 29, 2011

@author: Yadavito
'''

# internal #
import time

# external #
from PySide.QtCore import *
from PySide.QtGui import *

class StatsInfo(QDialog):
    def __init__(self, db, parent=None):
        super(StatsInfo, self).__init__(parent)
        
        self.db = db
        
        self.info = QLabel(u'')
        self.closeStats = QPushButton("I've seen enough")
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.info)
        self.layout.addWidget(self.closeStats)
        self.setLayout(self.layout)
        
        self.initComposition()
        self.initComponents()
        self.initActions()
        
    #---------- initialization ----------#
    def initComposition(self):
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Statistics')
    
    def initComponents(self):
        self.info.setWordWrap(True)
        self.info.setAlignment(Qt.AlignCenter)
        
        self.layout.setAlignment(Qt.AlignCenter)
    
    def initActions(self):
        self.closeStats.clicked.connect(self.hide)
    
    #-------------- actions -------------#
    def initStats(self):
        self.statistics = self.db.getAllSessions()
        
        infoText = u'Last ten sessions:<br/><br/>'
        total_time = 0; total_items = 0; active_time = 0; paused_time = 0
        for session in self.statistics[:10]:
            infoText += '<b>' + str(session.date) + '</b>:\t launched <b>' + str(session.times_launched) + '</b> time(s)<br/>' +\
            'Total time: ' + time.strftime('%H:%M:%S', time.gmtime(session.time_running)) +\
            '\tQuiz active: ' + time.strftime('%H:%M:%S', time.gmtime(session.time_active)) +\
            '\tQuiz paused: ' + time.strftime('%H:%M:%S', time.gmtime(session.time_paused)) + '<br/>'   +\
            'Correct items: <b>' + str(session.items_correct) + '</b>\tWrong items: <b>' + str(session.items_wrong) + '</b><br/><br/>'
            
        for session in self.statistics:            
            total_time += session.time_running
            active_time += session.time_active
            paused_time += session.time_paused
            total_items += (session.items_correct + session.items_wrong)
        
        infoText += '<b>Total time running</b>: ' + time.strftime('%H:%M:%S', time.gmtime(total_time)) + '\t' +\
        '<b>Total quiz time</b>: ' + time.strftime('%H:%M:%S', time.gmtime(active_time)) + '<br/>' +\
        '<b>Total paused time</b>: ' + time.strftime('%H:%M:%S', time.gmtime(paused_time)) + '<br/>' +\
        '<b>Total quizzes answered</b>: ' + str(total_items)
        
        self.info.setText(infoText)
        
    def showEvent(self, event):
        self.initStats()
        self.adjustSize()
        