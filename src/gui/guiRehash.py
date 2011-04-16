# -*- coding: utf-8 -*-
'''
Created on Apr 13, 2011

@author: Yadavito
'''

# internal #
#from itertools import combinations

# external #
from PySide.QtCore import *
from PySide.QtGui import *
from uromkan import romkan, normalize_double_n
from jcconv import kata2hira

# own #
from gui.guiUtil import clickable
from jdict.db import DBoMagic
from settings.constants import *
from settings.fonts import Fonts
from mParser.mecabTool import MecabTool
from utilities.log import log
#from utilities.utils import findCommonSubstring

class Filter(QObject):
    def eventFilter(self, object, event):
        
        def setBackgroundColor(object):
            background = u'background-color:'
            
            if object.parent().result: background += ' green;'
            else: background += ' red;'
            
            return background
            
        if event.type() == QEvent.HoverEnter:
            object.setStyleSheet('QLabel { border: 2px solid white; border-radius: 4px; color: white; ' + setBackgroundColor(object) + ' }')
            object.setText(object.text() + ' Next item...')
            object.parent().centerWidget()
        if event.type() == QEvent.HoverLeave:
            object.setStyleSheet('QLabel { color: black; border-radius: 4px; ' + setBackgroundColor(object)  + ' }')
            object.setText(object.text().split(' ')[0])
            object.parent().centerWidget()
        
        return False

class QuizRehash(QDialog):
    def __init__(self, db, kjd, edict, parent=None):
        super(QuizRehash, self).__init__(parent)
        
        self.db = db
        self.kjd = kjd
        self.edict = edict
        
        self.info = QLabel('Would you like to review problematic items?')
        self.yes = QPushButton('Okay')
        self.no = QPushButton('Let me go!')
        
        self.kanji = QLabel(u'')
        self.compounds = QLabel(u'')
        self.reading = QLineEdit(u'')
        self.mark = QLabel(u'')
        self.summary = QLabel(u'')
        
        self.layout = QGridLayout()
        self.layout.addWidget(self.info, 0, 0, 1, 2)
        self.layout.addWidget(self.yes, 1, 0)
        self.layout.addWidget(self.no, 1, 1)
        
        self.layout.addWidget(self.kanji, 2, 0, 2, 1)
        self.layout.addWidget(self.compounds, 2, 1, 2, 1)
        self.layout.addWidget(self.reading, 4, 0, 1, 2)
        self.layout.addWidget(self.mark, 5, 0, 1, 2)
        self.layout.addWidget(self.summary, 6, 0, 1, 2)
        
        self.setLayout(self.layout)
        
        self.initComposition()
        self.initComponents()
        self.initActions()
        
    def initComposition(self):
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.setWindowTitle('Quiz rehash')
        
    def initComponents(self):
        self.kanji.hide()
        self.compounds.hide()
        self.reading.hide()
        self.mark.hide()
        self.summary.hide()
        
        self.kanji.setStyleSheet('QLabel { background-color: white; border: 1px solid gray; }')
        self.kanji.setFont(QFont(Fonts.TukusiMyoutyouProLB, 36))
        self.kanji.setAlignment(Qt.AlignCenter)
        
        self.compounds.setStyleSheet('QLabel { background-color: white; border: 1px solid gray; }')
        self.compounds.setFont(QFont(Fonts.MSMyoutyou, 16.5))
        self.compounds.setWordWrap(True)
        self.compounds.setAlignment(Qt.AlignCenter)
        
        self.reading.setFont(QFont(Fonts.TukusiMyoutyouProLB, 13))
        self.reading.setAlignment(Qt.AlignCenter)
        
        self.mark.setAttribute(Qt.WA_Hover, True)
        self.mark.setAlignment(Qt.AlignCenter)
        self.mark.setFont(QFont(Fonts.MSMyoutyou, 13))
        
        self.summary.setAlignment(Qt.AlignCenter)
        self.summary.setFont(QFont('Calibri', 13))
    
    def initActions(self):
        self.no.clicked.connect(self.endRehash)
        self.yes.clicked.connect(self.beginRehash)
        
        self.reading.returnPressed.connect(self.checkAnswer)
        self.reading.textChanged.connect(self.convertToKana)
        
        clickable(self.mark).connect(self.continueReview)
        self.filter = Filter(self)
        self.mark.installEventFilter(self.filter)
        
        clickable(self.summary).connect(self.endRehash)
        
    #-------------- actions -------------#
    
    def parseReadings(self):
        items_grouped = {}
        for kanji in self.items:
            readings = {}
            try:
                lookup = self.kjd[kanji.character]
                for kun in lookup.kun_readings:
                    kun = kun.replace('.', '').replace('-', '')
                    for word in kanji.word:
                        if kun in kata2hira(MecabTool.parseToReadingsKana(word.word)[0]):
                            if readings.has_key(kun):
                                readings[kun].append(word.word)
                            else:
                                readings[kun] = [word.word]
                for on in lookup.on_readings:
                    on = kata2hira(on.replace('.', '').replace('-', ''))
                    for word in kanji.word:
                        if on in kata2hira(MecabTool.parseToReadingsKana(word.word)[0]):
                            if readings.has_key(on):
                                readings[on].append(word.word)
                            else:
                                readings[on] = [word.word]
            except Exception, e:
                log.error(e)
                
            # simple solution - difficult implementation
#            items_grouped[kanji.character] = readings
            # slightly more complicated solution - easier implementation
            for reading in readings:
                i = 0
                if items_grouped.has_key(kanji.character): items_grouped[kanji.character + '_' + str(i)] = (reading, readings[reading]); i += 1
                else: items_grouped[kanji.character] = (reading, readings[reading])
            
#        return items_grouped
        self.items = items_grouped
            
            
#            for word in kanji.word:
#                print word.word
#                try:
##                    lookup = self.edict[word.word]
# 
#                        
#                    
#                    readings.append(kata2hira(MecabTool.parseToReadingsKana(word.word)[0]))
#                except Exception, e:
#                    log.error(e)
#            variants = []
##            for combination in combinations(readings, len(readings)):
#            for combination in combinations(readings, len(readings) - 1):
#                if len(readings) == 1:
#                    variants.append(readings[0])
#                else:
#                    variants.append(findCommonSubstring(combination))
#            print ' '.join(variants)
    
    def checkSessionResults(self):
        self.items = self.db.getProblematicItems()
        if self.items is not None:
            self.parseReadings()
            self.items_iterator = iter(self.items)
            self.items_to_delete = []
            self.exec_()
            
    def endRehash(self):
        self.done(0)
        
    def beginRehash(self):
        self.yes.hide()
        self.no.hide()
        self.info.hide()
        
        self.kanji.show()
        self.compounds.show()
        self.reading.show()
        
        self.correct = 0
        self.wrong = 0
        
        self.continueReview()
        
    def convertToKana(self):
        inputLen = len(self.reading.text())
        if inputLen > 0:
            if self.reading.text()[ inputLen - 1 ] != u'n' and self.reading.text()[ inputLen - 2:] != u'ny':
                    converted = romkan(self.reading.text())
                    self.reading.setText(converted)
            if self.reading.text()[ inputLen - 2:] == u'nn':
                converted = romkan(normalize_double_n(self.reading.text()))
                self.reading.setText(converted)
        
    def checkAnswer(self):
        answer = self.reading.text()
        self.reading.setText(u'')
        
        if answer == self.items[self.current_item][0]:
            self.mark.setStyleSheet('QLabel { background-color: green; border-radius: 4px; }')
            self.mark.setText('Correct!')
            
            self.result = True
            self.correct += 1
            if self.items.has_key(self.current_item):
                self.items_to_delete.append(self.current_item)
                
            self.updateCompounds()
            
        else:
            self.mark.setStyleSheet('QLabel { background-color: red; border-radius: 4px; }')
            self.mark.setText('Wrong!(' + self.items[self.current_item][0] + ')')
            self.result = False
            self.wrong += 1
            
            self.updateCompounds()
            
        self.reading.hide()
        self.mark.show()
        
    def updateCompounds(self):
        compounds = u''
        for compound in self.items[self.current_item][1]:
            compounds += compound + u'\t～\t'
            try:
                lookup = self.edict[compound]
                compounds += lookup.readings[0] + '<br/>'
                compounds += "<i><font style='font-family: Calibri; font-size: 11pt'>" + ", ".join(lookup.senses).rstrip(",(P)") + "</font></i><br/>"
            except Exception, e:
                log.error(e)
        self.compounds.setText(compounds)
        self.adjustSize()
        self.centerWidget()
            
    def continueReview(self):
        self.mark.hide()
        self.reading.show()
        
        self.current_item = self.nextItem()
        if self.current_item is None:
            self.kanji.hide()
            self.compounds.hide()
            self.reading.hide()
            self.summary.show()
            self.summary.setText('Review complete!<br/>Correct: <b>' 
                                 + str(self.correct) + '</b>\t' 
                                 + 'Wrong: <b>' + str(self.wrong) + '</b><br/>'
                                 + 'Total: <b>' + str( self.wrong + self.correct )
                                 + '</b><br/>(click to quit)')
            self.adjustSize()
        else:
            if '_' in self.current_item: self.kanji.setText(self.current_item.split('_')[0])
            else: self.kanji.setText(self.current_item)
            compounds = u''
            for compound in self.items[self.current_item][1]:
                compounds += compound + '\t'
            self.compounds.setText(compounds)
        
    def nextItem(self):
        current_item = None
        try:
            current_item = self.items_iterator.next()
        except Exception, e:
            print e
            for key in self.items_to_delete: self.items.pop(key)
            self.items_iterator = iter(self.items)
            current_item = self.items_iterator.next()
        finally:
            return current_item
        
    def centerWidget(self):
        desktop = QApplication.desktop().screenGeometry()
        self.move((desktop.width() - self.width())/2, (desktop.height() - self.height())/2)
    