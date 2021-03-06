# -*- coding: utf-8 -*-
'''
Created on Jan 31, 2011

@author: Yadavito
'''

# internal #
#import sys
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
from gui.guiLoad import QuickLoad
from jdict.db import DictionaryLookup
from jtools.jgroup import KanjiGrouper
from utilities.log import log
from utilities.bijin import Achievements

# external #
from PySide.QtCore import QTimer,Qt,QRect,QObject,QEvent,QByteArray
from PySide.QtGui import *
from cjktools.resources.radkdict import RadkDict
from pkg_resources import resource_filename
from cjktools.resources import auto_format
from cjktools.resources import kanjidic
from cjktools import scripts
from ordereddict import OrderedDict

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
            object.parent().kanjiGroups.hide()

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
                
            #setting radikals
            if len(components) > 0: components.pop()    #remove last '\n'
            object.parent().info.components.setText(' '.join(components))
            object.parent().info.show()

        if event.type() == QEvent.MouseButtonPress:
            # item context menu #
            if event.button() == Qt.MiddleButton:
                
                object.parent().info.hide()
                object.parent().allInfo.hide()
                object.parent().kanjiInfo.hide()
                
                script = scripts.script_boundaries(object.text())
                resulting_info = u''
#                kanji_groups = {}
                kanji_groups = OrderedDict()
    
                for cluster in script:
                    if scripts.script_type(cluster) == scripts.Script.Kanji:
#                        for kanji in cluster[::-1]:
                        for kanji in cluster:
                            similar = object.parent().groups.findSimilarKanji(kanji)
                            try:
                                kanji_groups[kanji] = similar[:similar.index(kanji)] + similar[similar.index(kanji) + 1:] 
                            except Exception:
                                kanji_groups[kanji] = object.parent().groups.findSimilarKanji(kanji)
                                log.debug(u'Not in group: ' + kanji)
                            
                for kanji in kanji_groups:
#                for kanji in list(reversed(sorted(kanji_groups.keys()))):
                    resulting_info += kanji + u' ～\t'
                    for item in kanji_groups[kanji]:
                        lookup = object.parent().kjd[item]
                        resulting_info += " " + item + " <font style='font-family: Calibri; font-size: 12pt'>(" + lookup.gloss[0] + ")</font> "
                    resulting_info += '<br/>'
                
                if resulting_info == u'': resulting_info = u'No such groups in Kanji.Odyssey!'
                object.parent().kanjiGroups.info.setText(resulting_info)
                
                object.parent().kanjiGroups.show()
                
            # kanji info #
            if event.button() == Qt.RightButton:
                    
                object.parent().info.hide()
                object.parent().allInfo.hide()
                object.parent().kanjiGroups.hide()
                
                object.parent().kanjiInfo.info.setText(u'')
                
                script = scripts.script_boundaries(object.text())
                resulting_info = u''
    
                for cluster in script:
                    if scripts.script_type(cluster) == scripts.Script.Kanji:
                        for kanji in cluster:
                            try:
                                lookup = object.parent().kjd[kanji]
                                kun = lookup.kun_readings; on = lookup.on_readings; gloss = lookup.gloss
                                
                                resulting_info += "<font style='font-family: " + Fonts.HiragiNoMyoutyouProW3 + "; font-size: 16.5pt'>(" + kanji + ")</font>\t"
                            
                                if len(kun) > 0:
                                    resulting_info += '<b>kun: </b>' + ', '.join(kun) + '\t'
                                if len(on) > 0:
                                    resulting_info += '<b>on:</b>' + ', '.join(on) + '<br/>'
                                if len(gloss) > 0:
                                    resulting_info += "<font style='font-family: Calibri; font-size: 12pt'>" + ", ".join(gloss) + "</font><br/>"
                            except:
                                components += kanji + '<br/>'
                
                if resulting_info != '':  
                    if resulting_info.count('<br/>') > 7:  object.parent().kanjiInfo.setStyleSheet('QLabel { font-size: 13pt }')
                    object.parent().kanjiInfo.info.setText(resulting_info.rstrip('<br/>'))
                    
                else: object.parent().kanjiInfo.info.setText(u'No such kanji in kanjidic!')
                object.parent().kanjiInfo.show()
                
            # translation and strokes info #
            if event.button() == Qt.LeftButton:
                
                object.parent().kanjiInfo.hide()
                object.parent().info.hide()
                object.parent().kanjiGroups.hide()
                              
                unfillLayout(object.parent().allInfo.layout)
                object.parent().allInfo.layout.setMargin(1)
                
                kanjiList = []
                script = scripts.script_boundaries(object.text())

                for cluster in script:
                    if scripts.script_type(cluster) == scripts.Script.Kanji:
                        for kanji in cluster:
                            kanjiList.append(kanji)
                
                i=0; j=0;
                # kanji strokes
                if len(kanjiList) > 0:
                    
                    infile = open(PATH_TO_RES + STROKES + KANJI_MANIFEST, 'r')
                    text = infile.read()
                    infile.close()
                    
                    for kanji in kanjiList:
                        
                        if( text.find(kanji.encode('utf-8').encode('hex')) != -1):
                        
                            gif = QLabel()
                            gif.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)        
                            gif.setAlignment(Qt.AlignCenter) 
    
                            movie = QMovie(PATH_TO_RES + STROKES + kanji.encode('utf-8').encode('hex') + '.gif', QByteArray(), self) 
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
                    search = object.parent().edict[object.parent().srs.getWordNonInflectedForm(object.text())]

                    translationText = u''
                    
                    variants = search.senses_by_reading()[object.parent().srs.getWordPronounciation(object.parent().srs.getWordNonInflectedForm(object.text()))][:3]
                    variants = filter (lambda e: e != '(P)', variants)                                                                         
                    
                    translationText += '<b>' + object.parent().srs.getWordPronunciationFromExample(object.text()) + '</b>:\t' + ', '.join(variants)
                    translations.setText(translationText.rstrip('\n'))
                    
                except:
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
                
                object.parent().allInfo.layout.addWidget(translations, i, 0, 1, j)
                
                object.parent().allInfo.update()
                object.parent().allInfo.show()
                
            elif object.parent().allInfo.isVisible():

                object.parent().allInfo.hide()   
                object.parent().info.show()
            
        return False

class StatusFilter(QObject):
    """Status message mouse click filter"""
    def eventFilter(self, object, event):
        
        if event.type() == QEvent.HoverEnter:
            object.setWindowOpacity(0.90)
            object.progress.setValue(object.achievements.score)
            
            if object.achievements.achieved is not None:
                object.progress.setMaximum(object.achievements.threshold)
                object.progress.setValue(0)
            else:
                object.progress.show()
            object.activateWindow()

        if event.type() == QEvent.HoverLeave:
            object.setWindowOpacity(1)
            object.progress.hide()

        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                if object.achievements.achieved is not None:
                    object.web.searchImages(object.achievements.achieved[1])
                    object.web.show()
            elif event.button() == Qt.RightButton:
                object.hide()
            
        return False

#######
# GUI #
#######

class Quiz(QFrame):
     
    def __init__(self, options, parent=None):
        super(Quiz, self).__init__(parent)
        
        self.options = options
        
        """Session Info"""
        self.status = QFrame()
        #session message
        self.status.message = QLabel(u'')
        #achievements
        self.status.achievements = Achievements()
        self.status.info = QLabel(u'')
        self.status.progress = QProgressBar()
        self.status.layout = QVBoxLayout()
        #layout
        self.status.layout.addWidget(self.status.info)
        self.status.layout.addWidget(self.status.progress)
        self.status.layout.addWidget(self.status.message)
        self.status.setLayout(self.status.layout)
        #mouse event filter
        self.status.filter = StatusFilter(self.status)
        self.status.setAttribute(Qt.WA_Hover, True)
        self.status.installEventFilter(self.status.filter)

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
        
        """Kanji groups"""
        self.kanjiGroups = QFrame()
        self.kanjiGroups.layout = QVBoxLayout()
        self.kanjiGroups.info = QLabel(u'')
        self.kanjiGroups.layout.addWidget(self.kanjiGroups.info)
        self.kanjiGroups.setLayout(self.kanjiGroups.layout)
        
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
        
        ### initializing ###
        self.initializeResources()
        
        ### timers ###
        self.nextQuizTimer = QTimer()
        self.nextQuizTimer.setSingleShot(True)
        self.nextQuizTimer.timeout.connect(self.showQuiz)
        
        self.countdownTimer = QTimer()
        self.countdownTimer.setSingleShot(True)
        self.countdownTimer.timeout.connect(self.timeIsOut)
        
        self.trayUpdater = None
        #self.trayUpdater = RepeatTimer(1.0, self.updateTrayTooltip, self.options.getRepetitionInterval() * 60)
        self.remaining = 0
        
        """Start!"""
        if self.options.isQuizStartingAtLaunch():
            self.waitUntilNextTimeslot()
            self.trayIcon.setToolTip('Quiz has started automatically!')
            self.pauseAction.setText('&Pause')
            self.trayIcon.showMessage('Loading complete! (took ~'+ str(self.loadingTime.seconds) + ' seconds) Quiz underway.', 
                                      'Lo! Quiz already in progress!'  + self.loadingStatus, QSystemTrayIcon.MessageIcon.Warning, 10000)
        else:
            self.trayIcon.setToolTip('Quiz is not initiated!')
            self.trayIcon.showMessage('Loading complete! (took ~' + str(self.loadingTime.seconds) + ' seconds) Standing by.', 
                                      'Quiz has not started yet! If you wish, you could start it manually or enable autostart by default.'  + self.loadingStatus, 
                                      QSystemTrayIcon.MessageIcon.Information, 10000 )
            
        self.setWindowIcon(QIcon(PATH_TO_RES + ICONS + 'suzu.png'))
        """Test calls here:"""
        ###    ...    ###
        #self.connect(self.hooker, SIGNAL('noQdict'), self.noQdict)
        self.gem = self.saveGeometry()
        
    def startUpdatingTrayTooltip(self):
        self.remaining = self.nextQuizTimer.interval()
        
        if self.trayUpdater is not None and self.trayUpdater.isAlive():
            self.trayUpdater.cancel()
            
        self.trayUpdater = RepeatTimer(1.0, self.updateTrayTooltip, self.options.getRepetitionInterval() * 60)
        self.trayUpdater.start()
        
    def updateTrayTooltip(self):
        self.remaining -= UPDATE_FREQ
        self.trayIcon.setToolTip('Next quiz in ' + (str(self.remaining/UPDATE_FREQ) + ' seconds'))

#    def noQdict(self):
#        self.showSessionMessage('Nope, cannot show quick dictionary during actual quiz.')
        
####################################
#    Initialization procedures     #
####################################

    def initializeResources(self):
        
        """Initialize Options"""
#        self.options = Options()
        self.loadingStatus = u''
        
        self.qload = QuickLoad(self.options)
        if self.options.isLoadingOnStart():
            self.qload.exec_()
        
        """Pre-initialization"""
        self.animationTimer = ()
        self.progressTimer = ()
        self.grid_layout =()
        
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
        
        self.trayIcon.showMessage('Loading...', 'Initializing dictionaries', QSystemTrayIcon.MessageIcon.Information, 20000 )
        # kanji composition #
        if self.options.isLoadingRadk(): self.rdk = RadkDict()
        else: self.loadingStatus += '--> Radikt disabled!\n'
        # edict dictionary
        if self.options.isLoadingEdict():
            edict_file = resource_filename('cjktools_data', 'dict/je_edict')
            self.edict = auto_format.load_dictionary(edict_file)
        else: 
            self.edict = None
            self.loadingStatus += '--> Edict disabled!\n'
        # kanjidict dictionary #
        if self.options.isLoadingKdict(): self.kjd = kanjidic.Kanjidic()
        else: 
            self.kjd = None
            self.loadingStatus += '--> Kanjidict disabled!\n'
        # Kanji.Odyssey groups #
        self.groups = KanjiGrouper()
        if self.options.isLoadingGroups(): self.groups.loadgroupsFromDump()
        else: self.loadingStatus += '--> Kanji.Odyssey disabled!\n'
        
        """Initializing srs system"""
        self.trayIcon.showMessage('Loading...', 'Initializing databases', QSystemTrayIcon.MessageIcon.Information, 20000 )
        self.srs = srsScheduler()
        if self.options.isLoadingDb(): self.srs.initializeCurrentSession(self.options.getQuizMode(), self.options.getSessionSize())
        else: self.loadingStatus += '--> Database disabled!\n'
        
        """Jmdict lookup"""
        self.jmdict = DictionaryLookup()
        if self.options.isLoadingJmdict(): 
            self.jmdict.loadJmdictFromDumpRegex()
            self.jmdict.joinTables()
        else: self.loadingStatus += '--> Jmdict disabled!\n'
                
        """Manual add dialog"""
        self.manualAddDialog = ManualAdd(self.srs.db)
        
        if self.loadingStatus != '': self.loadingStatus = '\n\n' + self.loadingStatus
        
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
        #NB: This font will be used in buttons
        self.setFont(QFont(Fonts.TukusiMyoutyouProLB, self.options.getQuizFontSize()))

        desktop = QApplication.desktop().screenGeometry()
        self.setGeometry(QRect(desktop.width() - H_INDENT, desktop.height() - V_INDENT, D_WIDTH, D_HEIGHT))
        
        self.setStyleSheet("QWidget { background-color: rgb(252, 252, 252); }")
        
        """Info dialog"""
        self.info.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.info.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.info.setGeometry(QRect(desktop.width() - H_INDENT - I_WIDTH - I_INDENT, desktop.height() - V_INDENT, I_WIDTH, I_HEIGHT))
        
        self.info.setStyleSheet("QWidget { background-color: rgb(252, 252, 252); }")
        
        """Verbose info dialog"""
        self.allInfo.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.allInfo.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.allInfo.setGeometry(QRect(desktop.width() - H_INDENT - I_WIDTH - I_INDENT, desktop.height() - V_INDENT, I_WIDTH, I_HEIGHT))
        
        self.allInfo.setStyleSheet("QWidget { background-color: rgb(252, 252, 252); }")
        
        """Session message"""
        self.status.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.status.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.status.setGeometry(QRect(desktop.width() - H_INDENT, desktop.height() - V_INDENT - S_HEIGHT - S_INDENT - S_CORRECTION, S_WIDTH, S_HEIGHT))
        self.status.setMinimumSize(S_WIDTH, S_HEIGHT)
#        self.status.setMinimumWidth(S_WIDTH)
        
        self.status.setStyleSheet("QWidget { background-color: rgb(252, 252, 252); }")
        
        self.setMask(roundCorners(self.rect(),5))
#        self.status.setMask(roundCorners(self.status.rect(),5))
        #self.info.setMask(roundCorners(self.info.rect(),5))
        #self.allInfo.setMask(roundCorners(self.allInfo.rect(),5))
        
        """Kanji info"""
        self.kanjiInfo.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.kanjiInfo.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.kanjiInfo.setGeometry(QRect(desktop.width() - H_INDENT - K_WIDTH - K_INDENT, desktop.height() - V_INDENT, K_WIDTH, K_HEIGHT))
        
        self.kanjiInfo.setStyleSheet("QWidget { background-color: rgb(252, 252, 252); }")
        
        """Kanji groups"""
        self.kanjiGroups.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.kanjiGroups.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.kanjiGroups.setGeometry(QRect(desktop.width() - H_INDENT - G_WIDTH - G_INDENT, desktop.height() - V_INDENT, G_WIDTH, G_HEIGHT))
        
        self.kanjiGroups.setStyleSheet("QWidget { background-color: rgb(250, 250, 250); }")
        
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
        self.status.message.setAlignment(Qt.AlignCenter)
        self.status.layout.setMargin(0)
        
        self.status.info.setHidden(True)
        self.status.progress.setHidden(True)
        self.status.progress.setMaximumHeight(10)
        self.status.progress.setRange(0, self.status.achievements.threshold)
        self.status.layout.setAlignment(Qt.AlignCenter)
        self.status.info.setAlignment(Qt.AlignCenter)
        self.status.info.setFont(QFont(Fonts.RyuminPr5, 13))
        self.status.info.setWordWrap(False)
        
        self.status.gem = self.status.saveGeometry()
        
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
        
        self.kanjiGroups.info.setFont(QFont(Fonts.MSMyoutyou, 18.5))
        self.kanjiGroups.info.setAlignment(Qt.AlignCenter)
        self.kanjiGroups.info.setWordWrap(True)
        self.kanjiGroups.layout.setMargin(0)
        
        #NB: ...
        self.answered.setMaximumWidth(D_WIDTH)
        self.answered.setFont(QFont('Calibri', 11))


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
              
        example = self.srs.getCurrentExample()
        
        # checking for no example case
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
            
            # checking sentence length
            if len(self.srs.currentExample.sentence) > SENTENCE_MAX: self.sentence.setFont(QFont(self.options.getSentenceFont(), MIN_FONT_SIZE))
            else: self.sentence.setFont(QFont(self.options.getSentenceFont(), self.options.getSentenceFontSize()))
            
            #temporary debug info:
#            print len(example), self.sentence.font()
            
            self.sentence.setText(example)
            
            readings = self.srs.getQuizVariants()

            changeFont = False
            for item in readings:
                if len(item) > BUTTON_KANA_MAX : changeFont = True
                
            try:
                for i in range(0, self.layout_horizontal.count()):
                        if i > 3: break
                        self.layout_horizontal.itemAt(i).widget().setText(u'')
                        
                        if changeFont:
                            self.layout_horizontal.itemAt(i).widget().setStyleSheet('QPushButton { font-family: ' + self.options.getQuizFont() + '; font-size: 11pt; }')
                        else:
                            self.layout_horizontal.itemAt(i).widget().setStyleSheet('QPushButton { font-family: ' + self.options.getQuizFont() + '; font-size: %spt; }' % self.options.getQuizFontSize())
                            
                        self.layout_horizontal.itemAt(i).widget().setText(readings[i])
            except:
                log.debug(u'Not enough quiz variants for ' + self.srs.getCurrentItem())
        
    def getReadyPostLayout(self):
        self.sentence.hide()
        self.update()
        
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.labels = []
        
        columns_mod = 0
        #font size depending on sentence length
        if len(self.srs.currentExample.sentence) > SENTENCE_MAX: font =  QFont(self.options.getSentenceFont(), MIN_FONT_SIZE); columns_mod = 6
        else: font = QFont(self.options.getSentenceFont(), self.options.getSentenceFontSize())
        
        #row, column, rows span, columns span, max columns
        i = 0; j = 0; r = 1; c = 1; n = COLUMNS_MAX + columns_mod
        for word in self.srs.parseCurrentExample():
            label = QLabel(word)
            label.setFont(font)
            
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
        self.startUpdatingTrayTooltip()
        
    def beginCountdown(self):
        self.trayIcon.setToolTip('Quiz in progress!')
        self.pauseAction.setText('&Pause')
#        self.pauseAction.setShortcut('P')
        
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
        
        self.showQuizAction = QAction('&Quiz me now!', self, triggered=self.showQuiz)
        self.showQuizAction.setIcon(QIcon(PATH_TO_RES + TRAY + NOW_ICON))
        self.trayMenu.addAction(self.showQuizAction)
        
        self.pauseAction = QAction('&Start quiz!', self, triggered=self.pauseQuiz)
        self.pauseAction.setIcon(QIcon(PATH_TO_RES + TRAY + START_ICON))
        self.trayMenu.addAction(self.pauseAction)
        
        self.trayMenu.addSeparator()
        
        self.quickDictAction = QAction('Quick &dictionary', self, triggered=self.showQuickDict)
        self.quickDictAction.setIcon(QIcon(PATH_TO_RES + TRAY + DICT_ICON))
        self.trayMenu.addAction(self.quickDictAction)
        
        self.optionsAction = QAction('&Options', self, triggered=self.showOptions)
        self.optionsAction.setIcon(QIcon(PATH_TO_RES + TRAY + OPTIONS_ICON))
        self.trayMenu.addAction(self.optionsAction)
        
        self.quickLoadAction = QAction('Quick &load', self, triggered=self.showQuickLoad)
        self.quickLoadAction.setIcon(QIcon(PATH_TO_RES + TRAY + LOAD_ICON))
        self.trayMenu.addAction(self.quickLoadAction)
        
        self.trayMenu.addSeparator()
        
        self.aboutAction = QAction('&About', self, triggered=self.showAbout)
        self.aboutAction.setIcon(QIcon(PATH_TO_RES + TRAY + ABOUT_ICON))
        self.trayMenu.addAction(self.aboutAction)
        
        self.globalStatsAction = QAction('&Global statistics', self, triggered=self.showGlobalStatistics)
        self.globalStatsAction.setIcon(QIcon(PATH_TO_RES + TRAY + STAT_ICON))
        self.trayMenu.addAction(self.globalStatsAction)
        
        self.utilAction = QAction('U&tilities', self, triggered=self.showToolsDialog)
        self.utilAction.setIcon(QIcon(PATH_TO_RES + TRAY + UTILS_ICON))
        self.trayMenu.addAction(self.utilAction)
        
        self.trayMenu.addSeparator()
        
        self.quitAction = QAction('&Exit', self, triggered=self.saveAndExit)
        self.quitAction.setIcon(QIcon(PATH_TO_RES + TRAY + CLOSE_ICON))
        self.trayMenu.addAction(self.quitAction)
        

        self.trayIcon.setContextMenu(self.trayMenu)
        self.trayIcon.activated.connect(self.onTrayIconActivated)

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
        
    def refocusQuiz(self):
        self.answered.setShortcut('Space')
        self.activateWindow()
        self.answered.setFocus()
        
    def correctAnswer(self):
        self.postAnswerActions()
        
        self.srs.answeredCorrect()
        self.stats.quizAnsweredCorrect()
        
        self.checkTranslationSize(self.srs.getCurrentSentenceTranslation())

        self.status.achievements.correctAnswer()
        self.showSessionMessage(u'<font color=green>Correct: ' + self.srs.getCorrectAnswer() + '</font>\t|\tNext quiz: ' + self.srs.getNextQuizTime() 
                                + '\t|\t<font color=' + self.srs.getLeitnerGradeAndColor()['color'] +  '>Grade: ' + self.srs.getLeitnerGradeAndColor()['grade'] 
                                + ' (' + self.srs.getLeitnerGradeAndColor()['name'] + ')<font>')
        self.refocusQuiz()
        
    def wrongAnswer(self):
        self.postAnswerActions()
        
        self.srs.answeredWrong()
        self.stats.quizAnsweredWrong()
        
        self.checkTranslationSize(self.srs.getCurrentSentenceTranslation())
        
        self.status.achievements.wrongAnswer()
        self.showSessionMessage(u'<font color=tomato>Wrong! Should be: '+ self.srs.getCorrectAnswer() + '</font>\t|\tNext quiz: ' + self.srs.getNextQuizTime()
                                + '\t|\t<font color=' + self.srs.getLeitnerGradeAndColor()['color'] +  '>Grade: ' + self.srs.getLeitnerGradeAndColor()['grade'] 
                                + ' (' + self.srs.getLeitnerGradeAndColor()['name'] + ')<font>')
        self.refocusQuiz()
            
    def timeIsOut(self):
        self.stats.musingsStopped()
        self.stats.postQuizStarted()
        
        QTimer.singleShot(50, self.hideButtonsQuiz)     #NB: slight artificial lag to prevent recursive repaint crush (when mouse is suddenly over repainted button)
        self.getReadyPostLayout()
        
        self.srs.answeredWrong()
        self.stats.quizAnsweredWrong()

        self.checkTranslationSize(self.srs.getCurrentSentenceTranslation())
        
        self.status.achievements.wrongAnswer()
        self.showSessionMessage(u'<font color=tomato>Timeout! Should be: ' + self.srs.getCorrectAnswer() + '</font>\t|\tNext quiz: ' + self.srs.getNextQuizTime()
                                + '\t|\t<font color=' + self.srs.getLeitnerGradeAndColor()['color'] +  '>Grade: ' + self.srs.getLeitnerGradeAndColor()['grade'] 
                                + ' (' + self.srs.getLeitnerGradeAndColor()['name'] + ')<font>')    
        self.refocusQuiz()
        
    def checkTranslationSize(self, translation):
        if len(translation) > TRANSLATION_CHARS_LIMIT:
            self.answered.setStyleSheet('QPushButton { font-size: 9pt; }')
            
            space_indices = [i for i, value in enumerate(translation) if value == ' ']
            find_nearest_index = lambda value,list : min(list, key = lambda x:abs(x - value))
            nearest_index = find_nearest_index(TRANSLATION_CHARS_LIMIT, space_indices)
            translation = translation[:nearest_index] + '\n' + translation[nearest_index + 1:]
        else:
            self.answered.setStyleSheet('QPushButton { font-size: 11pt; }')
        
        self.answered.setText(translation)
    
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
#                self.pauseAction.setShortcut('U')
                self.trayIcon.setToolTip('Quiz paused!')
                
                self.trayIcon.setIcon(QIcon(PATH_TO_RES + TRAY + 'inactive.png'))
                self.trayUpdater.cancel()
                self.pauseAction.setIcon(QIcon(PATH_TO_RES + TRAY + START_ICON))
                self.stats.pauseStarted()
                
                self.updater.mayUpdate = True
                
            elif self.pauseAction.text() == '&Start quiz!':
                self.waitUntilNextTimeslot()
                self.pauseAction.setText('&Pause')
#                self.pauseAction.setShortcut('P')
                self.trayIcon.setToolTip('Quiz in progress!')
                
                self.trayIcon.setIcon(QIcon(PATH_TO_RES + TRAY + 'active.png'))
                self.pauseAction.setIcon(QIcon(PATH_TO_RES + TRAY + PAUSE_ICON))
            else:
                self.waitUntilNextTimeslot()
                self.pauseAction.setText('&Pause')
#                self.pauseAction.setShortcut('P')
                self.trayIcon.setToolTip('Quiz in progress!')
                
                self.trayIcon.setIcon(QIcon(PATH_TO_RES + TRAY + 'active.png'))
                self.pauseAction.setIcon(QIcon(PATH_TO_RES + TRAY + PAUSE_ICON))
                self.stats.pauseEnded()
                
                self.updater.mayUpdate = False
        else:
            self.showSessionMessage(u'Sorry, cannot pause while quiz in progress!')
 
    def showQuiz(self):
        if self.isHidden():
            self.updateContent()
            self.setButtonsActions()
            
            #self.restoreGeometry(self.gem)
            self.trayIcon.setIcon(QIcon(PATH_TO_RES + TRAY + 'active.png'))
            
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
        self.statistics.show()
        
    def showToolsDialog(self):
        self.tools.show()
        
    def showQuickLoad(self):
        self.qload.show()
        
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
        if self.status.achievements.achieved is not None:
            self.status.info.setText(self.status.achievements.achieved[1] + '\t( ' + self.status.achievements.achieved[0] + ' )')
            self.status.progress.hide()
            self.status.move(self.status.x(), self.status.y() - 15)
            self.status.info.show()
#            self.status.setMask(roundCorners(self.status.rect(),5))
        else:
            self.status.info.setText(u'')
            self.status.info.hide()
            self.status.restoreGeometry(self.status.gem)
#            self.status.setMask(roundCorners(self.status.rect(),5))
#        print self.status.y()
        self.status.adjustSize()
        self.status.show()
 
    def saveAndExit(self):
        self.hide()
        self.status.hide()
        self.allInfo.hide()
        self.kanjiInfo.hide()
        
        self.trayIcon.showMessage('Shutting down...', 'Saving session', QSystemTrayIcon.MessageIcon.Information, 20000 )
        
        if self.countdownTimer.isActive():
                self.countdownTimer.stop()
        if self.nextQuizTimer.isActive():
                self.nextQuizTimer.stop()
        if self.progressTimer != () and self.progressTimer.isAlive():
                self.progressTimer.cancel()
        if self.trayUpdater is not None and self.trayUpdater.isAlive() :
                self.trayUpdater.cancel()    
            
        self.rehash.checkSessionResults()
        
        self.srs.endCurrentSession(self.stats)
        self.trayIcon.hide()

        self.hooker.stop()

        self.updater.stop()
        self.optionsDialog.close()
        self.about.close()
        self.qdict.close()
        self.close()        
        
    def addReferences(self, about, options, qdict, updater, tools, statistics, web, rehash):
        self.about = about
        self.optionsDialog = options
        self.qdict = qdict
        self.updater = updater
        self.tools = tools
        self.statistics = statistics
        self.status.web = web
        self.rehash = rehash
        
    def initGlobalHotkeys(self):
        def toggleWidgetFlag(): self.qdict.showQDict = True
        self.hooker = GlobalHotkeyManager(toggleWidgetFlag , 'Q')
        self.hooker.setDaemon(True)
        self.hooker.start()
        
    def showEvent(self, event):
        self.restoreGeometry(self.gem)
