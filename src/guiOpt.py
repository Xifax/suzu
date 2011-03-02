# -*- coding: utf-8 -*-
'''
Created on Feb 16, 2011

@author: Yadavito
'''

import sys

from PySide.QtCore import *
from PySide.QtGui import *

from constants import *
from guiUtil import roundCorners
from rtimer import RepeatTimer

class StatusFilter(QObject):
    """Status message mouse click filter"""
    def eventFilter(self, object, event):
        
        if event.type() == QEvent.HoverEnter:
            object.status.setWindowOpacity(0.70)
            
        if event.type() == QEvent.HoverLeave:
            object.status.setWindowOpacity(1)
            
        if event.type() == QEvent.MouseButtonPress:
            object.status.hide()
            
        return False

class OptionsDialog(QFrame):
    
    def __init__(self, db, options, parent=None):
        super(OptionsDialog, self).__init__(parent)
        # db & options handlers
        self.db = db
        self.options = options
        self.dbItems = self.db.countTotalItemsInDb()
        
        # status info
        self.status = QFrame()
        self.status.info = QLabel(u'')
        self.status.layout = QHBoxLayout()
        self.status.layout.addWidget(self.status.info)
        self.status.setLayout(self.status.layout)
        
        ### runtime group ###
        self.appOptionsGroup = QGroupBox('Runtime')
        self.appOptionsGroup.setAlignment(Qt.AlignCenter)
        self.checkAutostart = QCheckBox('Begin quiz on application start')
        self.checkEnableLog = QCheckBox('Enable errors logging')
        self.checkEnableFade = QCheckBox('Enable fade effect')
        self.checkAlwaysOnTop = QCheckBox('Always on top')
        self.checkSoundSignal = QCheckBox('Announce quiz with sound')
        self.checkSplashScreen = QCheckBox('Splash screen on launch')
        self.checkGlobalHotkeys = QCheckBox('Enable global hotkeys')
        
        self.appLayout = QVBoxLayout()
        self.appLayout.addWidget(self.checkAutostart)
        self.appLayout.addWidget(self.checkSplashScreen)
        self.appLayout.addWidget(self.checkAlwaysOnTop)
        self.appLayout.addWidget(self.checkSoundSignal)
        self.appLayout.addWidget(self.checkEnableFade)
        self.appLayout.addWidget(self.checkEnableLog)
        self.appLayout.addWidget(self.checkGlobalHotkeys)
        
        self.appOptionsGroup.setLayout(self.appLayout)
        
        ### fonts group ###
        self.appFontsGroup = QGroupBox('Fonts')
        self.appFontsGroup.setAlignment(Qt.AlignCenter)
        self.sentenceFontLabel = QLabel(u'Sentence:')
        self.selectSentenceFont = QFontComboBox()
        self.quizFontLabel = QLabel(u'Quiz:')
        self.selectQuizFont = QFontComboBox()
        self.infoFontLabel = QLabel(u'Kanji info:')
        self.selectInfoFont = QFontComboBox()
        self.statusFontLabel = QLabel(u'Status message:')
        self.selectStatusFont = QFontComboBox()
        
        self.fontsLayout = QVBoxLayout()
        self.fontsLayout.addWidget(self.sentenceFontLabel)
        self.fontsLayout.addWidget(self.selectSentenceFont)
        self.fontsLayout.addWidget(self.quizFontLabel)
        self.fontsLayout.addWidget(self.selectQuizFont)
        self.fontsLayout.addWidget(self.infoFontLabel)
        self.fontsLayout.addWidget(self.selectInfoFont)
        self.fontsLayout.addWidget(self.statusFontLabel)
        self.fontsLayout.addWidget(self.selectStatusFont)      
        
        self.appFontsGroup.setLayout(self.fontsLayout)
        
        ### srs group ###
        self.srsGroup = QGroupBox('SRS Tweaks')
        self.srsGroup.setAlignment(Qt.AlignCenter)
        
        self.intervalLabel = QLabel(u'Interval between quizzes (minutes):')
        self.countdownlLabel = QLabel(u'Time for answer (seconds):')
        self.intervalSpin = QSpinBox()
        self.intervalDial = QDial()

        self.countdownSpin = QSpinBox()
        self.countdownDial = QDial()
        
        self.sessionItemsLabel = QLabel(u'Sample size:')
        self.sessionItemsLabel.setToolTip(u'Maximum number of unique items, selected for current session from active database.')
        self.sessionItemsSpin = QSpinBox()
        self.sessionLengthLabel = QLabel(u'Session limit:')
        self.sessionLengthLabel.setToolTip(u'Maximum allowed repetitions/day, including non-unique items.')
        self.sessionLengthSpin = QSpinBox()
        
        self.sessionModeLabel = QLabel(u'Quiz mode:')
        self.sessionModeCombo = QComboBox()
        
        self.srsLayout = QGridLayout()
        self.srsLayout.addWidget(self.intervalLabel, 0, 0, 1, 2)
        self.srsLayout.addWidget(self.intervalDial, 1, 0)
        self.srsLayout.addWidget(self.intervalSpin, 1, 1)
        self.srsLayout.addWidget(self.countdownlLabel, 2, 0, 1, 2)
        self.srsLayout.addWidget(self.countdownDial, 3, 0)
        self.srsLayout.addWidget(self.countdownSpin, 3, 1)
        self.srsLayout.addWidget(self.sessionItemsLabel, 4, 0)
        self.srsLayout.addWidget(self.sessionItemsSpin, 4, 1)
        self.srsLayout.addWidget(self.sessionLengthLabel, 5, 0)
        self.srsLayout.addWidget(self.sessionLengthSpin, 5, 1)
        self.srsLayout.addWidget(self.sessionModeLabel, 6, 0)
        self.srsLayout.addWidget(self.sessionModeCombo, 6, 1)
        
        self.srsGroup.setLayout(self.srsLayout)
        
        ### dictionary group ###
        self.dictGroup = QGroupBox('JMdict')
        self.dictGroup.setAlignment(Qt.AlignCenter)
        
        self.languageLabel = QLabel(u'Translation lookup in:')
        self.languageCombo = QComboBox()
        
        self.dictLayout = QGridLayout()
        self.dictLayout.addWidget(self.languageLabel, 0, 0)
        self.dictLayout.addWidget(self.languageCombo, 0, 1)
        
        self.dictGroup.setLayout(self.dictLayout)
        
        ### database group ###
        self.dbGroup = QGroupBox('Database')
        self.dbGroup.setAlignment(Qt.AlignCenter)
        
        self.totalLabel = QLabel(u'Kanji: <b>' + str(self.dbItems['kanji']) + '</b>\tWords: <b>' + str(self.dbItems['words']) + '</b><br />Total: <b>%s</b>' 
                                 % (self.dbItems['kanji'] + self.dbItems['words'])  )
        self.totalLabel.setWordWrap(True)
        #self.totalLabel.heightForWidth(True)
        self.viewAll = QToolButton()
        separator_one = QFrame();   separator_one.setFrameShape(QFrame.HLine);    separator_one.setFrameShadow(QFrame.Sunken)
        self.viewAll.setText(u'View all')
        self.addLabel = QLabel(u'Batch-add kanji to studying list:')
        self.comboTag = QComboBox()
        self.comboLevel = QComboBox()
        self.comboCompare = QComboBox()
        self.inputFrequency = QLineEdit()
        self.inputFrequency.setToolTip(u'Enter character frequency (from 1 to 6265)')
        self.addButton = QPushButton(u'Add items')
        #self.addButton.setGeometry(QRect(self.addButton.pos(), QSize(50,50)))
        
        self.tagsView = QTableWidget()
        self.tagsView.setColumnCount(4) #jlpt/grade level count active
        self.tagsView.setHorizontalHeaderLabels(['Grade', 'Level', 'Items', 'Active'])
        #self.tagsView.setRowCount(2)
        self.tagsView.setFixedSize(250,130)
        #item = QTableWidgetItem('test')
        #item.setFlags(item.flags() & Qt.ItemIsEditable)
        #item.setFlags(Qt.ItemIsEditable)
        #self.tagsView.setItem(0, 0, item)
        #self.tagsView.setItem(0, 1, QTableWidgetItem('lalala'))
        
        self.dbLayout = QGridLayout()
        self.dbLayout.addWidget(self.totalLabel, 0, 0, 1, 3)
        self.dbLayout.addWidget(self.viewAll, 0, 3, 1, 1)
        self.dbLayout.addWidget(separator_one, 1, 0, 1, 4)
        self.dbLayout.addWidget(self.addLabel, 2, 0, 1, 4)
        self.dbLayout.addWidget(self.comboTag, 3, 1)
        self.dbLayout.addWidget(self.comboLevel, 3, 2)
        self.dbLayout.addWidget(self.comboCompare, 4, 1)
        self.dbLayout.addWidget(self.inputFrequency, 4, 2)
        self.dbLayout.addWidget(self.addButton, 3, 3, 2, 1)

        self.dbLayout.addWidget(self.tagsView, 5, 0, 1, 4)
        
        self.dbGroup.setLayout(self.dbLayout)
                
        ### toolbox ###
        self.toolbox = QToolBox()
        self.toolbox.addItem(self.appOptionsGroup, 'Application')
        self.toolbox.addItem(self.appFontsGroup, 'Fonts')
        self.toolbox.addItem(self.srsGroup, 'Spaced Repetition System')
        self.toolbox.addItem(self.dictGroup, 'Dictionaries')
        self.toolbox.addItem(self.dbGroup, 'Studying items')
        
        ### main layout ###
        self.mainLayout = QVBoxLayout()

        self.bBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Reset | QDialogButtonBox.Close )#| QDialogButtonBox.Help)

        self.mainLayout.addWidget(self.toolbox)
        self.mainLayout.addWidget(self.bBox)
        
        self.setLayout(self.mainLayout)
        
        self.initializeComposition()
        self.initializeComponents()
        self.initializeActions()
        
        ### additional preparations ###
        self.updateComboLevel()
        self.updateDbTable()
        self.animationTimer = ()
    
    def initializeComposition(self):
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        desktop = QApplication.desktop().screenGeometry()

        self.setGeometry(QRect((desktop.width() - O_WIDTH)/2, (desktop.height() - O_HEIGHT)/2, O_WIDTH, O_HEIGHT))

        self.setStyleSheet("QWidget { background-color: rgb(255, 255, 255) }")
        
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum))
        self.setMask(roundCorners(self.rect(),5))
        
        self.status.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.status.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
        self.status.setGeometry((desktop.width() - O_WIDTH)/2, (desktop.height() + O_HEIGHT)/2 + OS_INDENT, O_WIDTH, OS_HEIGTH )
        self.status.setStyleSheet("QWidget { background-color: rgb(255, 255, 255) }")
        
        self.status.layout.setAlignment(Qt.AlignCenter)
        self.status.layout.setMargin(0)
        self.status.setMask(roundCorners(self.status.rect(),5))
    
    def initializeComponents(self):
        
        self.status.info.setFont(QFont('Cambria',self.options.getMessageFontSize()))

        self.appLayout.setAlignment(Qt.AlignCenter)
        self.mainLayout.setAlignment(Qt.AlignCenter)

        self.intervalDial.setNotchesVisible(True)
        self.intervalDial.setRange(1, 30)
        self.intervalDial.setSingleStep(1)
        
        self.intervalSpin.setRange(1,30)
        
        self.countdownDial.setNotchesVisible(True)
        self.countdownDial.setRange(5, 45)
        self.countdownDial.setSingleStep(1)
        
        self.countdownSpin.setRange(5,45)
        
        #TODO: set session length boundaries and values
        self.sessionItemsSpin.setRange(1, 99999)
        self.sessionLengthSpin.setRange(1, 99999)
        
        self.intervalDial.setValue(self.options.getRepetitionInterval())
        self.countdownDial.setValue(self.options.getCountdownInterval())
        
        self.sessionItemsSpin.setValue(self.options.getSessionSize())
        self.sessionLengthSpin.setValue(self.options.getSessionLength())
        
        self.checkAutostart.setChecked(self.options.isQuizStartingAtLaunch())
        self.checkSplashScreen.setChecked(self.options.isSplashEnabled())
        self.checkAlwaysOnTop.setChecked(self.options.isAlwaysOnTop())
        self.checkGlobalHotkeys.setChecked(self.options.isGlobalHotkeyOn())
        self.checkEnableLog.setChecked(self.options.isLoggingOn())
        self.checkEnableFade.setChecked(self.options.isFadeEffectOn())
        self.checkSoundSignal.setChecked(self.options.isSoundOn())
        
        self.sessionModeCombo.addItems(['kanji', 'compounds', 'all'])
        self.languageCombo.addItems(['eng','rus'])
        self.comboTag.addItems(['jlpt', 'grade'])
        self.comboCompare.addItems(['=', '>', '<', '>=', '<='])
        
        #self.status.installEventFilter(self.filter)
        
        #TODO: add control for maximum active items in db
        
        #self.intervalDial.setStyleSheet("QDial { background-color: rgb(255, 170, 0) ; }")
        
    def initializeActions(self):
        self.bBox.accepted.connect(self.saveOptions)
        self.bBox.rejected.connect(self.discardOptions)
        
        self.bBox.button(QDialogButtonBox.Reset).clicked.connect(self.resetOptions)
        
        self.intervalDial.valueChanged.connect(self.updateCountdown)
        self.intervalSpin.valueChanged.connect(self.updateInterval)
        
        self.countdownDial.valueChanged.connect(self.updateCountdownSpin)
        self.countdownSpin.valueChanged.connect(self.updateCountdownDial)
        
        self.comboTag.currentIndexChanged.connect(self.updateComboLevel)
    
    def saveOptions(self):
        """Saving all options"""
        ### flags ###
        self.options.setAlwaysOnTop(self.checkAlwaysOnTop.isChecked())
        self.options.setSplashEnabled(self.checkSplashScreen.isChecked())
        self.options.setQuizStartingAtLaunch(self.checkAutostart.isChecked())
        self.options.setSoundOn(self.checkSoundSignal.isChecked())
        self.options.setGlobalHotkeyOn(self.checkGlobalHotkeys.isChecked())
        self.options.setLoggingOn(self.checkEnableLog.isChecked())
        self.options.setFadeEffectOn(self.checkEnableFade.isChecked())
        ### session ###
        self.options.setRepetitionInterval(self.intervalDial.value())
        self.options.setCountdownInterval(self.countdownDial.value())
        self.options.setSessionSize(self.sessionItemsSpin.value())
        self.options.setSessionLength(self.sessionLengthSpin.value())
        
        self.showInfo(u'All options saved!')
    
    def resetOptions(self):
        print 'reset'
        
    def discardOptions(self):
        if self.status.isVisible(): self.status.hide()
        self.hide()
        
    def showInfo(self, message):
        self.status.info.setText(message)
        self.status.show()
        self.status.setWindowOpacity(0)
        self.fadeStatus()
        QTimer.singleShot(3000, self.fadeStatus)
    
    def updateCountdown(self):
        self.intervalSpin.setValue(self.intervalDial.value())
        self.update()
        
    def updateCountdownSpin(self):
        self.countdownSpin.setValue(self.countdownDial.value())
        self.update()
        
    def updateInterval(self):
        self.intervalDial.setValue(self.intervalSpin.value())
        self.update()
        
    def updateCountdownDial(self):
        self.countdownDial.setValue(self.countdownSpin.value())
        self.update()
        
    def updateComboLevel(self):
        if self.comboTag.currentText()=='jlpt':         #TODO: move to constants
            self.comboLevel.clear()
            self.comboLevel.addItems(['1','2','3','4'])
        elif self.comboTag.currentText()=='grade':
            self.comboLevel.clear()
            self.comboLevel.addItems(['1','2','3','4','5','6','7','8','9','10'])
            
    def updateDbTable(self):
        dbStats = self.db.countItemsByGrades()
        #self.tagsView.setRowCount(len(dbStats))
        i = 0
        for item in dbStats:
            if dbStats[item] != 0:
                self.tagsView.insertRow(i)
                grade = item[-1:];  level = u''
                if grade == 0: 
                    grade = 10; level = item[:-2]
                else:
                    level = item[:-1]
                
                self.tagsView.setItem(i, 0, QTableWidgetItem(level));   self.tagsView.itemAt(i, 0).setTextAlignment(Qt.AlignCenter)#;    self.tagsView.itemAt(i, 1).setFlags(Qt.ItemIsUserCheckable)
                self.tagsView.setItem(i, 1, QTableWidgetItem(str(grade)))#;  self.tagsView.itemAt(i, 1).setFlags(Qt.ItemIsUserCheckable) #;  self.tagsView.itemAt(i, 1).setTextAlignment(Qt.AlignCenter)
                self.tagsView.setItem(i, 2, QTableWidgetItem(str(dbStats[item])))#;  self.tagsView.itemAt(i, 2).setFlags(Qt.ItemIsUserCheckable)#;  self.tagsView.itemAt(i, 2).setTextAlignment(Qt.AlignCenter)   
                checkedItem = QTableWidgetItem();  checkedItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable); checkedItem.setCheckState(Qt.Checked)
                #checkedItem.setTextAlignment(Qt.AlignCenter)
                self.tagsView.setItem(i, 3, checkedItem)
                i = i + 1
        
        self.tagsView.resizeColumnsToContents()
        self.tagsView.resizeRowsToContents()
        
#------------------- Fading methods ---------------------#
    def fadeStatus(self):
        if self.status.windowOpacity() == 1:
            self.animationTimer = RepeatTimer(0.025, self.fadeOut, 40)
            self.animationTimer.start()
        else:
            self.animationTimer = RepeatTimer(0.025, self.fadeIn, 40)
            self.animationTimer.start()
    
    def fadeIn(self):
        self.status.setWindowOpacity(self.status.windowOpacity() + 0.1)
        
    def fadeOut(self):
        self.status.setWindowOpacity(self.status.windowOpacity() - 0.1)


app = QApplication(sys.argv)
app.setStyle('plastique')

from srsManager import srsScheduler
srsStub = srsScheduler()
srsStub.initializeCurrentSession('kanji', 300)
#srsStub = ()    #for testing purposes
#optionsStub = ()
from optionsBackend import Options
optionsStub = Options()
options = OptionsDialog(srsStub.db, optionsStub)
options.show()

sys.exit(app.exec_())

