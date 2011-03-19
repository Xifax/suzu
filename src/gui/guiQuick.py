# -*- coding: utf-8 -*-
'''
Created on Feb 27, 2011

@author: Yadavito
'''

# own #
from settings.constants import Q_HEIGTH, Q_WIDTH, Q_INDENT, Q_VINDENT, Q_SPACE
from settings.fonts import Fonts

# external #
from PySide.QtCore import *
from PySide.QtGui import *
from uromkan import romkan, normalize_double_n
from cjktools import scripts
from jcconv import hira2kata


class QuickDictionary(QFrame):
    
    def __init__(self, qdict, edict, kdict, db, options, parent=None):
        super(QuickDictionary, self).__init__(parent)
        #handlers
        self.qdict = qdict
        self.edict = edict
        self.kdict = kdict
        self.db = db
        self.options = options
        
        # items info & menu
        self.itemsMenu = QFrame()
        self.itemsMenu.layout = QVBoxLayout()
        self.itemsMenu.wordInfo = QLabel(u'')
        self.itemsMenu.kanjiInfo = QLabel(u'')
        self.itemsMenu.fixSize = QCommandLinkButton('Mantain current size')
        self.itemsMenu.fixSize.setCheckable(True)

        self.itemsMenu.buttonsLayout = QHBoxLayout()
        #=======================================================================
        # self.itemsMenu.addWordToStudying = QPushButton('Add word')
        # self.itemsMenu.addAllWordsToStudying = QPushButton('Add all words')
        # self.itemsMenu.addAllKanjiToStudying = QPushButton('Add kanji in words')
        #=======================================================================
        
#        self.itemsMenu.addWordToStudying = QCommandLinkButton('Word')
#        self.itemsMenu.addAllWordsToStudying = QCommandLinkButton('Selected')
#        self.itemsMenu.addAllKanjiToStudying = QCommandLinkButton('Kanji')
        
        self.itemsMenu.addWordToStudying = QPushButton('Word')
        self.itemsMenu.addAllWordsToStudying = QPushButton('Selection')
        self.itemsMenu.addAllKanjiToStudying = QPushButton('Kanji')
        self.itemsMenu.addEverything = QPushButton('All')
        
        self.itemsMenu.buttonsLayout.addWidget(self.itemsMenu.addWordToStudying)
        self.itemsMenu.buttonsLayout.addWidget(self.itemsMenu.addAllWordsToStudying)
        self.itemsMenu.buttonsLayout.addWidget(self.itemsMenu.addAllKanjiToStudying)
        self.itemsMenu.buttonsLayout.addWidget(self.itemsMenu.addEverything)
        
        self.itemsMenu.layout.addWidget(self.itemsMenu.wordInfo)
        self.itemsMenu.layout.addWidget(self.itemsMenu.kanjiInfo)
        
#        self.itemsMenu.layout.addWidget(self.itemsMenu.addWordToStudying)
#        self.itemsMenu.layout.addWidget(self.itemsMenu.addAllWordsToStudying)
#        self.itemsMenu.layout.addWidget(self.itemsMenu.addAllKanjiToStudying)

        separator = QFrame();   separator.setFrameShape(QFrame.HLine);    separator.setFrameShadow(QFrame.Sunken)
        self.itemsMenu.layout.addWidget(separator)
        self.itemsMenu.layout.addLayout(self.itemsMenu.buttonsLayout)
        self.itemsMenu.layout.addWidget(self.itemsMenu.fixSize)
        
        self.itemsMenu.setLayout(self.itemsMenu.layout)
        
        # qdict gui components
        self.lookup = QLineEdit()
        self.checkLoose = QPushButton('%')
        self.switchPreOrPost = QPushButton('+..')
                
        self.switchPreOrPost.setDisabled(True)
        self.checkLoose.setCheckable(True)
        self.switchPreOrPost.setCheckable(True)
        
        self.comboDictionary = QComboBox()
        self.comboDictionary.addItems(['edict', 'jmdict'])
        self.comboLang = QComboBox()
        self.comboLang.addItems(['eng', 'rus'])
        self.checkInline = QPushButton('inline')        #every sense on new string or inline
        self.checkInline.setCheckable(True)
      
        self.itemsLimit = QDial()
                
        self.lookupLayout = QHBoxLayout()
        self.lookupLayout.addWidget(self.checkLoose)
        self.lookupLayout.addWidget(self.switchPreOrPost)
        self.lookupLayout.addWidget(self.lookup)
        self.lookupLayout.addWidget(self.itemsLimit)
        self.lookupLayout.addWidget(self.checkInline)        
        self.lookupLayout.addWidget(self.comboDictionary)
        self.lookupLayout.addWidget(self.comboLang)
        
        if not self.options.isPlastique():
            self.sizeGrip = QSizeGrip(self)
        
        self.lookupResults = QTableWidget()
        self.lookupResults.setColumnCount(4)
        self.lookupResults.setHorizontalHeaderLabels(['db', 'word', 'kana', 'senses'])
        
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.lookupLayout)
        self.layout.addWidget(self.lookupResults)

        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)
        
        '''Flag for global shortcut thread'''
        self.showQDict = False
        self.timerShowCheck = QTimer()
        self.timerShowCheck.timeout.connect(self.checkShortcut)

        QShortcut(QKeySequence("Escape"), self, self.closeAndWait )
        
        self.initializeComposition()
        self.initializeComponents()
        self.initializeActions()
        
        '''Start'''
        self.timerShowCheck.start(200)
        
        self.updateDictionarySwitch()
    
    def initializeComposition(self):
        
        #self.setWindowFlags(Qt.WindowStaysOnTopHint |  Qt.MSWindowsFixedSizeDialogHint | Qt.Tool )
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint )
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
        #self.setStyleSheet("QWidget { background-color: rgb(255, 255, 255); }")
        
        desktop = QApplication.desktop().screenGeometry()
        self.move(desktop.width() - Q_WIDTH - 15, desktop.height() - Q_HEIGTH - 10)
        
        self.setMinimumWidth(Q_WIDTH)
        #self.setMinimumHeight(Q_HEIGTH)
        
        self.itemsMenu.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint )
        self.itemsMenu.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        #self.itemsMenu.setStyleSheet("QWidget { background-color: rgb(255, 255, 255); }")
        
        self.itemsMenu.setGeometry(QRect(desktop.width() - self.width() - Q_INDENT - Q_SPACE, desktop.height() - self.height() - Q_VINDENT, Q_INDENT, self.height()))
        
    def initializeComponents(self):
        self.setFont(QFont('Calibri', 13))
        #self.lookupResults.setFont(QFont(Fonts.SazanamiMyoutyou, 14))
        
        self.lookup.setFont(QFont(Fonts.TukusiMyoutyouProLB, 14))
        #self.setStyleSheet('QWidget { font-size: 12pt; }')
        
        
        self.lookup.setMaximumHeight(30)
        self.itemsLimit.setMaximumSize(QSize(30,30))

        self.comboDictionary.setCurrentIndex(self.comboDictionary.findText(self.options.getLookupDict()))
        self.comboLang.setCurrentIndex(self.comboLang.findText(self.options.getLookupLang()))
        
        self.itemsLimit.setRange(1, 500)
        self.itemsLimit.setValue(100)
        
        # items menu/info
        #self.itemsMenu.layout.setAlignment(Qt.AlignCenter)
        self.itemsMenu.wordInfo.setAlignment(Qt.AlignCenter)
        self.itemsMenu.kanjiInfo.setAlignment(Qt.AlignCenter)
        
        self.itemsMenu.wordInfo.setFont(QFont(Fonts.HiragiNoMarugotoProW4, 36))
        self.itemsMenu.kanjiInfo.setFont(QFont(Fonts.MSMyoutyou, 14))
        self.itemsMenu.kanjiInfo.setWordWrap(True)
        
#        self.itemsMenu.addWordToStudying.setMaximumWidth(120)
#        self.itemsMenu.addWordToStudying.setMaximumHeight(35)
#        self.itemsMenu.addAllWordsToStudying.setMaximumWidth(120)
#        self.itemsMenu.addAllWordsToStudying.setMaximumHeight(35)
#        self.itemsMenu.addAllKanjiToStudying.setMaximumWidth(120)
#        self.itemsMenu.addAllKanjiToStudying.setMaximumHeight(35)
        
        self.itemsMenu.fixSize.setMaximumHeight(40)
        
        self.itemsMenu.wordInfo.setStyleSheet('QLabel { background-color: rgb(255, 255, 255); border: 1px solid black; }')
        self.itemsMenu.kanjiInfo.setStyleSheet('QLabel { background-color: rgb(255, 255, 255); border: 1px solid black; }')
        
    def initializeActions(self):
                
        self.comboDictionary.currentIndexChanged.connect(self.updateDictionarySwitch)
        self.checkLoose.toggled.connect(self.updateLooseCheck)
        self.switchPreOrPost.toggled.connect(self.updateSwitch)
        self.checkInline.toggled.connect(self.updateInlineCheck)
        
        self.lookup.textChanged.connect(self.convertToKana)
        self.lookup.returnPressed.connect(self.clearInput)

        self.lookupResults.itemSelectionChanged.connect(self.showItemMenu)
        self.lookupResults.doubleClicked.connect(self.resultsClicked)
        
        #self.itemsLimit.valueChanged.connect(self.updateLimit)
        self.itemsLimit.sliderReleased.connect(self.updateLimit)
        
        self.itemsMenu.addWordToStudying.clicked.connect(self.addWordToStudy)
        self.itemsMenu.addAllWordsToStudying.clicked.connect(self.addSelectionToStudy)
        self.itemsMenu.addAllKanjiToStudying.clicked.connect(self.addKanjiToStudy)
        self.itemsMenu.addEverything.clicked.connect(self.addAllToStudy)

    def resizeEvent(self, event):
        self.updateItemMenuSize()
        
    def updateItemMenuSize(self):
        if not self.itemsMenu.fixSize.isChecked():
            desktop = QApplication.desktop().screenGeometry()
            self.itemsMenu.setGeometry(QRect(desktop.width() - self.width() - Q_INDENT - Q_SPACE, desktop.height() - self.height() - Q_VINDENT + 6, Q_INDENT - 2, self.height()))
        
    def resultsClicked(self):
        self.lookupResults.clearSelection()
    
    def showItemMenu(self):
        if len(self.lookupResults.selectedIndexes()) > 0:
        
            self.itemsMenu.wordInfo.setText(self.lookupResults.item(self.lookupResults.currentItem().row(), 1).text())
            
            self.itemsMenu.kanjiInfo.setText(self.parseWordToKanji())
            
            self.itemsMenu.show()
            #if not self.itemsMenu.fixSize.isChecked():
            self.updateItemMenuSize()
                
        else:
            self.itemsMenu.wordInfo.setText(u'')
            self.itemsMenu.hide()

    def parseWordToKanji(self):

        script = scripts.script_boundaries(self.itemsMenu.wordInfo.text())
        components = u''
        kanjiList = []

        for cluster in script:
            if scripts.script_type(cluster) == scripts.Script.Kanji:
                for kanji in cluster:
                    if not kanji in kanjiList:
                        kanjiList.append(kanji)
                        try: 
                            lookup = self.kdict[kanji]
                            kun = lookup.kun_readings; on = lookup.on_readings; gloss = lookup.gloss
                            
                            components += '<b>(' + kanji + ')</b>\t'
                            
                            if len(kun) > 0:
                                components += '<b>kun:</b>' + ', '.join(kun) + '\t'
                            if len(on) > 0:
                                components += '<b>on:</b>' + ', '.join(on) + '<br/>'
                            if len(gloss) > 0:
                                components += "<font style='font-family: Calibri; font-size: 11pt'>" + ", ".join(gloss) + "</font><br/>"
                                
                        except:
                            components += kanji + '<br/>'
                        
        return components.rstrip('<br/>')
    
    def addWordToStudy(self):
        self.db.addWordToDbByValue(self.itemsMenu.wordInfo.text())
    
    def addSelectionToStudy(self):
        for item in self.lookupResults.selectedItems():
            if item.column() == 1:
                self.db.addWordToDbByValue(item.text())
    
    def addKanjiToStudy(self):
        script = scripts.script_boundaries(self.itemsMenu.wordInfo.text())
        for cluster in script:
            if scripts.script_type(cluster) == scripts.Script.Kanji:
                for kanji in cluster:
                    self.db.addKanjiToDb(kanji)
    
    def addAllToStudy(self):
        pass

    def convertToKana(self):
        
        inputLen = len(self.lookup.text())
        if inputLen > 0:
            
            if scripts.script_type(self.lookup.text()) == scripts.Script.Kanji:
                pass    #TODO: ...
            #if re.search('n{1}', self.lookup.text()[ inputLen - 2: ]) is None:                            #NB: yes, regexp would be better, yet I failed miserably at it
            if self.lookup.text()[ inputLen - 1 ] != u'n' and self.lookup.text()[ inputLen - 2:] != u'ny':
                converted = romkan(self.lookup.text())      #NB: does not convert naninuneno, somehow (purpotedly, 'n' normalization is to blame)
                self.lookup.setText(converted)
                #self.testConvert.setText(converted)
            if self.lookup.text()[ inputLen - 2:] == u'nn':
                converted = romkan(normalize_double_n(self.lookup.text()))
                self.lookup.setText(converted)
                
            #print self.lookup.text()
            #scripts.script_type(cluster) == scripts.Script.Kanji:
            
            if len(scripts.script_boundaries(self.lookup.text())) == 1:
                if scripts.script_type(self.lookup.text()) == scripts.Script.Hiragana:
                    self.updateLookupResults(self.lookup.text())
        else:
            self.lookupResults.clearContents()
            self.lookupResults.setRowCount(0)

    def clearInput(self):
        self.lookup.setText(u'')
        
    def checkShortcut(self):
        if self.showQDict: 
            self.show()
            #QApplication.focusWidget(self)
            #QApplication.setActiveWindow(self)
            #self.setFocus()
            self.lookup.setFocus()
            self.timerShowCheck.stop()
        elif not self.showQDict:
            if self.isVisible():    self.hide()
            #if not self.timerShowCheck.isActive():  self.timerShowCheck.start(200)
            
    def closeAndWait(self):
        self.showQDict = False;
        self.hide()
        self.itemsMenu.hide()
        #if self.isVisible():
        if not self.timerShowCheck.isActive():  self.timerShowCheck.start(200)
        
    def updateLookupResults(self, query):
        self.lookupResults.clearContents()
        self.lookupResults.setRowCount(0)

        results = []
                
        if self.comboDictionary.currentText() == 'edict':
            lookup = self.qdict.lookupItemByReading(query)
            for item in lookup:
                try:
                    results.append(self.edict[item])
                except:
                    pass
        elif self.comboDictionary.currentText() == 'jmdict':
            if self.checkLoose.isChecked():
                if not self.switchPreOrPost.isChecked():
                    results = list(self.qdict.dictionaryR[query + '.*'])        

                    if len(results) == 0: 
                        results = list(self.qdict.dictionaryR[hira2kata(query)])
                        
                    #results = self.qdict.looseLookupByReadingJoin(query, self.switchPreOrPost.isChecked(), not self.switchPreOrPost.isChecked())[:limit]
                else:
                    results = list(self.qdict.dictionaryR[u'.*' + query + '$'])
                    
                    if len(results) == 0: 
                        results = list(self.qdict.dictionaryR[hira2kata(query)])
            else:
                results = list(self.qdict.dictionaryR[query + u'$'])
                
                if len(results) == 0: 
                    results = list(self.qdict.dictionaryR[hira2kata(query)])

                #results = self.qdict.lookupItemByReading(query)
                #results = self.qdict.lookupTranslationByReadingJoin(query)  #TODO: add language chooser
                #results = self.qdict.lookupAllByReading(query)
                                       
        i = 0
        
        if self.comboDictionary.currentText() == 'jmdict':
                if not self.checkInline.isChecked():
                    for item in results:
                        for key in item:
                            if key != 'kana':
                                self.lookupResults.insertRow(i)
                                
                                self.lookupResults.setItem(i, 0, QTableWidgetItem(u'ｘ'))
#                                self.lookupResults.setItem(i, 1, QTableWidgetItem(key))
                                #self.lookupResults.setItem(i, 2, QTableWidgetItem(item['kana']))
                                #self.lookupResults.setItem(i, 3, QTableWidgetItem(', '.join(item[key])))
                                
                                word = QTableWidgetItem(key); word.setFont(QFont(Fonts.TukusiMyoutyouProLB, 18))
                                self.lookupResults.setItem(i, 1, word)
                                
                                kana = QTableWidgetItem(item['kana']); kana.setFont(QFont(Fonts.TukusiMyoutyouProLB, 14))
                                self.lookupResults.setItem(i, 2, kana)
                                
                                senses = QTableWidgetItem(', '.join(item[key])); senses.setFont(QFont('Calibri', 11))
                                self.lookupResults.setItem(i, 3, senses)
                                
                                    
                                i = i + 1
                        if i > self.itemsLimit.value() : break
                else:
                    for item in results:
                        for key in item:
                            if key != 'kana':
                                for sense in item[key]:
                                    self.lookupResults.insertRow(i)
                                    
                                    self.lookupResults.setItem(i, 0, QTableWidgetItem(u'ｘ'))
                                    #self.lookupResults.setItem(i, 1, QTableWidgetItem(key))
                                    #self.lookupResults.setItem(i, 2, QTableWidgetItem(item['kana']))
                                    #self.lookupResults.setItem(i, 3, QTableWidgetItem(sense))
                                    
                                    word = QTableWidgetItem(key); word.setFont(QFont(Fonts.TukusiMyoutyouProLB, 18))
                                    self.lookupResults.setItem(i, 1, word)
                                    
                                    kana = QTableWidgetItem(item['kana']); kana.setFont(QFont(Fonts.TukusiMyoutyouProLB, 14))
                                    self.lookupResults.setItem(i, 2, kana)
                                    
                                    senses = QTableWidgetItem(sense); senses.setFont(QFont('Calibri', 11))
                                    self.lookupResults.setItem(i, 3, senses)
                            
                                i = i + 1
                        if i > self.itemsLimit.value() : break
        
        elif self.comboDictionary.currentText() == 'edict':
            for item in results:
                self.lookupResults.insertRow(i)
            
                self.lookupResults.setItem(i, 1, QTableWidgetItem(item.word))
                #self.lookupResults.setItem(i, 2, QTableWidgetItem(query))
                self.lookupResults.setItem(i, 3, QTableWidgetItem(', '.join(item.senses)))

                i = i + 1
                
#                self.lookupResults.setItem(i, 1, QTableWidgetItem(item['word']))
#                self.lookupResults.setItem(i, 2, QTableWidgetItem(item['kana']))
#                #self.lookupResults.setItem(i, 3, QTableWidgetItem(', '.join(item['sense'])))
#                self.lookupResults.setItem(i, 3, QTableWidgetItem(item['sense']))
                
        self.lookupResults.resizeColumnsToContents()
        self.lookupResults.resizeRowsToContents()
        
    def updateSwitch(self):
        if self.switchPreOrPost.isChecked():
            self.switchPreOrPost.setText('...+')
        else:
            self.switchPreOrPost.setText('+...')

        if self.lookup.text() != u'':   self.updateLookupResults(self.lookup.text())
        
    def updateDictionarySwitch(self):
        if self.comboDictionary.currentText() == 'edict':
            self.checkLoose.setDisabled(True)
        elif self.comboDictionary.currentText() == 'jmdict':
            self.checkLoose.setEnabled(True)
        
    def updateLooseCheck(self):
        if self.checkLoose.isChecked():
            self.switchPreOrPost.setEnabled(True)
        else:
            self.switchPreOrPost.setDisabled(True)
            
        if self.lookup.text() != u'':   self.updateLookupResults(self.lookup.text())
        
    def updateInlineCheck(self):
        if self.lookup.text() != u'':   self.updateLookupResults(self.lookup.text())
        
    def updateLimit(self):
        if self.lookup.text() != u'':   self.updateLookupResults(self.lookup.text())

#app = QApplication(sys.argv)
##app.setStyle('plastique')
#
##stubs
#srsStub = ()
##from db import DictionaryLookup
#from db import *
#qdict = DictionaryLookup()
##qdict.loadJmdictFromDumpRegex() #for test purposes
#'''
#test = qdict.lookupItemByReading(u'いやいや')
#test = qdict.looseLookupByReading(u'いやいや')
#test = qdict.looseLookupByReadingJoin(u'か')
#'''
#from pkg_resources import resource_filename #por qua thou err like t'ese?
#from cjktools.resources import auto_format
#from cjktools.resources import kanjidic
#
#from optionsBackend import Options
#
#options = Options()
#
#edict_file = resource_filename('cjktools_data', 'dict/je_edict')
#edict = auto_format.load_dictionary(edict_file)
#
#kdict = kanjidic.Kanjidic()
#
#from srsManager import srsScheduler
#
#srs = srsScheduler()
#srs.initializeCurrentSession('kanji', 300)
#
#qd = QuickDictionary(qdict, edict, kdict, srs.db, options)
#qd.showQDict = True
#qd.show()
#
#sys.exit(app.exec_())
