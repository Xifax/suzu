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

#TODO: fix forced builtins in Aptana settings
from cjktools.resources.radkdict import RadkDict
from pkg_resources import resource_filename
from cjktools.resources import auto_format
from cjktools.resources import kanjidic
from cjktools import scripts

class Filter(QObject):
    """Sentence components mouse hover filter"""
    def eventFilter(self, object, event):

        if event.type() == QEvent.HoverLeave:
            object.setStyleSheet("QLabel { color: rgb(0, 0, 0); }")
            quiz.info.hide()

        #NB: it may be nice to block info by left click OR
        #NB: show translation only when item left clicked!
        
        if event.type() == QEvent.HoverEnter:
            object.setStyleSheet("QLabel { color: rgb(0, 5, 255); }")
            quiz.info.item.setText(object.text())
            
            '''
            #NB: IS IT ALL EVEN NECESSARY? May as well get this from mecab parse results
            #setting reading        #words to edict, kanji to kanjidict
            search = []
            if len(object.text()) == 1:
                #NB: to kanjidict
                try:
                    search = quiz.kjd[object.text()]
                    quiz.info.reading.setText(' '.join(search.readings.sences_by_reading().keys()))
                except:
                    quiz.info.reading.setText('not found')
                
            else:
                #NB: to edict
                try: 
                    search = quiz.edict[object.text()]
                    #if len(search.sences_by_reading.keys()) > 2  :   search = search[:2]
                    quiz.info.reading.setText(' '.join(search.readings.sences_by_reading().keys()))
                except:
                    quiz.info.reading.setText('not found')
            '''
            
            reading = quiz.srs.getWordPronunciationFromExample(object.text())
            if reading != object.text() :  quiz.info.reading.setText(reading)
            else:   quiz.info.reading.setText(u'')
            
            #parsing word
            script = scripts.script_boundaries(object.text())
            components = []
            for cluster in script:
                if scripts.script_type(cluster) == scripts.Script.Kanji:
                    for kanji in cluster:
                        components = components + list(quiz.rdk[kanji])
                
            #setting radikals
            quiz.info.components.setText(' '.join(components))
            
            #looking up translation    #TODO: show translation only when left/right button is pressed (otherwise, show just main translation)
            '''
            try:
                search = quiz.edict[object.text()]
                #quiz.info.translation.setText(' '.join(search.senses))        #NB: TOO MUCH!
                quiz.info.translation.setText(search.senses_by_reading()[quiz.srs.getWordPronunciationFromExample(object.text())][0])
            except:
                quiz.info.translation.setText('')
            '''
            
            quiz.info.show()

            if event.type() == QEvent.MouseButtonPress:
                quiz.info.hide()
                #print 'lalala'      #TODO: show big box with readings
                #u'空'.encode('utf-8').encode('hex')
                #[f for f in fileList if f.find(u'空'.encode('utf-8').encode('hex') + '.gif') > -1]
                
                #path = '../res/kanji/' + kanji.encode('utf-8').encode('hex') + '.gif'
            print event.type()
            
        return False

class StatusFilter(QObject):
    """Status message mouse click filter"""
    def eventFilter(self, object, event):
        
        if event.type() == QEvent.HoverEnter:
            quiz.status.setWindowOpacity(0.70)
            
        if event.type() == QEvent.HoverLeave:
            quiz.status.setWindowOpacity(1)
            
        if event.type() == QEvent.MouseButtonPress:
            quiz.status.hide()
            
        return False

class Quiz(QFrame):
     
    def __init__(self, parent=None):
        super(Quiz, self).__init__(parent)

        """Session Info"""
        self.status = QFrame()
        ##session message
        self.status.message = QLabel(u'')
        self.status.layout = QHBoxLayout()
        self.status.layout.addWidget(self.status.message)
        self.status.setLayout(self.status.layout)
        ##mouse event filter
        self.status.filter = StatusFilter()
        self.status.setAttribute(Qt.WA_Hover, True)
        self.status.installEventFilter(self.status.filter)

        """Items Info"""
        self.info = QFrame()
        ##item reading
        self.info.reading = QLabel(u'')
        ##large item
        self.info.item = QLabel(u'')
        ##radikals or/and kanji components
        self.info.components = QLabel(u'')
        ##translation
        self.info.translation = QLabel(u'')
        #self.info.reading = QLabel(u'')
        self.info.layout = QVBoxLayout()
        self.info.layout.addWidget(self.info.reading)
        self.info.layout.addWidget(self.info.item)
        self.info.layout.addWidget(self.info.components)
        self.info.layout.addWidget(self.info.translation)
        self.info.setLayout(self.info.layout)
        
        """Verbose Info"""
        self.allInfo = QFrame()
        #self.allInfo.
        
        """Global Flags"""
        #self.correct = False
        
        """Quiz Dialog"""
        self.filter = Filter()
        ####    visual components    ###
        self.countdown = QProgressBar()
        self.sentence = QLabel(u'')
        
        self.var_1st = QPushButton(u'')
        self.var_2nd = QPushButton(u'')
        self.var_3rd = QPushButton(u'')
        self.var_4th = QPushButton(u'')

        self.answered = QPushButton(u'')
        self.answered.hide()
        
        ###    layouts    ####
        self.layout_vertical = QVBoxLayout()        #main
        self.layout_horizontal = QHBoxLayout()      #buttons
        
        self.layout_horizontal.addWidget(self.var_1st)
        self.layout_horizontal.addWidget(self.var_2nd)
        self.layout_horizontal.addWidget(self.var_3rd)
        self.layout_horizontal.addWidget(self.var_4th)
        
        self.layout_vertical.addWidget(self.countdown)
        self.layout_vertical.addWidget(self.sentence)
        self.layout_vertical.addLayout(self.layout_horizontal)
        
        self.layout_horizontal.addWidget(self.answered)

        self.setLayout(self.layout_vertical)

        ###    utility components    ###
        self.trayIcon = QSystemTrayIcon(self)
        self.trayMenu = QMenu()
        
        self.nextQuizTimer = QTimer()
        self.nextQuizTimer.setSingleShot(True)
        self.nextQuizTimer.timeout.connect(self.showQuiz)
        
        self.countdownTimer = QTimer()
        self.countdownTimer.setSingleShot(True)
        self.countdownTimer.timeout.connect(self.timeIsOut)
        
        """Pre-initialization"""
        self.animationTimer = ()
        self.progressTimer = ()
        self.grid_layout =()
                       
        """Initialize Options"""
        self.options = Options()
        
        """"Initialize Dictionaries    (will take a lot of time!)"""
        self.rdk = RadkDict()
        edict_file = resource_filename('cjktools_data', 'dict/je_edict')
        self.edict = auto_format.load_dictionary(edict_file)
        #self.kjd = kanjidic.Kanjidic()
        
        """Config Here"""
        self.initializeComposition()
        self.initializeComponents()
        self.setMenus()
        self.trayIcon.show()
        
        """initializing srs system"""
        self.srs = srsScheduler()
        self.srs.initializeCurrentSession(self.options.getQuizMode(), self.options.getSessionSize())
        
        """Start!"""
        if self.options.isQuizStartingAtLaunch():
            self.waitUntilNextTimeslot()
            self.trayIcon.setToolTip('Quiz has started automatically!')
        else:
            self.trayIcon.setToolTip('Quiz is not initiated!')
            
        """Test calls here:"""

####################################
#    Composition and appearance    #
####################################

    def initializeComposition(self):
        #TODO: may or may not want to control dialog size according to text size
        D_WIDTH = 550
        D_HEIGHT = 176#136
        
        #I_WIDTH = D_HEIGHT
        I_WIDTH = 200
        I_HEIGHT = D_HEIGHT
        I_INDENT = 2
        
        S_WIDTH = D_WIDTH
        S_HEIGHT = 30
        S_INDENT = I_INDENT
        S_CORRECTION = 0

        #down right corner position
        H_INDENT = D_WIDTH + 10 #indent from right
        V_INDENT = D_HEIGHT + 40 #indent from bottom
        
        """Main Dialog"""
        self.setWindowFlags(Qt.FramelessWindowHint) #and Qt.WindowStaysOnTopHint)    NB:changes widget to window
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        #Font will appear in buttons
        self.setFont(QFont(Fonts.HiragiNoMyoutyouProW3, self.options.getQuizFontSize()))

        desktop = QApplication.desktop().screenGeometry()
        self.setGeometry(QRect(desktop.width() - H_INDENT, desktop.height() - V_INDENT, D_WIDTH, D_HEIGHT))
        
        self.setStyleSheet("QWidget { background-color: rgb(255, 255,255); }")
        
        """Info dialog"""
        self.info.setWindowFlags(Qt.FramelessWindowHint)
        self.info.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.info.setGeometry(QRect(desktop.width() - H_INDENT - I_WIDTH - I_INDENT, desktop.height() - V_INDENT, I_WIDTH, I_HEIGHT))
        #self.info.setWindowOpacity(0.80)
        
        self.info.setStyleSheet("QWidget { background-color: rgb(255, 255,255); }")
        
        """Session message"""
        self.status.setWindowFlags(Qt.FramelessWindowHint)
        self.status.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.status.setGeometry(QRect(desktop.width() - H_INDENT, desktop.height() - V_INDENT - S_HEIGHT - S_INDENT - S_CORRECTION, S_WIDTH, S_HEIGHT))
        
        self.status.setStyleSheet("QWidget { background-color: rgb(255, 255,255); }")

    def initializeComponents(self):
        self.countdown.setMaximumHeight(6)
        self.countdown.setRange(0, self.options.getCountdownInterval() * 100)
        self.countdown.setTextVisible(False)
        self.countdown.setStyleSheet("QProgressbar { background-color: rgb(255, 255, 255); }")
        
        #self.setFont(QFont(Fonts.SyoutyouProEl, 40))#self.options.getQuizFontSize()))
        
        self.sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sentence.setFont(QFont(Fonts.HiragiNoMarugotoProW4, self.options.getSentenceFontSize()))
        #self.sentence.setFont(QFont(self.options.getSentenceFont(), self.options.getSentenceFontSize()))            #NB: does not work as it should!
        
        self.sentence.setWordWrap(True)
        self.trayIcon.setIcon(QIcon('../res/cards.ico'))
        
        self.status.message.setFont(QFont(Fonts.MSMyoutyou, self.options.getMessageFontSize()))
        self.status.layout.setAlignment(Qt.AlignCenter)
        self.status.message.setWordWrap(False)
        self.status.layout.setMargin(0)
        
        self.info.item.setFont(QFont(Fonts.HiragiNoMyoutyouProW3, 36))
        self.info.reading.setFont(QFont(Fonts.HiragiNoMyoutyouProW3, 16))
        self.info.components.setFont((QFont(Fonts.HiragiNoMyoutyouProW3, 14)))
        self.info.item.setWordWrap(True)
        self.info.components.setWordWrap(True)
        self.info.layout.setAlignment(Qt.AlignCenter)
        #self.info.layout.setSizeConstraint(self.info.layout.SetFixedSize)       #NB: would work nice, if the anchor point was in right corner
        
        self.info.reading.setAlignment(Qt.AlignCenter)
        self.info.item.setAlignment(Qt.AlignCenter)
        self.info.components.setAlignment(Qt.AlignCenter)
        
        self.info.reading.setStyleSheet("QLabel { color: rgb(155, 155, 155); }")
        self.info.components.setStyleSheet("QLabel { color: rgb(125, 125, 125); }")

####################################
#        Updating content          #
####################################        

    def updateContent(self):
        
        """Resetting multi-label sentence"""
        if self.grid_layout != ():
            for i in range(0, self.grid_layout.count()):
                    self.grid_layout.itemAt(i).widget().hide()
            self.layout_vertical.removeItem(self.grid_layout)
            self.grid_layout.setParent(None)
            self.update()
        if self.sentence.isHidden():    
            self.sentence.show()
        self.showButtonsQuiz()
        
        """Getting actual content"""
        self.srs.getNextItem()
              
        example = self.srs.getCurrentExample().replace(self.srs.getWordFromExample(), u"<font color='blue'>" + self.srs.getWordFromExample() + u"</font>")
        self.sentence.setText(example)
        
        readings = self.srs.getQuizVariants()
        
        if len(readings) == 4:
            self.var_1st.setText(readings[0])
            self.var_2nd.setText(readings[1])
            self.var_3rd.setText(readings[2])
            self.var_4th.setText(readings[3])
        
    def getReadyPostLayout(self):
        #NB: DANGEROUS stuff ahead!
        self.sentence.hide()
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
            #Don't ask, really
            if j + c > n: i = i + 1; j = 0
            
            self.grid_layout.addWidget(self.labels.pop(), i, j, r, c)
            
            if j <= n: j = j + c
            else: j = 0; i = i + 1
        
        self.grid_layout.setAlignment(Qt.AlignCenter)
        self.layout_vertical.insertLayout(1, self.grid_layout)

        self.update()
        
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
        
####################################
#        Timers and animations     #
####################################

    def waitUntilNextTimeslot(self):
        #if self.nextQuizTimer.isActive():   self.nextQuizTimer.stop()
        self.nextQuizTimer.start(self.options.getRepetitionInterval() * 60 * 1000)  #options are in minutes    NB: how do neatly I convert minutes to ms?
        
    def beginCountdown(self):
        self.trayIcon.setToolTip('Quiz in progress!')
        self.countdownTimer.start(self.options.getCountdownInterval() * 1000)

        self.progressTimer = RepeatTimer(0.01, self.updateCountdownBar, self.options.getCountdownInterval() * 100)
        self.progressTimer.start()
        
    def updateCountdownBar(self):
        self.countdown.setValue(self.countdown.value() - 1)
        #print self.countdown.value()
        self.countdown.update()         #NB: without .update() recursive repaint crushes qt

    def fade(self):
        if self.windowOpacity() == 1:
            self.animationTimer = RepeatTimer(0.025, self.fadeOut, 40)
            self.animationTimer.start()
        else:
            self.animationTimer = RepeatTimer(0.025, self.fadeIn, 40)
            self.animationTimer.start()
    
    def fadeIn(self):
        self.setWindowOpacity(self.windowOpacity() + 0.1)
        
    def fadeOut(self):
        self.setWindowOpacity(self.windowOpacity() - 0.1)
        
    def stopCountdown(self):
        self.progressTimer.cancel()
        self.countdownTimer.stop()
        self.countdown.setValue(0)
        
    def timeIsOut(self):
        QTimer.singleShot(50, self.hideButtonsQuiz)     #NB: slight artificial lag to prevent recursive repaint crush, when mouse is suddenly over appearing button
        self.getReadyPostLayout()
        self.srs.answeredWrong()

        #self.showSessionMessage(u'Time is out! Correct answer is:' + self.srs.getCorrectAnswer())
        self.showSessionMessage(u'Timeout! Should be: ' + self.srs.getCorrectAnswer() + ' - Next quiz: ' + self.srs.getNextQuizTime())
        self.answered.setFont(QFont('Calibri', 11))
        self.answered.setText(self.srs.getCurrentSentenceTranslation())
        
####################################
#        Actions and events        #
####################################    
    
    def setMenus(self):
        self.trayMenu.addAction(QAction('&Quiz me now!', self, shortcut="Q", triggered=self.showQuiz))
        self.pauseAction = QAction('&Pause', self, shortcut="P", triggered=self.pauseQuiz)
        self.trayMenu.addAction(self.pauseAction)
        self.trayMenu.addAction(QAction('&Options', self, shortcut="O", triggered=self.showOptions))
        self.trayMenu.addAction(QAction('&About', self, shortcut="A", triggered=self.showAbout))
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(QAction('&Exit', self, shortcut="E", triggered=self.saveAndExit))

        self.trayIcon.setContextMenu(self.trayMenu)
        #self.trayIcon.activated.connect(self.showQuiz) #NB: left click breaks it all
    
    def setButtonsActions(self):

        if self.var_1st.text() == self.srs.getCorrectAnswer():
                self.var_1st.clicked.connect(self.correctAnswer)
        else:
                self.var_1st.clicked.connect(self.wrongAnswer)
               
        if self.var_2nd.text() == self.srs.getCorrectAnswer():
                self.var_2nd.clicked.connect(self.correctAnswer)
        else:
                self.var_2nd.clicked.connect(self.wrongAnswer)
                
        if self.var_3rd.text() == self.srs.getCorrectAnswer():
                self.var_3rd.clicked.connect(self.correctAnswer)
        else:
                self.var_3rd.clicked.connect(self.wrongAnswer)
                
        if self.var_4th.text() == self.srs.getCorrectAnswer():
                self.var_4th.clicked.connect(self.correctAnswer)
        else:
                self.var_4th.clicked.connect(self.wrongAnswer)
                
    def resetButtonsActions(self):
        self.var_1st.disconnect()
        self.var_2nd.disconnect()
        self.var_3rd.disconnect()
        self.var_4th.disconnect()
        
    def correctAnswer(self):
        self.stopCountdown()
        self.hideButtonsQuiz()
        
        self.getReadyPostLayout()
        
        self.srs.answeredCorrect()
        #self.answered.setText(u"<font='Cambria'>" + self.srs.getCurrentSentenceTranslation() + "</font>")
        self.answered.setText(self.srs.getCurrentSentenceTranslation())
        self.answered.setFont(QFont('Calibri', 11))
        self.showSessionMessage(u'Correct: ' + self.srs.getCorrectAnswer() + ' - Next quiz: ' + self.srs.getNextQuizTime())
        
    def wrongAnswer(self):
        self.stopCountdown()
        self.hideButtonsQuiz()
        
        self.getReadyPostLayout()
        
        self.srs.answeredWrong()
        self.answered.setText(self.srs.getCurrentSentenceTranslation())
        self.answered.setFont(QFont('Calibri', 11))
        self.showSessionMessage(u'Wrong! Should be: ' + self.srs.getCorrectAnswer() + ' - Next quiz: ' + self.srs.getNextQuizTime())
            
    def hideQuizAndWaitForNext(self):
        
        self.status.hide()
        self.resetButtonsActions()
        
        self.setWindowOpacity(1)
        self.fade()
        QTimer.singleShot(1000, self.hide)
        self.waitUntilNextTimeslot()
 
    def pauseQuiz(self):
        #TODO: it would be good to hide sentence, if paused during the actual quiz!
        if self.isHidden():
            if self.pauseAction.text() == '&Pause':     #NB: somehow, QTimer.isActive does not work properly
                self.nextQuizTimer.stop()
                self.pauseAction.setText('&Unpause')
                self.trayIcon.setToolTip('Quiz paused!')
            else:
                self.waitUntilNextTimeslot()
                self.pauseAction.setText('&Pause')
                self.trayIcon.setToolTip('Quiz in progress!')
        else:
            self.showSessionMessage(u'Sorry, cannot pause while quiz in progress!')
 
    def showQuiz(self):
        if self.isHidden():
            self.updateContent()
            self.setButtonsActions()
            
            self.show()
            self.setWindowOpacity(0)
            self.fade()

            self.countdown.setValue(self.options.getCountdownInterval() * 100)
            self.beginCountdown()
            
            if self.nextQuizTimer.isActive():   self.nextQuizTimer.stop()
        else:
            self.showSessionMessage(u'Quiz is already underway!')
         
    def showOptions(self):
        print 'here be options!'
        
    def showAbout(self):
        print 'about, yeah'
        
    def showSessionMessage(self, message):
        """Shows info message"""
        self.status.message.setText(message)
        self.status.show()
        self.setFocus() #NB: does not work
 
    def saveAndExit(self):
        #TODO: check if it really works as it should
        if self.countdownTimer.isActive():
                self.countdownTimer.stop()
        if self.nextQuizTimer.isActive():
                self.nextQuizTimer.stop()
        if self.progressTimer != () and self.progressTimer.isAlive():
                self.progressTimer.cancel()      
            
        self.srs.endCurrentSession()
        
        self.status.hide()
        self.trayIcon.hide()
        self.close()
            
if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setStyle('plastique')
    
    quiz = Quiz()

    sys.exit(app.exec_())
