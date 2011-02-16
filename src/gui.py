# -*- coding: utf-8 -*-
'''
Created on Jan 31, 2011

@author: Yadavito
'''
 
import sys

from srs import srsScheduler
from rtimer import RepeatTimer
from fonts import Fonts
from options import Options

from PySide.QtCore import QTimer,Qt,QRect,QObject,QEvent 
from PySide.QtGui import *  #TODO: fix to parsimonious imports

class Filter(QObject):
    def eventFilter(self, object, event):

        if event.type() == QEvent.HoverLeave:
            object.setStyleSheet("QLabel { color: rgb(0, 0, 0); }")

        if event.type() == QEvent.HoverEnter:
            object.setStyleSheet("QLabel { color: rgb(0, 5, 255); }")
            print object.text()
            
        return False

class Quiz(QFrame):
     
    def __init__(self, parent=None):
        super(Quiz, self).__init__(parent)

        # kanji info
        self.info = QFrame()
        
        self.filter = Filter()

        self.countdown = QProgressBar()
        #NB: will be changed to a lot of labels!
        self.sentence = QLabel(u'')
        
        self.var_1st = QPushButton(u'')
        self.var_2nd = QPushButton(u'')
        self.var_3rd = QPushButton(u'')
        self.var_4th = QPushButton(u'')

        self.answered = QPushButton(u'')
        self.answered.hide()

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
                       
        #initialize options
        self.options = Options()
        
        #config here
        self.initializeComposition()
        self.initializeComponents()
        self.setMenus()
        self.trayIcon.show()
        
        #initializing srs system
        self.srs = srsScheduler()
        self.srs.initializeCurrentSession(self.options.getQuizMode(), self.options.getSessionSize())
        
        #begin!
        if self.options.isQuizStartingAtLaunch():
            self.waitUntilNextTimeslot()
            self.trayIcon.setToolTip('Quiz has started automatically!')
        else:
            self.trayIcon.setToolTip('Quiz is not initiated!')
    
    def waitUntilNextTimeslot(self):
        #self.nextQuizTimer.start(10000) #10 seconds for testing purposes
        self.nextQuizTimer.start(self.options.getRepetitionInterval() * 60 * 1000)  #options are in minutes
        
    def beginCountdown(self):
        self.countdownTimer.start(10000)

        self.progressTimer = RepeatTimer(0.01, self.updateCountdownBar, 1000)
        self.progressTimer.start()
        
    def updateCountdownBar(self):
        self.countdown.setValue(self.countdown.value() - 1)
        print self.countdown.value()
        self.countdown.update()         #without update recursive repaint crushes qt

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
        #self.setFont(QFont(Fonts.SazanamiMyoutyou, 12))
        self.setFont(QFont(Fonts.SyoutyouProEl, 16))

        #self.setWindowOpacity(0.88)
        desktop = QApplication.desktop().screenGeometry()
        self.setGeometry(QRect(desktop.width() - H_INDENT, desktop.height() - V_INDENT, D_WIDTH, D_HEIGHT))
        
        self.setStyleSheet("QWidget { background-color: rgb(255, 255,255); }")
                
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
        self.countdown.setStyleSheet("QProgressbar { background-color: rgb(255, 255, 255); }")
        
        self.sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #TODO: it's actually nice to change fonts every iteration
        self.sentence.setFont(QFont(Fonts.HiragiNoMarugotoProW4, 18))
        #self.sentence.setFont(QFont(self.options.getSentenceFont(), self.options.getSentenceFontSize()))            #NB: does not work as it should!
        
        #self.var_1st.setStyleSheet("QWidget { border: 1px solid red;}")

        #self.sentence.setStyleSheet("QWidget {border:1px solid rgb(255, 170, 255); }")
        #self.sentence.setFont(QFont(u'小塚明朝 Pro EL', 12))
        #self.sentence.setFont(QFont(u'メイリオ', 12))
        #self.sentence.font().setStyleStrategy(QFont.PreferQuality)
        
        self.sentence.setWordWrap(True)
        self.trayIcon.setIcon(QIcon('../res/cards.ico'))
        
    def updateContent(self):
        self.showButtonsQuiz()
        
        currentQuiz = self.srs.getNextItem()
              
        example = self.srs.getCurrentExample().replace(currentQuiz, u"<font color='blue'>" + currentQuiz + u"</font>")
        self.sentence.setText(example)
        
        '''
        readings = self.srs.getQuizVariants(self.srs.getCurrentItem())
        
        if len(readings) == 4:
            self.var_1st.setText(readings[0])
            self.var_2nd.setText(readings[1])
            self.var_3rd.setText(readings[2])
            self.var_4th.setText(readings[3])
        '''
        
    def getReadyPostLayout(self):
        #NB: DANGEROUS stuff ahead!
        #self.layout_vertical.removeWidget()
        self.sentence.hide()        #to show later -> .show()!
        self.update()
        
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.labels = []
        
        #row, column, rows span, columns span, max columns
        i = 0; j = 0; r = 1; c = 1; n = 16
        for word in self.srs.parseCurrentExample():
            label = QLabel(word)
            #label.setFont(QFont(self.options.getSentenceFont(), self.options.getSentenceFontSize()))
            label.setFont(QFont(Fonts.HiragiNoMarugotoProW4, self.options.getSentenceFontSize()))
            
            label.setAttribute(Qt.WA_Hover, True)
            label.installEventFilter(self.filter)
            self.labels.append(label)
            
            if len(label.text()) > 1: c = len(label.text())
            else: c = 1
            
            if j + c > n: i = i + 1; j = 0
            
            self.grid_layout.addWidget(self.labels.pop(), i, j, r, c)
            
            if j <= n: j = j + c
            else: j = 0; i = i + 1
        
        #self.grid_layout.setSizeConstraint(self.grid_layout.SetFixedSize)
        self.grid_layout.setAlignment(Qt.AlignCenter)           #EURECA!!!
        self.layout_vertical.insertLayout(1, self.grid_layout)
        #self.layout_vertical.setStretchFactor(self.grid_layout, 10)

        #self.setLayout(self.grid_layout)
        self.update()
        
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
        
        self.getReadyPostLayout()
        #self.answered.setText(u'Wrong! Correct answer is:' + self.srs.getCorrectAnswer(self.srs.getCurrentItem()))
        #self.hideQuizAndWaitForNext()
        
    def timeIsOut(self):
        print 'timeout'
        QTimer.singleShot(50,self.hideButtonsQuiz)     #to prevent recursive repaint when mouse is suddenly over appearing button
        #self.hideButtonsQuiz()
        self.answered.setText(u'Time is out! Correct answer is:' + self.srs.getCorrectAnswer(self.srs.getCurrentItem()))
            
    def hideQuizAndWaitForNext(self):
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
        #TODO: check if it really works as it should
        if self.countdownTimer.isActive():
                self.countdownTimer.stop()
        if self.nextQuizTimer.isActive():
                self.nextQuizTimer.stop()
        if self.progressTimer != () and self.progressTimer.isAlive():
                self.progressTimer.cancel()      
            
        self.srs.endCurrentSession()
        
        self.trayIcon.hide()
        self.close()
            
class Sentence(QWidget):
    def __init__(self, parent=Quiz):
        super(Sentence, self).__init__(parent)
    #standalone widget for sentence
    
class Info(QWidget):
    def __init__(self, parent=Quiz):
        super(Sentence, self).__init__(parent)
    #standalone wiget for items info

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('plastique')
    
    quiz = Quiz()

    sys.exit(app.exec_())
