# -*- coding: utf-8 -*-
'''
Created on Jan 31, 2011

@author: Yadavito
'''
 
import sys

from srs import srsScheduler
from rtimer import RepeatTimer
from fonts import Fonts

from PySide.QtCore import QTimer,Qt,QRect #TODO: fix to parsimonious imports
from PySide.QtGui import *

class Quiz(QFrame):
     
    def __init__(self, parent=None):
        super(Quiz, self).__init__(parent)

        # kanji info
        self.info = QFrame()

        self.countdown = QProgressBar()
        
        #self.sentence = QLabel(u"<font size=8>これはテストの" + "<b><font color='blue'>文</font></b>" + "であります</font>")
        #self.sentence = QLabel(u"これはテストの" + "<font color='blue'>文</font>" + "でありますですですですですですですですですですでですですですです！")
        self.sentence = QLabel(u'')
        
        #font = QFont(u'メイリオ', 12) #さざなみ明朝      #メイリオ
        #font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 90)

        self.var_1st = QPushButton(u'')
        self.var_2nd = QPushButton(u'')
        self.var_3rd = QPushButton(u'')
        self.var_4th = QPushButton(u'')

        self.answered = QPushButton(u'')
        self.answered.hide()
        #self.answered.setFlat(True)

        self.layout_vertical = QVBoxLayout()
        self.layout_horizontal = QHBoxLayout()
        
        self.layout_horizontal.addWidget(self.var_1st)
        self.layout_horizontal.addWidget(self.var_2nd)
        self.layout_horizontal.addWidget(self.var_3rd)
        self.layout_horizontal.addWidget(self.var_4th)
        
        #QShortcut(QKeySequence("Ctrl+1"), self, None, self.var_1st.click())

        self.layout_vertical.addWidget(self.countdown)
        self.layout_vertical.addWidget(self.sentence)
        self.layout_vertical.addLayout(self.layout_horizontal)
        
        self.layout_horizontal.addWidget(self.answered)
        #layout_global.addLayout(layout_vertical)
        #layout_global.addWidget(self.countdown)
        
        #layout.addWidget(self.button)

        self.setLayout(self.layout_vertical)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayMenu = QMenu()
        
        self.nextQuizTimer = QTimer()
        self.nextQuizTimer.setSingleShot(True)
        self.nextQuizTimer.timeout.connect(self.showQuiz)
        
        self.countdownTimer = QTimer()
        self.countdownTimer.setSingleShot(True)
        self.countdownTimer.timeout.connect(self.timeIsOut)
        
        self.animationTimer = ()
        self.progressTimer = ()
                
        #config here
        self.initializeComposition()
        self.initializeComponents()
        self.setMenus()
        
        self.trayIcon.show()
        
        #!!!
        self.srs = srsScheduler()
        
        #begin work!
        ###self.waitUntilNextTimeslot()
        #self.showQuiz()
        #self.hideButtonsQuiz()
        
        
        #self.trayIcon.showMessage('Test message!')
        
        #self.info.show() --> to do cool stuff
    
    def waitUntilNextTimeslot(self):
        #TODO: no magic constants!
        self.nextQuizTimer.start(10000) #10 seconds for testing purposes
        #self.nextQuizTimer.singleShot(10000, self.showQuiz)
        
    def beginCountdown(self):
        self.countdownTimer.start(10000)
        # yes, this looks awful, ok
        #10000/100
        #RepeatTimer(0.01, self.updateCountdownBar,1000).start()
        self.progressTimer = RepeatTimer(0.01, self.updateCountdownBar, 1000)
        self.progressTimer.start()
        
    def updateCountdownBar(self):
        self.countdown.setValue(self.countdown.value() - 1)
        print self.countdown.value()

    def initializeComposition(self):
        #TODO: may or may not want to control dialog size according to text size
        D_WIDTH = 500
        D_HEIGHT = 176#136

        #down right corner position
        H_INDENT = D_WIDTH + 10 #indent from right
        V_INDENT = D_HEIGHT + 40 #indent from bottom
        
        self.setWindowFlags(Qt.FramelessWindowHint) #and Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setFont(QFont(Fonts.SazanamiMyoutyou, 12))
        #self.setFont(QFont(u'さざなみ明朝 ', 12))
        #self.setWindowOpacity(0.88)
        desktop = QApplication.desktop().screenGeometry()
        self.setGeometry(QRect(desktop.width() - H_INDENT, desktop.height() - V_INDENT, D_WIDTH, D_HEIGHT))
        
        self.setStyleSheet("QWidget { background-color: rgb(255, 255,255);}")
        
    def fade(self):
        if self.windowOpacity() == 1:
            self.animationTimer = RepeatTimer(0.025,self.fadeOut,40)
            self.animationTimer.start()
        else:
            self.animationTimer = RepeatTimer(0.025,self.fadeIn,40)
            self.animationTimer.start()
    
    def fadeIn(self):
        self.setWindowOpacity(self.windowOpacity() + 0.1)
        
    def fadeOut(self):
        self.setWindowOpacity(self.windowOpacity() - 0.1)
        
    def initializeComponents(self):
        self.countdown.setMaximumHeight(6)
        self.countdown.setRange(0,1000)
        self.countdown.setTextVisible(False)
        self.countdown.setStyleSheet("QProgressbar { background-color: rgb(255, 255,255);}")
        
        self.sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #TODO: it's actually nice to change fonts every iteration
        self.sentence.setFont(QFont(Fonts.HiragiNoMarugotoProW4, 18))
        
        #self.var_1st.setStyleSheet("QWidget { border: 1px solid red;}")

        #self.sentence.setStyleSheet("QWidget {border:1px solid rgb(255, 170, 255); }")
        #self.sentence.setFont(QFont(u'小塚明朝 Pro EL', 12))
        #self.sentence.setFont(QFont(u'メイリオ', 12))
        #self.sentence.font().setStyleStrategy(QFont.PreferQuality)
        
        self.sentence.setWordWrap(True)
        self.trayIcon.setIcon(QIcon('../res/cards.ico'))
        
    def updateContent(self):
        self.showButtonsQuiz()
        
        self.srs.getExample(self.srs.getNextItem())
        #TODO: add color modification for quiz part, for example:
        #example = self.srs.getExample(self.srs.getCurrentItem()).replace(self.srs.getCurrentItem(), u"<font color='blue'>" + self.srs.getCurrentItem() + u"</font>") #this is for test only
        #example = u"これはテストの" + "<font color='blue'>文</font>" + "でありますですですですですですですですですですでですですですです！"
        example =u'軈て幽霊は濃い霧の中に消えた。'
        self.sentence.setText(example)#self.srs.getExample(self.srs.getCurrentItem()))
        
        readings = self.srs.getQuizVariants(self.srs.getCurrentItem())
        
        if len(readings) == 4:
            self.var_1st.setText(readings[0])
            self.var_2nd.setText(readings[1])
            self.var_3rd.setText(readings[2])
            self.var_4th.setText(readings[3])
        
    def setButtonsActions(self):

        if self.var_1st.text() == self.srs.getCorrectAnswer(self.srs.getCurrentItem()):
                self.var_1st.clicked.connect(self.correctAnswer)
        else:
                self.var_1st.clicked.connect(self.wrongAnswer)
               
        if self.var_2nd.text() == self.srs.getCorrectAnswer(self.srs.getCurrentItem()):
                self.var_2nd.clicked.connect(self.correctAnswer)
        else:
                self.var_2nd.clicked.connect(self.wrongAnswer)
                
        if self.var_3rd.text() == self.srs.getCorrectAnswer(self.srs.getCurrentItem()):
                self.var_3rd.clicked.connect(self.correctAnswer)
        else:
                self.var_3rd.clicked.connect(self.wrongAnswer)
                
        if self.var_4th.text() == self.srs.getCorrectAnswer(self.srs.getCurrentItem()):
                self.var_4th.clicked.connect(self.correctAnswer)
        else:
                self.var_4th.clicked.connect(self.wrongAnswer)
                
    def resetButtonsActions(self):
        self.var_1st.disconnect()
        self.var_2nd.disconnect()
        self.var_3rd.disconnect()
        self.var_4th.disconnect()
        
    def hideButtonsQuiz(self):
        self.var_1st.hide()
        self.var_2nd.hide()
        self.var_3rd.hide()
        self.var_4th.hide()
        
        self.answered.clicked.connect(self.hideQuizAndWaitForNext)
        self.answered.show()
        
    def showButtonsQuiz(self):
        self.var_1st.show()
        self.var_2nd.show()
        self.var_3rd.show()
        self.var_4th.show()
        
        self.answered.hide()
        self.answered.disconnect()
        
    def stopCountdown(self):
        self.progressTimer.cancel()
        self.countdownTimer.stop()
        
    def correctAnswer(self):
        self.stopCountdown()
        print 'correct!'
        self.hideButtonsQuiz()
        self.answered.setText(u'Correct!')
        #self.hideQuizAndWaitForNext() # -> temporarily
        
    def wrongAnswer(self):
        self.stopCountdown()
        print 'wrong!'
        self.hideButtonsQuiz()
        self.answered.setText(u'Wrong! Correct answer is:' + self.srs.getCorrectAnswer(self.srs.getCurrentItem()))
        #self.hideQuizAndWaitForNext()
        
    def timeIsOut(self):
        print 'timeout'
        self.hideButtonsQuiz()
        self.answered.setText(u'Time is out! Correct answer is:' + self.srs.getCorrectAnswer(self.srs.getCurrentItem()))
            
    def hideQuizAndWaitForNext(self):
        # N.B.
        self.resetButtonsActions()
        
        self.setWindowOpacity(1)
        self.fade()
        QTimer.singleShot(1000,self.hide)
        self.waitUntilNextTimeslot()
    
    def setMenus(self):
        self.trayMenu.addAction(QAction('&Quiz me now!', self, shortcut="Q", triggered=self.showQuiz))
        self.pauseAction = QAction('&Pause', self, shortcut="P", triggered=self.pauseQuiz)
        self.trayMenu.addAction(self.pauseAction)
        self.trayMenu.addAction(QAction('&Options', self, shortcut="O", triggered=self.showOptions))
        self.trayMenu.addAction(QAction('&About', self, shortcut="A", triggered=self.showAbout))
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(QAction('&Exit', self, shortcut="E", triggered=self.saveAndExit))

        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.setToolTip('Quiz in progress!')
        #self.trayIcon.activated.connect(self.showQuiz) # left click breaks it all
 
    def pauseQuiz(self):
        #TODO: it would be good to hide sentence, if paused during the actual quiz!
        if self.isHidden():
            if self.pauseAction.text() == '&Pause':     # somehow, QTimer.isActive does not work properly
                self.nextQuizTimer.stop()
                self.pauseAction.setText('&Unpause')
                self.trayIcon.setToolTip('Quiz paused!')
            else:
                self.waitUntilNextTimeslot()
                self.pauseAction.setText('&Pause')
                self.trayIcon.setToolTip('Quiz in progress!')
        else:
            print 'Sorry, cannot pause while quiz in progress!'
 
    def showQuiz(self):
        if self.isHidden():
            self.updateContent()
            self.setButtonsActions()
            
            self.show()
            self.setWindowOpacity(0)
            self.fade()

            self.countdown.setValue(1000) #TODO: no magic constant!
            self.beginCountdown()
        else:
            print 'Already quizZzing!'
         
    def showOptions(self):
        print 'here be options!'
        
    def showAbout(self):
        print 'about, yeah'
 
    def saveAndExit(self):
        #TODO: check if it really works
        if self.countdownTimer.isActive():
                self.countdownTimer.stop()
        if self.nextQuizTimer.isActive():
                self.nextQuizTimer.stop()
        if self.progressTimer.isAlive():
                self.progressTimer.cancel()      
            
        self.trayIcon.hide()
        self.close() #TODO: with bells and whistles

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('plastique')
    
    quiz = Quiz()
    #quiz.show()

    sys.exit(app.exec_())
