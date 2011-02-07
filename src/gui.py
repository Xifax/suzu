# -*- coding: utf-8 -*-
'''
Created on Jan 31, 2011

@author: Yadavito
'''
 
import sys

from srs import srsScheduler
from rtimer import RepeatTimer

from PySide.QtCore import *
from PySide.QtGui import *

class Quiz(QFrame):
     
    def __init__(self, parent=None):
        super(Quiz, self).__init__(parent)

        # kanji info
        self.info = QFrame()

        self.countdown = QProgressBar()
        
        #self.sentence = QLabel(u"<font size=8>これはテストの" + "<b><font color='blue'>文</font></b>" + "であります</font>")
        self.sentence = QLabel(u"これはテストの" + "<font color='blue'>文</font>" + "でありますですですですですですですですですですでですですですです！")
        
        #font = QFont(u'メイリオ', 12) #さざなみ明朝      #メイリオ
        #font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 90)

        self.var_1st = QPushButton(u"ぶん")
        self.var_2nd = QPushButton(u"とら")
        self.var_3rd = QPushButton(u"あい")
        self.var_4th = QPushButton(u"よう")

        self.answered = QPushButton(u'')
        self.answered.hide()
        #self.answered.setFlat(True)

        self.layout_vertical = QVBoxLayout()
        self.layout_horizontal = QHBoxLayout()
        
        self.layout_horizontal.addWidget(self.var_1st)
        self.layout_horizontal.addWidget(self.var_2nd)
        self.layout_horizontal.addWidget(self.var_3rd)
        self.layout_horizontal.addWidget(self.var_4th)

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
        self.countdownTimer = QTimer()
        self.animationTimer = ()
                
        #config here
        self.initializeComposition()
        self.initializeComponents()
        self.setMenus()
        
        self.trayIcon.show()
        
        #!!!
        self.srs = srsScheduler()
        
        #begin work!
        #self.waitUntilNextTimeslot()
        self.showQuiz()
        #self.hideButtonsQuiz()
        
        
        #self.trayIcon.showMessage('Test message!')
        
        #self.info.show() --> to do cool stuff
    
    def waitUntilNextTimeslot(self):
        self.nextQuizTimer.singleShot(2000, self.showQuiz)
        
    #def beginCountdown(self):
        #self.countdownTimer.singleShot(1000, self.showQuiz)

    def initializeComposition(self):
        #may or may not want to control dialog size according to text size
        D_WIDTH = 400
        D_HEIGHT = 136

        #down right corner position
        H_INDENT = D_WIDTH + 10 #indent from right
        V_INDENT = D_HEIGHT + 40 #indent from bottom
        
        self.setWindowFlags(Qt.FramelessWindowHint) #and Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setFont(QFont(u'さざなみ明朝 ', 12))
        #self.setWindowOpacity(0.88)
        desktop = QApplication.desktop().screenGeometry()
        self.setGeometry(QRect(desktop.width() - H_INDENT, desktop.height() - V_INDENT, D_WIDTH, D_HEIGHT))
        
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
        self.sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sentence.setFont(QFont(u'メイリオ', 12))
        self.sentence.font().setStyleStrategy(QFont.PreferAntialias)
        self.sentence.setWordWrap(True)
        self.trayIcon.setIcon(QIcon('../resources/noren.ico'))
        
    def updateContent(self):
        self.showButtonsQuiz()
        
        self.srs.getExample(self.srs.getNextItem())
        self.sentence.setText(self.srs.getExample(self.srs.getCurrentItem()))
        
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
        
    def correctAnswer(self):
        print 'correct!'
        self.hideButtonsQuiz()
        self.answered.setText(u'Correct!')
        #self.hideQuizAndWaitForNext() # -> temporarily
        
    def wrongAnswer(self):
        print 'wrong!'
        self.hideButtonsQuiz()
        self.answered.setText(u'Wrong! Correct answer is:' + self.srs.getCorrectAnswer(self.srs.getCurrentItem()))
        #self.hideQuizAndWaitForNext()
            
    def hideQuizAndWaitForNext(self):
        # N.B.
        self.resetButtonsActions()
        
        self.setWindowOpacity(1)
        self.fade()
        QTimer.singleShot(1000,self.hide)
        self.waitUntilNextTimeslot()

    
    def setMenus(self):
        self.trayMenu.addAction(QAction('&Quiz me now!', self, shortcut="Q", triggered=self.showQuiz))
        self.trayMenu.addAction(QAction('&Options', self, shortcut="O", triggered=self.showOptions))
        self.trayMenu.addAction(QAction('&About', self, shortcut="A", triggered=self.showAbout))
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(QAction('&Exit', self, shortcut="E", triggered=self.saveAndExit))

        self.trayIcon.setContextMenu(self.trayMenu)
        #self.trayIcon.activated.connect(self.showForm())
        self.trayIcon.setToolTip('Test!')
 
    #def showForm(self):
        #self.show()
 
    def showQuiz(self):
        self.updateContent()
        self.setButtonsActions()
        
        self.show()
        self.setWindowOpacity(0)
        self.fade()
         
    def showOptions(self):
        print 'here be options!'
        
    def showAbout(self):
        print 'about, yeah'
 
    def saveAndExit(self):
        self.trayIcon.hide()
        self.close() #to do with bells and whistles

if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('plastique')
    
    quiz = Quiz()
    #quiz.show()

    sys.exit(app.exec_())
