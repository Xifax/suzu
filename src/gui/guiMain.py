# -*- coding: utf-8 -*-
'''
Created on Jan 31, 2011

@author: Yadavito
'''

# internal #
import sys
from datetime import datetime

# own #
from srs.srsManager import srsScheduler
from settings.fonts import Fonts
from settings.optionsBackend import Options
from settings.constants import *
from utilities.rtimer import RepeatTimer
from utilities.stats import Stats
from utilities.utils import GlobalHotkeyManager#, BackgroundDownloader 
from gui.guiManualAdd import ManualAdd 
from gui.guiUtil import roundCorners, unfillLayout
from jdict.db import DictionaryLookup
from utilities.log import log

# external #
from PySide.QtCore import QTimer,Qt,QRect,QObject,QEvent,QByteArray
from PySide.QtGui import *
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
            
            object.parent().info.hide()
            object.parent().allInfo.hide()
            object.parent().kanjiInfo.hide()

            desktop = QApplication.desktop().screenGeometry()
            object.parent().info.setGeometry(QRect(desktop.width() - H_INDENT - I_WIDTH - I_INDENT, desktop.height() - V_INDENT, I_WIDTH, I_HEIGHT))
        
        if event.type() == QEvent.HoverEnter:
            object.setStyleSheet("QLabel { color: rgb(0, 5, 255); }")
            
            object.parent().info.item.setText(object.text())
            
            reading = object.parent().srs.getWordPronunciationFromExample(object.text())
            if reading != object.text() :  object.parent().info.reading.setText(reading)
            else:   object.parent().info.reading.setText(u'')
            
            #parsing word
            script = scripts.script_boundaries(object.text())
            components = []

            for cluster in script:
                if scripts.script_type(cluster) == scripts.Script.Kanji:
                    for kanji in cluster:
                        components = components + list(object.parent().rdk[kanji]) + list('\n')
                        #kanji_list.append(kanji)
                
            #setting radikals
            if len(components) > 0: components.pop()    #remove last '\n'
            object.parent().info.components.setText(' '.join(components))
            
            #looking up translation    #TODO: show translation only when left/right button is pressed (otherwise, show just main translation)
            '''
            try:
                search = object.parent().edict[object.text()]
                #object.parent().info.translation.setText(' '.join(search.senses))        #NB: TOO MUCH!
                object.parent().info.translation.setText(search.senses_by_reading()[object.parent().srs.getWordPronunciationFromExample(object.text())][0])
            except:
                object.parent().info.translation.setText('')
            '''
            
            #object.parent().info.setWindowOpacity(0)
            #fade(object.parent().info)
            #QTimer.singleShot(100, object.parent().info.show)      #for additional smoothness
            object.parent().info.show()

        if event.type() == QEvent.MouseButtonPress:
            # item context menu #
            if event.button() == Qt.MiddleButton:
                object.parent().info.hide()
                object.parent().allInfo.hide()
                object.parent().kanjiInfo.hide()
                print 'Middle'   #TODO: add distinction between actions     
                
            # kanji info #
            if event.button() == Qt.RightButton:
                #if object.parent().info.isVisible() and object.parent().kanjiInfo.isHidden():  
                    
                object.parent().info.hide()
                object.parent().allInfo.hide()
                
                object.parent().kanjiInfo.info.setText(u'')
                
                script = scripts.script_boundaries(object.text())
                #kanji_list = []
                resulting_info = u''
    
                for cluster in script:
                    if scripts.script_type(cluster) == scripts.Script.Kanji:
                        for kanji in cluster:
                            try:
                                lookup = object.parent().kjd[kanji]
                                kun = lookup.kun_readings; on = lookup.on_readings; gloss = lookup.gloss
                                
                                #resulting_info += '<b>(' + kanji + ')</b>\t'
                                resulting_info += "<font style='font-family: " + Fonts.HiragiNoMyoutyouProW3 + "; font-size: 18pt'>(" + kanji + ")</font>\t"
                            
                                if len(kun) > 0:
                                    resulting_info += '<b>kun: </b>' + ', '.join(kun) + '\t'
                                if len(on) > 0:
                                    resulting_info += '<b>on:</b>' + ', '.join(on) + '<br/>'
                                    #resulting_info += '<b>on: </b>' + ', '.join(on) + '\t'
                                if len(gloss) > 0:
                                    resulting_info += "<font style='font-family: Calibri; font-size: 12pt'>" + ", ".join(gloss) + "</font><br/>"
                            except:
                                components += kanji + '<br/>'
                            #kanji_list.append(kanji)
                
                if resulting_info != '':  object.parent().kanjiInfo.info.setText(resulting_info.rstrip('<br/>'))
                else: object.parent().kanjiInfo.info.setText(u'No such kanji in kanjidic!')
                object.parent().kanjiInfo.show()
                
            # translation and strokes info #
            if event.button() == Qt.LeftButton:
                
                #if object.parent().info.isVisible() and object.parent().allInfo.isHidden():  
                object.parent().kanjiInfo.hide()
                object.parent().info.hide()
                              
                #object.parent().unfill(object.parent().allInfo.layout)
                unfillLayout(object.parent().allInfo.layout)
                object.parent().allInfo.layout.setMargin(1)
                #object.parent().allInfo.layout.setAlignment(Qt.AlignCenter)
                
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
                            object.parent().allInfo.layout.addWidget(gif, i, j);   j = j + 1
                            movie.start()
                              
                    i = i + 1
                
                # words translation
                translations = QLabel(u'')
                translations.setFont(QFont('Calibri', 11))
                translations.setWordWrap(True)
                translations.setAlignment(Qt.AlignCenter)
                try:
                    #search = object.parent().edict[object.text()]
                    search = object.parent().edict[object.parent().srs.getWordNonInflectedForm(object.text())]

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
                    
                    #variants = search.senses_by_reading()[object.parent().srs.getWordPronunciationFromExample(object.text())]#[0]       #NB: add non-inflected form control
                    variants = search.senses_by_reading()[object.parent().srs.getWordPronounciation(object.parent().srs.getWordNonInflectedForm(object.text()))][:3]  #TODO: or add option, specifying, how many variants
                    variants = filter (lambda e: e != '(P)', variants)                                                                          #should be shown
                    
                    translationText += '<b>' + object.parent().srs.getWordPronunciationFromExample(object.text()) + '</b>:\t' + ', '.join(variants)
                    translations.setText(translationText.rstrip('\n'))
                    
                    #print translations.text()
                except:
                    #object.parent().jmdict.lookupItemTranslationJoin(object.parent().srs.getWordNonInflectedForm(object.text()))
                    # at first - search just kana
                    # then - search word by reading
                    '''    
                    search = object.parent().jmdict.lookupItemByReading(object.parent().srs.getWordPronounciation(object.parent().srs.getWordNonInflectedForm(object.text())))
                    if len(search) > 0:
                        lookup = object.parent().jmdict.lookupItemTranslationJoin(search[0])
                        if len(lookup) > 5: lookup = lookup[:5]
                        translations.setText('<b>' + object.parent().srs.getWordPronunciationFromExample(object.text())+ '</b>:\t' + ', '.join(lookup))
                    '''
                    ### by reading
                    search = object.parent().jmdict.lookupTranslationByReadingJoin(object.parent().srs.getWordPronounciation(object.parent().srs.getWordNonInflectedForm(object.text())), object.parent().options.getLookupLang())
                    if len(search) > 0:
                        if len(search) > 5: search = search[:5]
                        translations.setText('<b>' + object.parent().srs.getWordPronunciationFromExample(object.text())+ '</b>:\t' + ', '.join(search))
                    ### by kanji
                    else:
                        search = object.parent().jmdict.lookupItemByReading(object.parent().srs.getWordPronounciation(object.parent().srs.getWordNonInflectedForm(object.text())))
                        if len(search) > 0:
                            lookup = object.parent().jmdict.lookupItemTranslationJoin(search[0], object.parent().options.getLookupLang())
                            if len(lookup) > 5: lookup = lookup[:5]
                            translations.setText('<b>' + object.parent().srs.getWordPronunciationFromExample(object.text())+ '</b>:\t' + ', '.join(lookup))
                    ### nothing found
                    if len(search) == 0: translations.setText(u'Alas, no translation in edict or jmdict!')
                
                if i > 0:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.HLine)
                    separator.setFrameShadow(QFrame.Sunken)
                    object.parent().allInfo.layout.addWidget(separator, i, 0, 1, j);   i = i + 1
                
                object.parent().allInfo.layout.addWidget(translations, i, 0, 1, j)    #NB: rows span should be changed, maybe
                
                object.parent().allInfo.update()
                object.parent().allInfo.show()
                
            elif object.parent().allInfo.isVisible():  #object.parent().info.isHidden():

                object.parent().allInfo.hide()   
                object.parent().info.show()
            
        return False

class StatusFilter(QObject):
    """Status message mouse click filter"""
    def eventFilter(self, object, event):
        
        if event.type() == QEvent.HoverEnter:
            object.parent().status.setWindowOpacity(0.70)
            
        if event.type() == QEvent.HoverLeave:
            object.parent().status.setWindowOpacity(1)
            
        if event.type() == QEvent.MouseButtonPress:
            object.parent().status.hide()
            
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
        #self.status.filter = StatusFilter()
        self.status.setAttribute(Qt.WA_Hover, True)
        #self.status.installEventFilter(self.status.filter)

        """Items Info"""
        self.info = QFrame()
        self.info.reading = QLabel(u'')
        self.info.item = QLabel(u'')
        self.info.components = QLabel(u'')

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
        self.info.setLayout(self.info.layout)
        
        """Verbose Info"""
        self.allInfo = QFrame()
        self.allInfo.layout = QGridLayout()
        self.allInfo.setLayout(self.allInfo.layout)
        #the rest is (should be) generated on the fly
        
        """Kanji info"""
        self.kanjiInfo = QFrame()
        self.kanjiInfo.layout = QVBoxLayout()
        self.kanjiInfo.info = QLabel(u'')
        self.kanjiInfo.layout.addWidget(self.kanjiInfo.info)
        self.kanjiInfo.setLayout(self.kanjiInfo.layout)
        
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
            
        self.setWindowIcon(QIcon(PATH_TO_RES + ICONS + 'suzu.png'))
        """Test calls here:"""
        ###    ...    ###
        #self.connect(self.hooker, SIGNAL('noQdict'), self.noQdict)
        self.gem = self.saveGeometry()

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

        """Manual add dialog"""
        self.manualAddDialog = ManualAdd(self.srs.db)
        
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
        
        """Kanji info"""
        self.kanjiInfo.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.kanjiInfo.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.kanjiInfo.setGeometry(QRect(desktop.width() - H_INDENT - K_WIDTH - K_INDENT, desktop.height() - V_INDENT, K_WIDTH, K_HEIGHT))
        
        self.kanjiInfo.setStyleSheet("QWidget { background-color: rgb(255, 255, 255); }")
        
#        self.setMask(roundCorners(self.rect(),5))
#        self.status.setMask(roundCorners(self.status.rect(),5))

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
        self.trayIcon.setIcon(QIcon(PATH_TO_RES + TRAY + 'active.png'))
        
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
        
        self.kanjiInfo.info.setFont(QFont(Fonts.MSMyoutyou, 14.5))
        self.kanjiInfo.info.setAlignment(Qt.AlignCenter)
        self.kanjiInfo.info.setWordWrap(True)
        self.kanjiInfo.layout.setMargin(0)
        #NB: ...
        self.answered.setMaximumWidth(D_WIDTH)
        self.answered.setFont(QFont('Calibri', 11))


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
        
        example = self.srs.getCurrentExample()
        
        #NB: checking for no example case
        if example is None:
            self.manualAddDialog.setProblemKanji(self.srs.getCurrentItemKanji())
            done = self.manualAddDialog.exec_()
            
            if done == 0:
                self.updateContent()
            elif done == 1:
                self.updateContent()
            else:
                pass
        else:
            example = example.replace(self.srs.getWordFromExample(), u"<font color='blue'>" + self.srs.getWordFromExample() + u"</font>")
            
            print datetime.now() - start    #testing
            self.sentence.setText(example)
            
            start = datetime.now()  #testing
            readings = self.srs.getQuizVariants()
            print datetime.now() - start    #testing
            

            changeFont = False
            for item in readings:
                if len(item) > BUTTON_KANA_MAX : changeFont = True
                
#            if changeFont: self.setStyleSheet('QPushButton { font-size: 11pt; }')
#            else:   self.setStyleSheet('QPushButton { font-size: %spt; }' % self.options.getQuizFontSize())

            try:
                for i in range(0, self.layout_horizontal.count()):
                        if i > 3: break
                        self.layout_horizontal.itemAt(i).widget().setText(u'')
                        
                        if changeFont:
                            self.layout_horizontal.itemAt(i).widget().setStyleSheet('QPushButton { font-size: 11pt; }')
                        else:
                            self.layout_horizontal.itemAt(i).widget().setStyleSheet('QPushButton { font-size: %spt; }' % self.options.getQuizFontSize())
                            
                        self.layout_horizontal.itemAt(i).widget().setText(readings[i])
            except:
                log.debug(u'Not enough quiz variants for ' + self.srs.getCurrentItem())
        
    def getReadyPostLayout(self):
        self.sentence.hide()
        self.update()
        
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.labels = []
        
        #row, column, rows span, columns span, max columns
        i = 0; j = 0; r = 1; c = 1; n = 22
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
        self.postAnswerActions()
        
        self.srs.answeredCorrect()
        self.stats.quizAnsweredCorrect()
        
        self.answered.setText(self.srs.getCurrentSentenceTranslation())
        self.checkTranslationSize()
        
        self.showSessionMessage(u'<font color=green>Correct: ' + self.srs.getCorrectAnswer() + '</font>\t|\tNext quiz: ' + self.srs.getNextQuizTime() 
                                + '\t|\t<font color=' + self.srs.getLeitnerGradeAndColor()['color'] +  '>Grade: ' + self.srs.getLeitnerGradeAndColor()['grade'] 
                                + ' (' + self.srs.getLeitnerGradeAndColor()['name'] + ')<font>')
        
        #self.answered.setShortcut('5')
        #self.setFocus()
        
    def wrongAnswer(self):
        self.postAnswerActions()
        
        self.srs.answeredWrong()
        self.stats.quizAnsweredWrong()
        
        self.answered.setText(self.srs.getCurrentSentenceTranslation())
        self.checkTranslationSize()
        
        self.showSessionMessage(u'<font color=tomato>Wrong! Should be: '+ self.srs.getCorrectAnswer() + '</font>\t|\tNext quiz: ' + self.srs.getNextQuizTime()
                                + '\t|\t<font color=' + self.srs.getLeitnerGradeAndColor()['color'] +  '>Grade: ' + self.srs.getLeitnerGradeAndColor()['grade'] 
                                + ' (' + self.srs.getLeitnerGradeAndColor()['name'] + ')<font>')
            
    def timeIsOut(self):
        self.stats.musingsStopped()
        self.stats.postQuizStarted()
        
        QTimer.singleShot(50, self.hideButtonsQuiz)     #NB: slight artificial lag to prevent recursive repaint crush (when mouse is suddenly over repainted button)
        self.getReadyPostLayout()
        
        self.srs.answeredWrong()
        self.stats.quizAnsweredWrong()

        self.answered.setText(self.srs.getCurrentSentenceTranslation())
        self.checkTranslationSize()
        
        self.showSessionMessage(u'<font color=tomato>Timeout! Should be: ' + self.srs.getCorrectAnswer() + '</font>\t|\tNext quiz: ' + self.srs.getNextQuizTime()
                                + '\t|\t<font color=' + self.srs.getLeitnerGradeAndColor()['color'] +  '>Grade: ' + self.srs.getLeitnerGradeAndColor()['grade'] 
                                + ' (' + self.srs.getLeitnerGradeAndColor()['name'] + ')<font>')    
        
    def checkTranslationSize(self):
        if len(self.answered.text()) > TRANSLATION_CHARS_LIMIT:
            self.answered.setStyleSheet('QPushButton { font-size: 8pt; }')
        else:
            self.answered.setStyleSheet('QPushButton { font-size: 11pt; }')
    
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
        self.updater.mayUpdate = True
 
    def pauseQuiz(self):
        if self.isHidden():
            if self.pauseAction.text() == '&Pause':
                self.nextQuizTimer.stop()
                self.pauseAction.setText('&Unpause')
                self.pauseAction.setShortcut('U')
                self.trayIcon.setToolTip('Quiz paused!')
                
                self.trayIcon.setIcon(QIcon(PATH_TO_RES + TRAY + 'inactive.png'))
                self.stats.pauseStarted()
                
                self.updater.mayUpdate = True
                
            elif self.pauseAction.text() == '&Start quiz!':
                self.waitUntilNextTimeslot()
                self.pauseAction.setText('&Pause')
                self.pauseAction.setShortcut('P')
                self.trayIcon.setToolTip('Quiz in progress!')
                
                self.trayIcon.setIcon(QIcon(PATH_TO_RES + TRAY + 'active.png'))
            else:
                self.waitUntilNextTimeslot()
                self.pauseAction.setText('&Pause')
                self.pauseAction.setShortcut('P')
                self.trayIcon.setToolTip('Quiz in progress!')
                
                self.trayIcon.setIcon(QIcon(PATH_TO_RES + TRAY + 'active.png'))
                self.stats.pauseEnded()
                
                self.updater.mayUpdate = False
        else:
            self.showSessionMessage(u'Sorry, cannot pause while quiz in progress!')
 
    def showQuiz(self):
        if self.isHidden():
            self.updateContent()
            self.setButtonsActions()
            
            #self.restoreGeometry(self.gem)
            
            self.show()
            self.setWindowOpacity(0)
            self.fade()

            self.countdown.setValue(self.options.getCountdownInterval() * 100)
            self.beginCountdown()
            self.stats.musingsStarted()
            
            if self.nextQuizTimer.isActive():   self.nextQuizTimer.stop()
            self.updater.mayUpdate = False
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
        self.kanjiInfo.hide()
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
        
    def showEvent(self, event):
        self.restoreGeometry(self.gem)
