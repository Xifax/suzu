# -*- coding: utf-8 -*-
'''
Created on Jan 31, 2011

@author: Yadavito
@version: 0.0.1
@requires: Python 2.6.6
@requires: PySide 1.0.0
'''

# -> this is main application module <- #
#===============================================================================
# --- suzu ---
# -> main project file <-
# -> contains: 
#   - central GUI dialog
#   - TODO list
#   - dependencies & packages
#   - notes and iformation
# -> structure:
#
# -> launch:
#   - python suzu.py
#===============================================================================

##################################
### here goes global TODO list ###
##################################

# urgent
# LATER: change button font size depending on number of characters (< 5)
# TODO: add additional info dialog, briefly describing each kanji in compound

# concept
# TODO: implement 'similar kanji' system, based on comparing number of similar rads in RadDict

# functionality
# ...

# utilitarian
# TODO: errors logging

##################################
###     Aptana built-ins:      ###
##################################
# PySide
# elixir
# jcconv
# enum
# pkg_resources

import sys

from optionsBackend import Options
from srsManager import srsScheduler
from rtimer import RepeatTimer
from fonts import Fonts
from stats import Stats
from constants import *
from about import About
from guiOpt import OptionsDialog
from guiQuick import QuickDictionary
from db import *
from guiUtil import roundCorners, unfillLayout
from utils import BackgroundDownloader, GlobalHotkeyManager

from PySide.QtCore import QTimer,Qt,QRect,QObject,QEvent,QByteArray
from PySide.QtGui import *  #TODO: fix to parsimonious imports

from cjktools.resources.radkdict import RadkDict
from pkg_resources import resource_filename
from cjktools.resources import auto_format
from cjktools.resources import kanjidic
from cjktools import scripts

##########################################
# Event filters/handlers and key hookers #
##########################################

class Filter(QObject):
    """Sentence components mouse hover filter"""
    def eventFilter(self, object, event):

        if event.type() == QEvent.HoverLeave:
            object.setStyleSheet("QLabel { color: rgb(0, 0, 0); }")
            
            quiz.info.hide()
            quiz.allInfo.hide()

            desktop = QApplication.desktop().screenGeometry()
            quiz.info.setGeometry(QRect(desktop.width() - H_INDENT - I_WIDTH - I_INDENT, desktop.height() - V_INDENT, I_WIDTH, I_HEIGHT))
        
        if event.type() == QEvent.HoverEnter:
            object.setStyleSheet("QLabel { color: rgb(0, 5, 255); }")
            
            quiz.info.item.setText(object.text())
            
            reading = quiz.srs.getWordPronunciationFromExample(object.text())
            if reading != object.text() :  quiz.info.reading.setText(reading)
            else:   quiz.info.reading.setText(u'')
            
            #parsing word
            script = scripts.script_boundaries(object.text())
            components = []

            for cluster in script:
                if scripts.script_type(cluster) == scripts.Script.Kanji:
                    for kanji in cluster:
                        components = components + list(quiz.rdk[kanji]) + list('\n')
                        #kanji_list.append(kanji)
                
            #setting radikals
            if len(components) > 0: components.pop()    #remove last '\n'
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
            
            #quiz.info.setWindowOpacity(0)
            #fade(quiz.info)
            #QTimer.singleShot(100, quiz.info.show)      #for additional smoothness
            quiz.info.show()

        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.MiddleButton:
                print 'Middle'   #TODO: add distinction between actions     
            if event.button() == Qt.LeftButton:
                print 'Left'   #TODO: add distinction between actions
            if quiz.info.isVisible() and quiz.allInfo.isHidden():  
                quiz.info.hide()
                              
                #quiz.unfill(quiz.allInfo.layout)
                unfillLayout(quiz.allInfo.layout)
                quiz.allInfo.layout.setMargin(1)
                #quiz.allInfo.layout.setAlignment(Qt.AlignCenter)
                
                kanjiList = []
                script = scripts.script_boundaries(object.text())

                for cluster in script:
                    if scripts.script_type(cluster) == scripts.Script.Kanji:
                        for kanji in cluster:
                            kanjiList.append(kanji)
                
                i=0; j=0;
                # kanji strokes
                if len(kanjiList) > 0:
                    
                    infile = open('../res/kanji/KANJI-MANIFEST-UNICODE-HEX', 'r')
                    text = infile.read()
                    infile.close()
                    
                    for kanji in kanjiList:
                        
                        if( text.find(kanji.encode('utf-8').encode('hex')) != -1):
                        
                            gif = QLabel()
                            gif.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)        
                            gif.setAlignment(Qt.AlignCenter) 
    
                            movie = QMovie('../res/kanji/' + kanji.encode('utf-8').encode('hex') + '.gif', QByteArray(), self) 
                            movie.setCacheMode(QMovie.CacheAll) 
                            movie.setSpeed(150) 
                            
                            gif.setMovie(movie)
                            quiz.allInfo.layout.addWidget(gif, i, j);   j = j + 1
                            movie.start()
                              
                    i = i + 1
                
                # words translation
                translations = QLabel(u'')
                translations.setFont(QFont('Calibri', 11))
                translations.setWordWrap(True)
                translations.setAlignment(Qt.AlignCenter)
                try:
                    #search = quiz.edict[object.text()]
                    search = quiz.edict[quiz.srs.getWordNonInflectedForm(object.text())]

                    translationText = u''
                    '''
                    for sense in search.senses_by_reading():                #TODO: change to show only one sence
                        variants = search.senses_by_reading()[sense]
                        variants = filter (lambda e: e != '(P)', variants)
                        #TODO: add replace for ()
                        
                        translationText += '<b>' + sense + '</b>:\t' + ', '.join(variants) + '\n'

                    #NB: crop text to n symbols    
                    translations.setText(translationText.rstrip('\n'))
                    '''
                    
                    #variants = search.senses_by_reading()[quiz.srs.getWordPronunciationFromExample(object.text())]#[0]       #NB: add non-inflected form control
                    variants = search.senses_by_reading()[quiz.srs.getWordPronounciation(quiz.srs.getWordNonInflectedForm(object.text()))][:3]  #TODO: or add option, specifying, how many variants
                    variants = filter (lambda e: e != '(P)', variants)                                                                          #should be shown
                    
                    translationText += '<b>' + quiz.srs.getWordPronunciationFromExample(object.text()) + '</b>:\t' + ', '.join(variants)
                    translations.setText(translationText.rstrip('\n'))
                    
                    #print translations.text()
                except:
                    #quiz.jmdict.lookupItemTranslationJoin(quiz.srs.getWordNonInflectedForm(object.text()))
                    # at first - search just kana
                    # then - search word by reading
                    '''    
                    search = quiz.jmdict.lookupItemByReading(quiz.srs.getWordPronounciation(quiz.srs.getWordNonInflectedForm(object.text())))
                    if len(search) > 0:
                        lookup = quiz.jmdict.lookupItemTranslationJoin(search[0])
                        if len(lookup) > 5: lookup = lookup[:5]
                        translations.setText('<b>' + quiz.srs.getWordPronunciationFromExample(object.text())+ '</b>:\t' + ', '.join(lookup))
                    '''
                    ### by reading
                    search = quiz.jmdict.lookupTranslationByReadingJoin(quiz.srs.getWordPronounciation(quiz.srs.getWordNonInflectedForm(object.text())), quiz.options.getLookupLang())
                    if len(search) > 0:
                        if len(search) > 5: search = search[:5]
                        translations.setText('<b>' + quiz.srs.getWordPronunciationFromExample(object.text())+ '</b>:\t' + ', '.join(search))
                    ### by kanji
                    else:
                        search = quiz.jmdict.lookupItemByReading(quiz.srs.getWordPronounciation(quiz.srs.getWordNonInflectedForm(object.text())))
                        if len(search) > 0:
                            lookup = quiz.jmdict.lookupItemTranslationJoin(search[0], quiz.options.getLookupLang())
                            if len(lookup) > 5: lookup = lookup[:5]
                            translations.setText('<b>' + quiz.srs.getWordPronunciationFromExample(object.text())+ '</b>:\t' + ', '.join(lookup))
                    ### nothing found
                    if len(search) == 0: translations.setText(u'Alas, no translation in edict or jmdict!')
                
                if i > 0:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.HLine)
                    separator.setFrameShadow(QFrame.Sunken)
                    quiz.allInfo.layout.addWidget(separator, i, 0, 1, j);   i = i + 1
                
                quiz.allInfo.layout.addWidget(translations, i, 0, 1, j)    #NB: rows span should be changed, maybe
                
                quiz.allInfo.update()
                quiz.allInfo.show()
                
            elif quiz.allInfo.isVisible():  #quiz.info.isHidden():

                quiz.allInfo.hide()   
                quiz.info.show()
            
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

#######
# GUI #
#######

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
        self.info.reading = QLabel(u'')
        self.info.item = QLabel(u'')
        self.info.components = QLabel(u'')
        ##translation
        #self.info.translation = QLabel(u'')
        #self.info.animationTimer = ()

        separator_one = QFrame()
        separator_one.setFrameShape(QFrame.HLine)
        separator_one.setFrameShadow(QFrame.Sunken)
        
        separator_two = QFrame()
        separator_two.setFrameShape(QFrame.HLine)
        separator_two.setFrameShadow(QFrame.Sunken)
        
        self.info.layout = QVBoxLayout()
        self.info.layout.addWidget(self.info.reading)
        self.info.layout.addWidget(separator_one)
        self.info.layout.addWidget(self.info.item)
        self.info.layout.addWidget(separator_two)
        self.info.layout.addWidget(self.info.components)
        #self.info.layout.addWidget(self.info.translation)
        self.info.setLayout(self.info.layout)
        
        """Verbose Info"""
        self.allInfo = QFrame()
        self.allInfo.layout = QGridLayout()
        self.allInfo.setLayout(self.allInfo.layout)
        #the rest is (should be) generated on the fly
        
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
        
        self.gifLoading = QMovie('../res/cube.gif')
        self.gifLoading.frameChanged.connect(self.updateTrayIcon)
        
        self.nextQuizTimer = QTimer()
        self.nextQuizTimer.setSingleShot(True)
        self.nextQuizTimer.timeout.connect(self.showQuiz)
        
        self.countdownTimer = QTimer()
        self.countdownTimer.setSingleShot(True)
        self.countdownTimer.timeout.connect(self.timeIsOut)
        
        ### initializing ###
        self.initializeResources()
        
        
        """Start!"""
        if self.options.isQuizStartingAtLaunch():
            self.waitUntilNextTimeslot()
            self.trayIcon.setToolTip('Quiz has started automatically!')
            self.pauseAction.setText('&Pause')
            self.trayIcon.showMessage('Loading complete! (took ~'+ str(self.loadingTime.seconds) + ' seconds) Quiz underway.', 'Lo! Quiz already in progress!', QSystemTrayIcon.MessageIcon.Warning, 10000)
        else:
            self.trayIcon.setToolTip('Quiz is not initiated!')
            self.trayIcon.showMessage('Loading complete! (took ~' + str(self.loadingTime.seconds) + ' seconds) Standing by.', 'Quiz has not started yet! If you wish, you could start it manually or enable autostart by default.', 
                                      QSystemTrayIcon.MessageIcon.Information, 10000 )
            
        """Test calls here:"""
        ###    ...    ###
        #self.connect(self.hooker, SIGNAL('noQdict'), self.noQdict)

    def noQdict(self):
        self.showSessionMessage('Nope, cannot show quick dictionary during actual quiz.')

####################################
#    Initialization procedures     #
####################################

    def initializeResources(self):
        
        """Pre-initialization"""
        self.animationTimer = ()
        self.progressTimer = ()
        self.grid_layout =()
                       
        """Initialize Options"""
        self.options = Options()
        
        """Initialize Statistics"""
        self.stats = Stats()
        
        """Config Here"""
        self.initializeComposition()
        self.initializeComponents()
        self.setMenus()
        self.trayIcon.show()
        #self.startTrayLoading()
        
        """"Initialize Dictionaries    (will take a some time!)"""
        time_start = datetime.now()
        
        self.trayIcon.showMessage('Loading...', 'Initializing dictionaries', QSystemTrayIcon.MessageIcon.Information, 20000 )     #TODO: change into loading dialog... or not
        self.rdk = RadkDict()
        edict_file = resource_filename('cjktools_data', 'dict/je_edict')
        self.edict = auto_format.load_dictionary(edict_file)
        self.kjd = kanjidic.Kanjidic()
        
        """Initializing srs system"""
        self.trayIcon.showMessage('Loading...', 'Initializing databases', QSystemTrayIcon.MessageIcon.Information, 20000 )
        self.srs = srsScheduler()
        self.srs.initializeCurrentSession(self.options.getQuizMode(), self.options.getSessionSize())
        
        """Jmdict lookup"""
        self.jmdict = DictionaryLookup()
        
        """Global hotkeys hook"""
        #TODO: add multiple hotkeys and fix stop()
        #self.hooker = GlobalHotkeyManager(toggleQDictFlag, 'Q')
#        self.hooker = GlobalHotkeyManager(toggleWidgetFlag(self.qdict), 'Q')
#        self.hooker.setDaemon(True) #temporarily, should work using stop()
#        self.hooker.start()
        
        time_end = datetime.now()
        self.loadingTime =  time_end - time_start

####################################
#    Composition and appearance    #
####################################

    def initializeComposition(self):
        
        """Main Dialog"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        #Font will appear in buttons
        self.setFont(QFont(Fonts.TukusiMyoutyouProLB, self.options.getQuizFontSize()))

        desktop = QApplication.desktop().screenGeometry()
        self.setGeometry(QRect(desktop.width() - H_INDENT, desktop.height() - V_INDENT, D_WIDTH, D_HEIGHT))
        
        self.setStyleSheet("QWidget { background-color: rgb(255, 255, 255); }")
        
        """Info dialog"""
        self.info.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.info.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.info.setGeometry(QRect(desktop.width() - H_INDENT - I_WIDTH - I_INDENT, desktop.height() - V_INDENT, I_WIDTH, I_HEIGHT))
        
        self.info.setStyleSheet("QWidget { background-color: rgb(255, 255, 255); }")
        
        """Verbose info dialog"""
        self.allInfo.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.allInfo.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.allInfo.setGeometry(QRect(desktop.width() - H_INDENT - I_WIDTH - I_INDENT, desktop.height() - V_INDENT, I_WIDTH, I_HEIGHT))
        
        self.allInfo.setStyleSheet("QWidget { background-color: rgb(255, 255, 255); }")
        
        """Session message"""
        self.status.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.status.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.status.setGeometry(QRect(desktop.width() - H_INDENT, desktop.height() - V_INDENT - S_HEIGHT - S_INDENT - S_CORRECTION, S_WIDTH, S_HEIGHT))
        
        self.status.setStyleSheet("QWidget { background-color: rgb(255, 255, 255); }")
        
        self.setMask(roundCorners(self.rect(),5))
        self.status.setMask(roundCorners(self.status.rect(),5))
        #self.info.setMask(roundCorners(self.info.rect(),5))
        #self.allInfo.setMask(roundCorners(self.allInfo.rect(),5))

    def initializeComponents(self):
        self.countdown.setMaximumHeight(6)
        self.countdown.setRange(0, self.options.getCountdownInterval() * 100)
        self.countdown.setTextVisible(False)
        self.countdown.setStyleSheet("QProgressbar { background-color: rgb(255, 255, 255); }")
        
        #self.setFont(QFont(Fonts.SyoutyouProEl, 40))#self.options.getQuizFontSize()))
        
        self.sentence.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #self.sentence.setFont(QFont(Fonts.HiragiNoMarugotoProW4, self.options.getSentenceFontSize()))
        self.sentence.setFont(QFont(self.options.getSentenceFont(), self.options.getSentenceFontSize()))
        
        self.sentence.setWordWrap(True)
        self.trayIcon.setIcon(QIcon('../res/tray/active.png'))
        
        self.status.message.setFont(QFont('Cambria', self.options.getMessageFontSize()))
        self.status.layout.setAlignment(Qt.AlignCenter)
        self.status.message.setWordWrap(False)
        self.status.layout.setMargin(0)
        
        self.info.item.setFont(QFont(Fonts.HiragiNoMyoutyouProW3, 36))
        self.info.reading.setFont(QFont(Fonts.HiragiNoMyoutyouProW3, 16))
        self.info.components.setFont((QFont(Fonts.HiragiNoMyoutyouProW3, 14)))
        #self.info.item.setWordWrap(True)
        self.info.components.setWordWrap(True)
        #self.info.layout.setAlignment(Qt.AlignCenter)
        self.info.layout.setMargin(0)
        #self.info.layout.setSizeConstraint(self.info.layout.SetFixedSize)       #NB: would work nice, if the anchor point was in right corner
        
        self.info.reading.setAlignment(Qt.AlignCenter)
        self.info.item.setAlignment(Qt.AlignCenter)
        self.info.components.setAlignment(Qt.AlignCenter)
        
        #self.info.setLayoutDirection(Qt.RightToLeft)
        
        self.info.reading.setStyleSheet("QLabel { color: rgb(155, 155, 155); }")
        self.info.components.setStyleSheet("QLabel { color: rgb(100, 100, 100); }")


####################################
#        Updating content          #
####################################        
    '''
    def unfill(self, layoutName): 
        def deleteItems(layout): 
            if layout is not None: 
                while layout.count(): 
                    item = layout.takeAt(0) 
                    widget = item.widget() 
                    if widget is not None: 
                        widget.deleteLater() 
                    else: 
                        deleteItems(item.layout()) 
        deleteItems(layoutName) 
    '''
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
              
        start = datetime.now()  #testing
        example = self.srs.getCurrentExample().replace(self.srs.getWordFromExample(), u"<font color='blue'>" + self.srs.getWordFromExample() + u"</font>")
        print datetime.now() - start    #testing
        self.sentence.setText(example)
        
        start = datetime.now()  #testing
        readings = self.srs.getQuizVariants()
        print datetime.now() - start    #testing
        
        '''
        changeFont = False
        for item in readings:
            if len(item) > 5 : changeFont = True
            
        if changeFont: self.setStyleSheet('QWidget { font-size: 11pt; }')
        else:   self.setStyleSheet('QWidget { font-size: %spt; }' % self.options.getQuizFontSize())
        '''
        '''
        if len(readings) == 4:                  #NB: HERE LIES THE GREAT ERROR
            self.var_1st.setText(readings[0])
            self.var_2nd.setText(readings[1])
            self.var_3rd.setText(readings[2])
            self.var_4th.setText(readings[3])
        '''
        
        try:
            for i in range(0, self.layout_horizontal.count()):
                    if i > 3: break
                    self.layout_horizontal.itemAt(i).widget().setText(u'')
                    #self.layout_horizontal.itemAt(i).setStyleSheet('QPushButton { font-size: 11pt; }')
                    self.layout_horizontal.itemAt(i).widget().setText(readings[i])
        except:
            print 'Not enough quiz variants'
            #TODO: log this
        
    def getReadyPostLayout(self):
        self.sentence.hide()
        self.update()
        
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.labels = []
        
        #row, column, rows span, columns span, max columns
        i = 0; j = 0; r = 1; c = 1; n = 16
        for word in self.srs.parseCurrentExample():
            label = QLabel(word)
            label.setFont(QFont(self.options.getSentenceFont(), self.options.getSentenceFontSize()))
            #label.setFont(QFont(Fonts.HiragiNoMarugotoProW4, self.options.getSentenceFontSize()))
            
            label.setAttribute(Qt.WA_Hover, True)
            label.installEventFilter(self.filter)
            self.labels.append(label)
            
            if len(label.text()) > 1: c = len(label.text())
            else: c = 1
            #Don't ask, really
            if j + c > n: i = i + 1; j = 0
            
            self.grid_layout.addWidget(self.labels.pop(), i, j, r, c)       #NB: Ehh, pop should remove label from list, shouldn't it?
            
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
        self.pauseAction.setText('&Pause')
        self.pauseAction.setShortcut('P')
        
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
        
####################################
#        Actions and events        #
####################################    
    
    def setMenus(self):
        self.trayMenu.addAction(QAction('&Quiz me now!', self, shortcut="Q", triggered=self.showQuiz))
        self.pauseAction = QAction('&Start quiz!', self, shortcut="S", triggered=self.pauseQuiz)
        self.trayMenu.addAction(self.pauseAction)
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(QAction('Quick &dictionary', self, shortcut="D", triggered=self.showQuickDict))
        self.trayMenu.addAction(QAction('&Global &statistics', self, shortcut="G", triggered=self.showGlobalStatistics))
        self.trayMenu.addAction(QAction('&Options', self, shortcut="O", triggered=self.showOptions))
        self.trayMenu.addAction(QAction('&About', self, shortcut="A", triggered=self.showAbout))
        self.trayMenu.addSeparator()
        self.trayMenu.addAction(QAction('&Exit', self, shortcut="E", triggered=self.saveAndExit))

        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.activated.connect(self.onTrayIconActivated)

    #TODO: show session statistics
    def onTrayIconActivated(self, reason):
        '''
        if reason == QSystemTrayIcon.DoubleClick:
            print 'tray icon double clicked'
        '''
        if reason == QSystemTrayIcon.Trigger:
            if self.isHidden():
                self.trayIcon.showMessage('Current session statistics:', 'Running time:\t\t' + self.stats.getRunningTime() + 
                                          '\nItems seen:\t\t' + str(self.stats.totalItemSeen) + 
                                          '\nCorrect answers:\t\t' + str(self.stats.answeredCorrect) +
                                          '\nWrong answers:\t\t' + self.stats.getIncorrectAnswersCount() +
                                          '\nCorrect ratio:\t\t' + self.stats.getCorrectRatioPercent() +
                                          #'\nQuiz total time:\t\t' + self.stats.getQuizActive() +
                                          '\nQuiz paused time:\t\t' + self.stats.getPausedTime() +
                                          '\nTotal pondering time:\t' + self.stats.getMusingsTime() +
                                          '\nTotal post-quiz time:\t' + self.stats.getQuizTime() +
                                          '\nAverage pondering:\t' + self.stats.getAverageMusingTime() +
                                          '\nAverage post-quiz:\t' + self.stats.getAveragePostQuizTime(), 
                                          QSystemTrayIcon.MessageIcon.Information, 20000)
    
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
                
        self.var_1st.setShortcut('1')
        self.var_2nd.setShortcut('2')
        self.var_3rd.setShortcut('3')
        self.var_4th.setShortcut('4')
                
    def resetButtonsActions(self):
        self.var_1st.disconnect()
        self.var_2nd.disconnect()
        self.var_3rd.disconnect()
        self.var_4th.disconnect()
        
    def postAnswerActions(self):
        self.stats.musingsStopped()
        self.stats.postQuizStarted()
        
        self.stopCountdown()
        self.hideButtonsQuiz()
        
        self.getReadyPostLayout()
        
    def correctAnswer(self):
        '''
        self.stats.musingsStopped()
        self.stats.postQuizStarted()
        
        self.stopCountdown()
        self.hideButtonsQuiz()
        
        self.getReadyPostLayout()
        '''
        self.postAnswerActions()
        
        self.srs.answeredCorrect()
        self.stats.quizAnsweredCorrect()
        #self.answered.setText(u"<font='Cambria'>" + self.srs.getCurrentSentenceTranslation() + "</font>")
        self.answered.setText(self.srs.getCurrentSentenceTranslation())
        self.answered.setFont(QFont('Calibri', 11))
        self.showSessionMessage(u'<font color=green>Correct: ' + self.srs.getCorrectAnswer() + '</font>\t|\tNext quiz: ' + self.srs.getNextQuizTime() 
                                + '\t|\t<font color=' + self.srs.getLeitnerGradeAndColor()['color'] +  '>Grade: ' + self.srs.getLeitnerGradeAndColor()['grade'] 
                                + ' (' + self.srs.getLeitnerGradeAndColor()['name'] + ')<font>')
        
        #self.answered.setShortcut('5')
        #self.setFocus()
        
    def wrongAnswer(self):
        '''
        self.stats.musingsStopped()
        self.stats.postQuizStarted()
        
        self.stopCountdown()
        self.hideButtonsQuiz()
        
        self.getReadyPostLayout()
        '''
        self.postAnswerActions()
        
        self.srs.answeredWrong()
        self.stats.quizAnsweredWrong()
        
        self.answered.setText(self.srs.getCurrentSentenceTranslation())
        self.answered.setFont(QFont('Calibri', 11))
        #self.showSessionMessage(u"Wrong! Should be: <font style='font-family:" + Fonts.MSMyoutyou + "'>" 
                                #+ self.srs.getCorrectAnswer() + "</font> - Next quiz: " + self.srs.getNextQuizTime())
        self.showSessionMessage(u'<font color=tomato>Wrong! Should be: '+ self.srs.getCorrectAnswer() + '</font>\t|\tNext quiz: ' + self.srs.getNextQuizTime()
                                + '\t|\t<font color=' + self.srs.getLeitnerGradeAndColor()['color'] +  '>Grade: ' + self.srs.getLeitnerGradeAndColor()['grade'] 
                                + ' (' + self.srs.getLeitnerGradeAndColor()['name'] + ')<font>')
            
    def timeIsOut(self):
        self.stats.musingsStopped()
        self.stats.postQuizStarted()
        
        QTimer.singleShot(50, self.hideButtonsQuiz)     #NB: slight artificial lag to prevent recursive repaint crush, when mouse is suddenly over appearing button
        self.getReadyPostLayout()
        
        self.srs.answeredWrong()
        self.stats.quizAnsweredWrong()

        #self.showSessionMessage(u'Time is out! Correct answer is:' + self.srs.getCorrectAnswer())
        self.answered.setFont(QFont('Calibri', 11))
        self.answered.setText(self.srs.getCurrentSentenceTranslation())
        self.showSessionMessage(u'<font color=tomato>Timeout! Should be: ' + self.srs.getCorrectAnswer() + '</font>\t|\tNext quiz: ' + self.srs.getNextQuizTime()
                                + '\t|\t<font color=' + self.srs.getLeitnerGradeAndColor()['color'] +  '>Grade: ' + self.srs.getLeitnerGradeAndColor()['grade'] 
                                + ' (' + self.srs.getLeitnerGradeAndColor()['name'] + ')<font>')        
    
    def hideQuizAndWaitForNext(self):
        self.stats.postQuizEnded()
        
        self.status.hide()
        self.info.hide()
        self.allInfo.hide()
        self.resetButtonsActions()
        
        self.setWindowOpacity(1)
        self.fade()
        QTimer.singleShot(1000, self.hide)
        self.waitUntilNextTimeslot()
        updater.mayUpdate = True
 
    def pauseQuiz(self):
        if self.isHidden():
            if self.pauseAction.text() == '&Pause':
                self.nextQuizTimer.stop()
                self.pauseAction.setText('&Unpause')
                self.pauseAction.setShortcut('U')
                self.trayIcon.setToolTip('Quiz paused!')
                
                self.trayIcon.setIcon(QIcon('../res/tray/inactive.png'))
                self.stats.pauseStarted()
                
                updater.mayUpdate = True
                
            elif self.pauseAction.text() == '&Start quiz!':
                self.waitUntilNextTimeslot()
                self.pauseAction.setText('&Pause')
                self.pauseAction.setShortcut('P')
                self.trayIcon.setToolTip('Quiz in progress!')
                
                self.trayIcon.setIcon(QIcon('../res/tray/active.png'))
            else:
                self.waitUntilNextTimeslot()
                self.pauseAction.setText('&Pause')
                self.pauseAction.setShortcut('P')
                self.trayIcon.setToolTip('Quiz in progress!')
                
                self.trayIcon.setIcon(QIcon('../res/tray/active.png'))
                self.stats.pauseEnded()
                
                updater.mayUpdate = False
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
            self.stats.musingsStarted()
            
            if self.nextQuizTimer.isActive():   self.nextQuizTimer.stop()
            updater.mayUpdate = False
        else:
            self.showSessionMessage(u'Quiz is already underway!')
         
    def showOptions(self):
        self.optionsDialog.show()
        
    def showAbout(self):
        self.about.show()
        
    def showQuickDict(self):
        self.qdict.showQDict = True
        
    def showGlobalStatistics(self):
        print '...'
        
    def startTrayLoading(self):
        self.gifLoading.start()
        #self.iconTimer = QTimer()
        #self.iconTimer.timeout.connect(self.updateTrayIcon)
        #self.iconTimer.start(100)
        
    def stopTrayLoading(self):
        self.gifLoading.stop()
        
    def updateTrayIcon(self):
        self.trayIcon.setIcon(self.gifLoading.currentPixmap())
        
    def showSessionMessage(self, message):
        """Shows info message"""
        self.status.message.setText(message)
        self.status.show()
        #self.setFocus() #NB: does not work
 
    def saveAndExit(self):
        self.hide()
        self.status.hide()
        self.allInfo.hide()
        self.trayIcon.showMessage('Shutting down...', 'Saving session', QSystemTrayIcon.MessageIcon.Information, 20000 )
        #self.startTrayLoading()
        
        if self.countdownTimer.isActive():
                self.countdownTimer.stop()
        if self.nextQuizTimer.isActive():
                self.nextQuizTimer.stop()
        if self.progressTimer != () and self.progressTimer.isAlive():
                self.progressTimer.cancel()      
            
        self.srs.endCurrentSession()
        self.trayIcon.hide()

        self.hooker.stop()

        self.updater.stop()
        self.optionsDialog.close()
        self.about.close()
        self.qdict.close()
        self.close()        
        
    def addReferences(self, about, options, qdict, updater):
        self.about = about
        self.optionsDialog = options
        self.qdict = qdict
        self.updater = updater
        
    def initGlobalHotkeys(self):
        def toggleWidgetFlag(): self.qdict.showQDict = True
        self.hooker = GlobalHotkeyManager(toggleWidgetFlag , 'Q')
        self.hooker.setDaemon(True)
        self.hooker.start()
                
if __name__ == '__main__':

    app = QApplication(sys.argv)
    
    quiz = Quiz()
    if quiz.options.isPlastique():  app.setStyle('plastique')
    quiz.setWindowIcon(QIcon('../res/icons/suzu.png'))
    
    about = About()
    options = OptionsDialog(quiz.srs.db, quiz.options)
    qdict = QuickDictionary(quiz.jmdict, quiz.edict, quiz.kjd, quiz.srs.db, quiz.options)
        
    updater = BackgroundDownloader(quiz.options.getRepetitionInterval())
    updater.start()
    
    quiz.addReferences(about, options, qdict, updater)
    quiz.initGlobalHotkeys()
    
    sys.exit(app.exec_())
